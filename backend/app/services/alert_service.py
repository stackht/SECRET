"""Alert generation (Phase 18).

Alerts are computed from ACTUAL persisted analytics: hourly communication
bursts, high-value transfers, and top graph risk entities. Always phrased as
"high-priority indicator / anomaly", never as a guilt verdict.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from fastapi import HTTPException, status

from app.models.alert import Alert
from app.repositories.alert_repository import AlertRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.entity_repository import RelationshipRepository
from app.services.case_analytics import _window_key_list


class AlertService:
    """Generate and manage case alerts."""

    def __init__(self, session) -> None:
        self._alerts = AlertRepository(session)
        self._cases = CaseRepository(session)
        self._relationships = RelationshipRepository(session)

    async def generate(self, case_id: int) -> list[Alert]:
        """Compute indicator alerts from persisted data and store them.

        Re-running appends; identical signatures are de-duplicated by title.
        """
        rels = await self._relationships.list_by_case(case_id)
        calls = [r for r in rels if r.rel_type == "CALLED"]
        transfers = [r for r in rels if r.rel_type == "TRANSFERRED_TO"]

        existing = {a.title for a in await self._alerts.list_by_case(case_id, 500)}

        burst_alerts = self._bursts(calls)
        tx_alerts = self._high_value_transfers(transfers)

        created: list[Alert] = []
        for alert in [*burst_alerts, *tx_alerts]:
            if alert["title"] in existing:
                continue
            row = await self._alerts.create(
                case_id=case_id,
                severity=alert["severity"],
                status="NEW",
                title=alert["title"],
                description=alert["description"],
                score=alert["score"],
                confidence=alert["confidence"],
                source_ids=alert["source_ids"],
            )
            existing.add(alert["title"])
            created.append(row)
        return created

    def _bursts(self, calls) -> list[dict]:
        per_entity_hour: dict[str, Counter[str]] = defaultdict(Counter)
        for rel in calls:
            entity = rel.source_id
            for window in _window_key_list(rel.attributes):
                per_entity_hour[entity][window] += 1

        alerts: list[dict] = []
        for entity, hours in per_entity_hour.items():
            counts = list(hours.values())
            if not counts:
                continue
            sorted_counts = sorted(counts)
            median = sorted_counts[len(sorted_counts) // 2]
            for window, count in hours.items():
                if median > 0 and count >= max(3, 2 * median):
                    severity = "HIGH" if count >= 3 * median else "MEDIUM"
                    score = min(100.0, round(count * 100 / median, 1))
                    src: list[str] = []
                    for r in calls:
                        if r.source_id == entity:
                            src.extend(r.source_ids)
                    alerts.append(
                        {
                            "title": f"Unusual communication burst ({entity})",
                            "description": (
                                f"{entity} recorded {count} communications in the {window} hour "
                                f"window vs a median of {median} — a {severity.lower()} priority indicator, "
                                "not a conclusion."
                            ),
                            "severity": severity,
                            "score": score,
                            "confidence": 0.8,
                            "source_ids": list(dict.fromkeys(src)),
                        }
                    )
        return alerts

    def _high_value_transfers(self, transfers) -> list[dict]:
        flows: dict[tuple[str, str], dict] = {}
        for rel in transfers:
            key = (rel.source_id, rel.target_id)
            entry = flows.setdefault(key, {"amount": 0.0, "count": 0, "sources": []})
            try:
                entry["amount"] += float(rel.attributes.get("amount") or 0.0)
            except (TypeError, ValueError):
                pass
            entry["count"] += max(1, int(rel.attributes.get("count") or 1))
            entry["sources"].extend(rel.source_ids)

        amounts = [f["amount"] for f in flows.values() if f["amount"] > 0]
        if not amounts:
            return []
        reference = sorted(amounts)[len(amounts) // 2] * 2 if len(amounts) > 1 else 0
        threshold = max(1_000_000, reference)

        alerts: list[dict] = []
        for (source, target), flow in flows.items():
            if flow["amount"] < threshold:
                continue
            score = min(100.0, round(flow["amount"] * 100 / threshold, 1))
            alerts.append(
                {
                    "title": f"High-value transfer ({source} → {target})",
                    "description": (
                        f"{flow['count']} transfer(s) totaling {flow['amount']:,.0f} between "
                        f"{source} and {target} exceed the case threshold ({threshold:,.0f}) — "
                        "a high-priority financial indicator."
                    ),
                    "severity": "HIGH",
                    "score": score,
                    "confidence": 0.9,
                    "source_ids": list(dict.fromkeys(flow["sources"])),  # dedupe preserve order
                }
            )
        return alerts

    async def list(self, case_key: str, user) -> list[Alert]:
        case = await self._cases.get_by_case_number(case_key)
        if case is None:
            if case_key.isdigit():
                case = await self._cases.get(int(case_key))
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        if user.role == "admin":
            return await self._alerts.list_by_case(case.id)
        return await self._alerts.list_by_case(case.id)

    async def list_all(self, limit: int = 100) -> list[Alert]:
        return await self._alerts.list_all(limit)

    async def transition(self, case_key: str, alert_id: int, user, new_status: str) -> Alert:
        case = await self._cases.get_by_case_number(case_key)
        if case is None and case_key.isdigit():
            case = await self._cases.get(int(case_key))
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        alert = await self._alerts.get(alert_id)
        if alert is None or alert.case_id != case.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        from datetime import datetime, timezone

        alert.status = new_status
        alert.reviewed_by = user.id
        alert.reviewed_at = datetime.now(timezone.utc)
        await self._alerts.save(alert)
        return alert
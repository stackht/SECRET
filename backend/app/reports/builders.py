"""Report builders (Phase 9).

Each builder assembles report sections from live application state: the
relational DB (cases, profiles) and graph analytics (NetworkX over the store).
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseCriminal
from app.models.criminal import CriminalProfile
from app.schemas.report import ReportSection
from app.services.analytics_service import AnalyticsService


async def _case(session: AsyncSession, case_number: str) -> Case | None:
    result = await session.execute(select(Case).where(Case.case_number == case_number))
    return result.scalar_one_or_none()


async def _case_profiles(session: AsyncSession, case_id: int) -> list[CriminalProfile]:
    stmt = (
        select(CriminalProfile)
        .join(CaseCriminal, CaseCriminal.profile_id == CriminalProfile.id)
        .where(CaseCriminal.case_id == case_id)
        .order_by(CriminalProfile.id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


def _fmt_lines(mapping: dict) -> list[str]:
    return [f"{k}: {v}" for k, v in mapping.items()]


async def build_investigation_summary(
    session: AsyncSession,
    store,
    case_number: str,
    title: str,
) -> list[ReportSection]:
    case = await _case(session, case_number)
    sections: list[ReportSection] = []

    if case is None:
        return [
            ReportSection(
                heading="Investigation Summary",
                body=[f"No case found for {case_number}.", "Report reflects no associated records."],
            )
        ]

    profiles = await _case_profiles(session, case.id)
    sections.append(
        ReportSection(
            heading="Case Overview",
            body=_fmt_lines(
                {
                    "Case": case.case_number,
                    "Title": case.title,
                    "Status": case.status,
                    "Priority": case.priority,
                    "Created": case.created_at.isoformat(),
                    "Entities associated": len(profiles),
                }
            ),
        )
    )

    sections.append(
        ReportSection(
            heading="Associated Entities",
            body=[f"{p.secret_id}  {p.name}  ({p.profile_type}, risk {p.risk_score})" for p in profiles]
            or ["No entities associated."],
        )
    )

    analytics = AnalyticsService(store)
    try:
        communities = await analytics.communities()
        sections.append(
            ReportSection(
                heading="Network Structure",
                body=[
                    f"Communities detected: {communities.count}",
                    f"Network density: {communities.network_density}",
                    *[
                        f"Community #{c.community_id}: {c.size} entities"
                        for c in communities.communities[:8]
                    ],
                ],
            )
        )
    except Exception:  # noqa: BLE001 - analytics unavailable should not break a report
        sections.append(
            ReportSection(heading="Network Structure", body=["Analytics unavailable for this case."])
        )

    return sections


async def build_entity_intelligence(
    session: AsyncSession,
    store,
    entity_id: str,
    title: str,
) -> list[ReportSection]:
    result = await session.execute(select(CriminalProfile).where(CriminalProfile.secret_id == entity_id))
    profile = result.scalar_one_or_none()

    if profile is None:
        return [
            ReportSection(
                heading="Entity Intelligence",
                body=[f"No profile found for {entity_id}.", "Report reflects no associated records."],
            )
        ]

    sections = [
        ReportSection(
            heading="Entity Overview",
            body=_fmt_lines(
                {
                    "Entity": profile.secret_id,
                    "Name": profile.name,
                    "Type": profile.profile_type,
                    "Risk score": profile.risk_score,
                    "Risk level": profile.risk_level,
                    "Confidence": profile.confidence,
                    "Status": profile.status,
                    "Aliases": ", ".join(profile.aliases or []),
                }
            ),
        )
    ]

    analytics = AnalyticsService(store)
    try:
        graph = await analytics._graph()
        node = graph.nodes.get(entity_id)
        if node is not None:
            degree = graph.degree(entity_id)
            neighbors = [n for n in graph.neighbors(entity_id)][:12]
            sections.append(
                ReportSection(
                    heading="Network Connections",
                    body=[f"Degree: {degree}", *[f"- {n}" for n in neighbors]],
                )
            )
    except Exception:  # noqa: BLE001
        sections.append(ReportSection(heading="Network Connections", body=["Unavailable."]))

    return sections


async def build_network_analysis(
    session: AsyncSession,
    store,
    title: str,
) -> list[ReportSection]:
    analytics = AnalyticsService(store)
    sections: list[ReportSection] = []

    try:
        communities = await analytics.communities()
        key_entities = await analytics.key_entities(top_k=10)
        links = await analytics.link_prediction(top_k=10)
        risk = await analytics.risk_assessment(run_anomalies=True)
    except Exception:  # noqa: BLE001
        return [
            ReportSection(heading="Network Analysis", body=["Analytics unavailable for this graph."])
        ]

    sections.append(
        ReportSection(
            heading="Community Structure",
            body=[
                f"Communities detected: {communities.count}",
                f"Network density: {communities.network_density}",
                *[f"Community #{c.community_id}: {c.size} entities" for c in communities.communities[:8]],
            ],
        )
    )

    sections.append(
        ReportSection(
            heading="Key Influencers",
            body=[
                f"{e.entity_id}  score={e.score}  factor={e.dominant_factor}"
                for e in key_entities.items
            ]
            or ["None identified."],
        )
    )

    sections.append(
        ReportSection(
            heading="Possible Hidden Links",
            body=[
                f"{l.source} <-> {l.target}  (score {l.score})" for l in links.candidates
            ]
            or ["None."],
        )
    )

    sections.append(
        ReportSection(
            heading="Risk Overview",
            body=[
                f"{r.entity_id}  {r.risk_level}  score={r.risk_score}"
                for r in risk.items[:10]
            ],
        )
    )

    if risk.anomalies:
        sections.append(
            ReportSection(
                heading="Flagged Anomalies",
                body=[f"- {a}" for a in risk.anomalies],
            )
        )

    return sections


async def build_transaction_analysis(session: AsyncSession, store, title: str) -> list[ReportSection]:
    # No dedicated transaction table in this phase; derive from graph TRANSFERRED_TO
    # edges present on entity accounts.
    analytics = AnalyticsService(store)
    try:
        graph = await analytics._graph()
    except Exception:  # noqa: BLE001
        return [ReportSection(heading="Transaction Analysis", body=["Unavailable."])]

    transfer_edges = [
        (a, b, d.get("type"))
        for a, b, d in graph.edges(data=True)
        if d.get("type") == "TRANSFERRED_TO"
    ]
    return [
        ReportSection(
            heading="Transaction Analysis",
            body=_fmt_lines({"Transfers mapped (synthetic)": len(transfer_edges)}),
        ),
        ReportSection(
            heading="Transfer Flows",
            body=[f"{a} -> {b}" for a, b, _ in transfer_edges] or ["No transfer edges present."],
        ),
    ]


async def build_communication_analysis(
    session: AsyncSession, store, title: str
) -> list[ReportSection]:
    analytics = AnalyticsService(store)
    try:
        graph = await analytics._graph()
    except Exception:  # noqa: BLE001
        return [ReportSection(heading="Communication Analysis", body=["Unavailable."])]

    comm_edges = [
        (a, b)
        for a, b, d in graph.edges(data=True)
        if d.get("type") in {"CALLED", "USES"}
    ]
    return [
        ReportSection(
            heading="Communication Analysis",
            body=_fmt_lines({"Communication links (synthetic)": len(comm_edges)}),
        ),
        ReportSection(
            heading="Frequent Contacts",
            body=[f"{a} <-> {b}" for a, b in comm_edges[:20]] or ["No communication edges present."],
        ),
    ]


BUILDERS = {
    "investigation_summary": build_investigation_summary,
    "entity_intelligence": build_entity_intelligence,
    "network_analysis": build_network_analysis,
    "transaction_analysis": build_transaction_analysis,
    "communication_analysis": build_communication_analysis,
}

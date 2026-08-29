"""Entity resolution (original Phase 5).

Proposes candidate duplicate identities from entity mentions + known aliases.
Outputs candidates with a confidence score and supporting evidence. Always
requires analyst confirmation — never auto-merges uncertain identities.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_UNWANTED = re.compile(r"[\W_]+")


def normalize_name(name: str) -> str:
    """Lowercase, strip punctuation, and collapse whitespace."""
    cleaned = _UNWANTED.sub(" ", name).strip().lower()
    return re.sub(r"\s+", " ", cleaned)


def _initials(name: str) -> str:
    return "".join(part[0] for part in name.split() if part)


def similarity(a: str, b: str) -> float:
    """Return a 0..1 similarity between two names.

    Combines token-set overlap (Jaccard) with a token-initial/prefix matcher so
    aliases like "Rahul Kumar" ~ "Rahul K" / "R Kumar" are recognized.
    """
    na, nb = normalize_name(a), normalize_name(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0

    ta, tb = na.split(), nb.split()
    if not ta or not tb:
        return 0.0

    # Jaccard on full tokens.
    inter = len(set(ta) & set(tb))
    union = len(set(ta) | set(tb))
    jaccard = inter / union if union else 0.0

    # Token-level initial/prefix matches (e.g. "k" <= "kumar", "rah" <= "rahul").
    # Substring matching requires length >= 3 to avoid short-token false hits.
    def _token_match(x: str, y: str) -> bool:
        if x.startswith(y) or y.startswith(x):
            return True
        if len(x) >= 3 and len(y) >= 3 and (y in x or x in y):
            return True
        return False

    prefix_hits = 0
    for x in ta:
        for y in tb:
            if x != y and _token_match(x, y):
                prefix_hits += 1
                break

    best_prefix = prefix_hits / max(len(ta), len(tb))

    # Substring-level evidence for single-word aliases / initials.
    if na in nb or nb in na:
        best_prefix = max(best_prefix, 0.8)
    init_a, init_b = _initials(na), _initials(nb)
    if init_a and init_b and (init_a == init_b or init_a in init_b or init_b in init_a):
        best_prefix = max(best_prefix, 0.7)

    return max(jaccard, best_prefix)


@dataclass
class ResolutionCandidate:
    """A suggested duplicate pair, pending analyst confirmation."""

    existing_id: str
    existing_name: str
    candidate_id: str
    candidate_name: str
    confidence: float
    evidence: list[str] = field(default_factory=list)


@dataclass
class ResolutionConflict:
    """A proposed merge, flagged for analyst confirmation."""

    candidate: ResolutionCandidate
    status: str = "pending"  # pending | confirmed | rejected


def resolve(
    known: dict[str, list[str]],  # entity_id -> list of known names/aliases
    mentions: list,
) -> list[ResolutionConflict]:
    """Match new entity mentions against known entities by alias overlap.

    `mentions` are objects with `.entity_id`, `.name`, and (optionally) `.aliases`.
    Returns proposed merges, each requiring confirmation.
    """
    conflicts: list[ResolutionConflict] = []
    seen: set[tuple[str, str]] = set()

    known_items = list(known.items())
    for mention in mentions:
        names = [mention.name, *(getattr(mention, "aliases", []) or [])]
        for existing_id, existing_names in known_items:
            if mention.entity_id == existing_id:
                continue
            pair = tuple(sorted((mention.entity_id, existing_id)))
            if pair in seen:
                continue

            best = 0.0
            best_pair: tuple[str, str] | None = None
            for n1 in names:
                for n2 in existing_names:
                    s = similarity(n1, n2)
                    if s > best:
                        best = s
                        best_pair = (n1, n2)

            if best >= 0.6:  # strong-enough overlap to propose
                seen.add(pair)
                evidence = [f"name overlap: '{best_pair[0]}' ~ '{best_pair[1]}'"]
                conflicts.append(
                    ResolutionConflict(
                        candidate=ResolutionCandidate(
                            existing_id=existing_id,
                            existing_name=existing_names[0],
                            candidate_id=mention.entity_id,
                            candidate_name=mention.name,
                            confidence=round(best * 100.0, 1),
                            evidence=evidence,
                        )
                    )
                )
    return conflicts


def confirm(conflict: ResolutionConflict, decision: bool) -> ResolutionConflict:
    """Record an analyst decision (confirm or reject) on a merge."""
    conflict.status = "confirmed" if decision else "rejected"
    return conflict

"""Graph materializer tests (Phase 6).

Verifies relational records (profiles + case links) are materialized into the
in-memory graph store — no Neo4j required.
"""
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.graph.memory_store import MemoryGraphStore
from app.models.case import Case, CaseCriminal, CasePriority, CaseStatus
from app.models.criminal import CriminalProfile, EntityType, RiskLevel
from app.services.graph_materializer import GraphMaterializer


def test_materialize_profiles_and_case_links() -> None:
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    S = async_sessionmaker(eng, expire_on_commit=False)

    async def scenario() -> dict:
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        store = MemoryGraphStore()

        async with S() as session:
            p1 = CriminalProfile(
                secret_id="P-0421",
                profile_type=EntityType.PERSON.value,
                name="Person A",
                aliases=["Alpha"],
                risk_score=94,
                risk_level=RiskLevel.CRITICAL.value,
                confidence=96,
                attributes={},
            )
            p2 = CriminalProfile(
                secret_id="P-0182",
                profile_type=EntityType.PERSON.value,
                name="Person B",
                risk_score=71,
                risk_level=RiskLevel.HIGH.value,
                confidence=88,
                attributes={},
            )
            case = Case(
                case_number="CASE-2026-0001",
                title="Organized Network Analysis",
                status=CaseStatus.OPEN.value,
                priority=CasePriority.HIGH.value,
            )
            session.add_all([p1, p2, case])
            await session.flush()

            session.add(CaseCriminal(case_id=case.id, profile_id=p1.id, role_in_case="PRIMARY"))
            session.add(CaseCriminal(case_id=case.id, profile_id=p2.id, role_in_case="RELATED"))
            await session.commit()

            summary = await GraphMaterializer(session, store).run()

        return {"summary": summary, "store": store, "case_id": case.id}

    def run() -> dict:
        return asyncio.run(scenario())

    result = run()
    store: MemoryGraphStore = result["store"]

    assert result["summary"]["entities"] == 3  # 2 profiles + 1 case
    assert result["summary"]["edges"] == 2      # 2 INVOLVED_IN links
    assert result["summary"]["cases"] == 1

    # Profiles became entity nodes with domain properties.
    person = store.nodes["P-0421"]
    assert person.type == "PERSON"
    assert person.properties["risk_score"] == 94

    # Case node exists.
    case_key = f"CS-{result['case_id']:04d}"
    assert case_key in store.nodes

    # Two INVOLVED_IN edges present.
    involved = [e for e in store.edges.values() if e.type == "INVOLVED_IN"]
    assert len(involved) == 2

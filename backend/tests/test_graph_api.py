"""Graph API tests (Phase 6).

Exercises the `/api/v1/graph/*` endpoints using the in-memory graph store injected
via dependency override — no Neo4j required.
"""
import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_graph_store
from app.core.database import Base, get_db_session
from app.core.security import hash_password
from app.graph.memory_store import MemoryGraphStore
from app.graph.types import GraphEdge, GraphNode
from app.main import app
from app.models.user import User, UserRole

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin-secret"


def _seed(nodes, edges) -> MemoryGraphStore:
    store = MemoryGraphStore()
    for n in nodes:
        store.nodes[n.id] = n
    for e in edges:
        store.edges[e.id] = e
    return store


@pytest.fixture()
def graph_client() -> TestClient:
    """TestClient with SQLite DB + in-memory graph store injected."""
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    S = async_sessionmaker(eng, expire_on_commit=False)

    async def setup():
        async with eng.begin() as c:
            await c.run_sync(Base.metadata.create_all)
        async with S() as s:
            s.add(User(username="admin", email="admin@example.com",
                      password_hash=hash_password("admin-secret"), role=UserRole.ADMIN.value))
            await s.commit()

    asyncio.run(setup())

    store = _seed(
        [GraphNode(id="P-0421", type="PERSON", name="Person A"),
         GraphNode(id="V-2048", type="VEHICLE", name="Vehicle VX"),
         GraphNode(id="O-1101", type="ORGANIZATION", name="Org Orion")],
        [GraphEdge(id="E1", source_id="P-0421", target_id="O-1101", type="MEMBER_OF"),
         GraphEdge(id="E2", source_id="P-0421", target_id="V-2048", type="OWNS")],
    )

    async def override_db():
        async with S() as s:
            yield s

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_graph_store] = lambda: store
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    asyncio.run(eng.dispose())


def _auth(db_client: TestClient) -> dict:
    resp = db_client.post("/api/v1/auth/login",
                          json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_network_returns_nodes_and_edges(graph_client: TestClient) -> None:
    resp = graph_client.get("/api/v1/graph/network", headers=_auth(graph_client))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["nodes"]) == 3
    assert len(body["edges"]) == 2


def test_network_filter_by_node_type(graph_client: TestClient) -> None:
    resp = graph_client.get("/api/v1/graph/network",
                            params={"node_types": ["ORGANIZATION"]},
                            headers=_auth(graph_client))
    assert resp.status_code == 200
    body = resp.json()
    assert [n["id"] for n in body["nodes"]] == ["O-1101"]


def test_get_entity(graph_client: TestClient) -> None:
    resp = graph_client.get("/api/v1/graph/entities/P-0421", headers=_auth(graph_client))
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "P-0421"
    assert body["type"] == "PERSON"


def test_get_entity_missing_404(graph_client: TestClient) -> None:
    resp = graph_client.get("/api/v1/graph/entities/ZZZ-9999", headers=_auth(graph_client))
    assert resp.status_code == 404


def test_get_neighbors(graph_client: TestClient) -> None:
    resp = graph_client.get("/api/v1/graph/entities/P-0421/neighbors",
                            headers=_auth(graph_client))
    assert resp.status_code == 200
    ids = {n["id"] for n in resp.json()}
    assert ids == {"O-1101", "V-2048"}


def test_expand_neighborhood(graph_client: TestClient) -> None:
    resp = graph_client.get("/api/v1/graph/entities/P-0421/expand",
                            params={"depth": 2},
                            headers=_auth(graph_client))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["nodes"]) == 3
    assert len(body["edges"]) == 2


def test_graph_requires_auth(graph_client: TestClient) -> None:
    resp = graph_client.get("/api/v1/graph/network")
    assert resp.status_code == 401


def test_materialize_requires_privilege(graph_client: TestClient) -> None:
    resp = graph_client.post("/api/v1/graph/materialize")
    assert resp.status_code == 401

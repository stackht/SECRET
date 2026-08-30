"""In-memory graph store (Phase 6).

Implements the `GraphStore` protocol with plain Python data structures. Used for
tests and lightweight prototyping without requiring a live Neo4j instance.
"""
from app.graph.types import GraphEdge, GraphNode, GraphSubgraph


class MemoryGraphStore:
    """Naive in-memory implementation of the graph store protocol."""

    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: dict[str, GraphEdge] = {}
        self._edge_counter = 0

    # --- mutations ---

    def _new_edge_id(self) -> str:
        self._edge_counter += 1
        return f"E-{self._edge_counter:04d}"

    async def upsert_node(self, node: GraphNode) -> None:
        self.nodes[node.id] = node

    async def upsert_edge(self, edge: GraphEdge) -> None:
        if edge.id in self.edges:
            self.edges[edge.id] = edge
            return
        for existing in self.edges.values():
            if (existing.source_id, existing.target_id, existing.type) == (
                edge.source_id,
                edge.target_id,
                edge.type,
            ):
                existing.properties = edge.properties
                return
        store_edge = GraphEdge(
            id=self._new_edge_id(),
            source_id=edge.source_id,
            target_id=edge.target_id,
            type=edge.type,
            properties=edge.properties,
        )
        self.edges[store_edge.id] = store_edge

    # --- reads ---

    async def get_entity(self, entity_id: str) -> GraphNode | None:
        return self.nodes.get(entity_id)

    async def get_relationships(self, entity_id: str) -> list[GraphEdge]:
        return [
            e
            for e in self.edges.values()
            if e.source_id == entity_id or e.target_id == entity_id
        ]

    async def get_neighbors(
        self,
        entity_id: str,
        node_types: list[str] | None = None,
        rel_types: list[str] | None = None,
    ) -> list[GraphNode]:
        node_types = set(node_types or ())
        rel_types = set(rel_types or ())
        result: list[GraphNode] = []
        for edge in self.edges.values():
            if rel_types and edge.type not in rel_types:
                continue
            if edge.source_id == entity_id:
                neighbor_id = edge.target_id
            elif edge.target_id == entity_id:
                neighbor_id = edge.source_id
            else:
                continue
            neighbor = self.nodes.get(neighbor_id)
            if neighbor and (not node_types or neighbor.type in node_types):
                result.append(neighbor)
        # Deduplicate while preserving order.
        seen: set[str] = set()
        unique: list[GraphNode] = []
        for node in result:
            if node.id not in seen:
                seen.add(node.id)
                unique.append(node)
        return unique

    async def expand_neighborhood(
        self,
        entity_id: str,
        depth: int = 1,
        node_types: list[str] | None = None,
        rel_types: list[str] | None = None,
    ) -> GraphSubgraph:
        start = self.nodes.get(entity_id)
        if start is None:
            return GraphSubgraph()

        visited: set[str] = set()
        nodes_by_id: dict[str, GraphNode] = {start.id: start}
        edges: list[GraphEdge] = []
        frontier = {entity_id}
        rel_types_set = set(rel_types or ())
        node_types_set = set(node_types or ())

        for _ in range(depth):
            next_frontier: set[str] = set()
            for current in frontier:
                if current in visited:
                    continue
                visited.add(current)
                for edge in self.edges.values():
                    if rel_types_set and edge.type not in rel_types_set:
                        continue
                    connected = False
                    if edge.source_id == current:
                        neighbor_id = edge.target_id
                        connected = True
                    elif edge.target_id == current:
                        neighbor_id = edge.source_id
                        connected = True
                    if not connected:
                        continue
                    neighbor = self.nodes.get(neighbor_id)
                    if neighbor is None:
                        continue
                    if node_types_set and neighbor.type not in node_types_set:
                        continue
                    if edge not in edges:
                        edges.append(edge)
                    if neighbor_id not in nodes_by_id:
                        nodes_by_id[neighbor_id] = neighbor
                    next_frontier.add(neighbor_id)
            frontier = next_frontier

        return GraphSubgraph(nodes=list(nodes_by_id.values()), edges=edges)

    async def build_network(
        self,
        node_types: list[str] | None = None,
        rel_types: list[str] | None = None,
        limit: int = 500,
    ) -> GraphSubgraph:
        node_types_set = set(node_types or ())
        rel_types_set = set(rel_types or ())
        nodes = [
            n for n in self.nodes.values()
            if not node_types_set or n.type in node_types_set
        ][:limit]
        node_ids = {n.id for n in nodes}
        edges = [
            e for e in self.edges.values()
            if e.source_id in node_ids and e.target_id in node_ids
            and (not rel_types_set or e.type in rel_types_set)
        ]
        return GraphSubgraph(nodes=nodes, edges=edges)

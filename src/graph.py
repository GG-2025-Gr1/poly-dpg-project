import networkx as nx
from typing import List, Union, Optional

from .elements import Vertex, Hyperedge


class Graph:
    def __init__(self):
        self._nx_graph = nx.Graph()

    def add_vertex(self, v: Vertex) -> None:
        """Dodaje wierzchołek geometryczny 2D."""
        self._nx_graph.add_node(v.uid, type="vertex", data=v, x=v.x, y=v.y)

    def update_vertex(
        self, uid: Union[int, str], x: Optional[float] = None, y: Optional[float] = None
    ) -> None:
        """Aktualizuje pozycję wierzchołka."""

        vertex_obj = self.get_vertex(uid)

        if x is not None:
            vertex_obj.x = x
            self._nx_graph.nodes[uid]["x"] = x
        if y is not None:
            vertex_obj.y = y
            self._nx_graph.nodes[uid]["y"] = y

    def add_hyperedge(self, h: Hyperedge) -> None:
        """Dodaje węzeł hiperkrawędzi."""
        self._nx_graph.add_node(
            h.uid, type="hyperedge", label=h.label, R=h.r, B=h.b, data=h
        )

    def update_hyperedge(
        self,
        uid: Union[int, str],
        label: Optional[str] = None,
        r: Optional[int] = None,
        b: Optional[int] = None,
    ) -> None:
        """Aktualizuje właściwości hiperkrawędzi."""

        hyperedge_obj = self.get_hyperedge(uid)

        if label is not None:
            hyperedge_obj.label = label
            self._nx_graph.nodes[uid]["label"] = label

        if r is not None:
            hyperedge_obj.r = r
            self._nx_graph.nodes[uid]["r"] = r
        if b is not None:
            hyperedge_obj.b = b
            self._nx_graph.nodes[uid]["b"] = b

    def connect(self, node_id1: Union[int, str], node_id2: Union[int, str]) -> None:
        """Tworzy krawędź grafową między węzłami."""

        if node_id1 not in self._nx_graph.nodes:
            raise ValueError(f"Węzeł o ID {node_id1} nie istnieje w grafie.")
        if node_id2 not in self._nx_graph.nodes:
            raise ValueError(f"Węzeł o ID {node_id2} nie istnieje w grafie.")

        self._nx_graph.add_edge(node_id1, node_id2)

    def get_node(self, uid) -> Union[Vertex, Hyperedge, None]:
        if uid not in self._nx_graph.nodes:
            raise ValueError(f"Węzeł o ID {uid} nie istnieje w grafie.")
        return self._nx_graph.nodes[uid]["data"]

    def get_vertex(self, uid: Union[int, str]) -> Vertex:
        node = self.get_node(uid)
        if not isinstance(node, Vertex):
            raise ValueError(f"Węzeł o ID {uid} nie jest wierzchołkiem typu Vertex.")
        return node

    def get_hyperedge(self, uid: Union[int, str]) -> Hyperedge:
        node = self.get_node(uid)
        if not isinstance(node, Hyperedge):
            raise ValueError(f"Węzeł o ID {uid} nie jest hiperkrawędzią.")
        return node

    def remove_node(self, uid: Union[int, str]) -> None:
        if uid not in self._nx_graph:
            raise ValueError(f"Węzeł o ID {uid} nie istnieje w grafie.")
        self._nx_graph.remove_node(uid)

    def get_neighbors(self, uid: Union[int, str]) -> List[Vertex]:
        if not isinstance(self.get_node(uid), Vertex):
            raise ValueError(f"Węzeł o ID {uid} nie jest wierzchołkiem typu Vertex.")

        neighbors = set()
        for hyperedge_id in self._nx_graph.neighbors(uid):
            neighbors_with_self = self.get_hyperedge_vertices(hyperedge_id)
            for neighbor_obj in neighbors_with_self:
                if neighbor_obj.uid != uid:
                    neighbors.add(neighbor_obj)

        return list(neighbors)

    def get_vertex_hyperedges(self, vertex_uid: Union[int, str]) -> List[Hyperedge]:
        """Zwraca listę hiperkrawędzi połączonych z danym wierzchołkiem."""
        if not isinstance(self.get_node(vertex_uid), Vertex):
            raise ValueError(
                f"Węzeł o ID {vertex_uid} nie jest wierzchołkiem typu Vertex."
            )

        hyperedges = set()
        for neighbor_id in self._nx_graph.neighbors(vertex_uid):
            try:
                hyperedge_obj = self.get_hyperedge(neighbor_id)
                hyperedges.add(hyperedge_obj)
            except ValueError:
                continue

        return list(hyperedges)

    def get_hyperedge_vertices(self, hyperedge_uid: Union[int, str]) -> List[Vertex]:
        """Zwraca listę wierzchołków połączonych z daną hiperkrawędzią."""

        if not isinstance(self.get_node(hyperedge_uid), Hyperedge):
            raise ValueError(f"Węzeł o ID {hyperedge_uid} nie jest hiperkrawędzią.")

        vertices = set()
        for neighbor_id in self._nx_graph.neighbors(hyperedge_uid):
            try:
                vertex_obj = self.get_vertex(neighbor_id)
                vertices.add(vertex_obj)
            except ValueError:
                continue

        return list(vertices)

    def get_hyperedges_between_vertices(
        self, vertex_uid1: Union[int, str], vertex_uid2: Union[int, str]
    ) -> List[Hyperedge]:
        """Zwraca hiperkrawędź łączącą dwa wierzchołki, jeśli istnieje."""

        if not isinstance(self.get_node(vertex_uid1), Vertex):
            raise ValueError(
                f"Węzeł o ID {vertex_uid1} nie jest wierzchołkiem typu Vertex."
            )
        if not isinstance(self.get_node(vertex_uid2), Vertex):
            raise ValueError(
                f"Węzeł o ID {vertex_uid2} nie jest wierzchołkiem typu Vertex."
            )

        neighbors1 = set(self.get_vertex_hyperedges(vertex_uid1))
        neighbors2 = set(self.get_vertex_hyperedges(vertex_uid2))

        return list(neighbors1.intersection(neighbors2))

    @property
    def nx_graph(self):
        return self._nx_graph

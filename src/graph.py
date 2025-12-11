import networkx as nx
from typing import List, Union, Optional
from elements import Vertex, Hyperedge

class Graph:
    def __init__(self):
        self._nx_graph = nx.Graph()

    def add_vertex(self, v: Vertex):
        """Dodaje wierzchołek geometryczny 2D."""
        # Zapisujemy obiekt Vertex w 'data' oraz współrzędne wprost dla NetworkX (do rysowania)
        self._nx_graph.add_node(
            v.uid, 
            type='vertex', 
            data=v, 
            x=v.x, 
            y=v.y
        )

    def add_hyperedge(self, h: Hyperedge):
        """Dodaje węzeł hiperkrawędzi (Q, E...)."""
        self._nx_graph.add_node(
            h.uid, 
            type='hyperedge', 
            label=h.label, 
            R=h.r, 
            B=h.b, 
            data=h
        )

    def connect(self, node_id1, node_id2):
        """Tworzy krawędź grafową między węzłami."""
        if node_id1 not in self._nx_graph.nodes or node_id2 not in self._nx_graph.nodes:
            raise ValueError(f"Próba połączenia nieistniejących węzłów: {node_id1} - {node_id2}")
        self._nx_graph.add_edge(node_id1, node_id2)

    def get_node(self, uid) -> Union[Vertex, Hyperedge, None]:
        if uid not in self._nx_graph.nodes:
            return None
        return self._nx_graph.nodes[uid]['data']

    def remove_node(self, uid):
        if uid in self._nx_graph:
            self._nx_graph.remove_node(uid)

    def get_neighbors(self, uid) -> List[Union[Vertex, Hyperedge]]:
        if uid not in self._nx_graph:
            return []
        neighbors_ids = self._nx_graph.neighbors(uid)
        return [self.get_node(nid) for nid in neighbors_ids]

    @property
    def nx_graph(self):
        return self._nx_graph
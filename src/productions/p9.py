from typing import List, Union
from ..graph import Graph
from ..elements import Hyperedge
from .production import Production


class ProductionP9(Production):
    """
    P9: Oznaczenie elementu (S) do rafinacji.
    Znajduje element S z R=0 (lub bez R) i ustawia R=1.
    """

    def find_lhs(self, graph: Graph, target_id: Union[int, str] = None) -> List[Hyperedge]:
        candidates = []
        for node_id, data in graph.nx_graph.nodes(data=True):
            he = data.get("data")

            # 1. Musi to być Hyperedge
            if not isinstance(he, Hyperedge):
                continue

            # 2. Opcjonalne filtrowanie po ID
            if target_id is not None and he.uid != target_id:
                continue

            # 3. Musi mieć etykietę 'S' (element siatki)
            if he.label != 'S':
                continue

            # 4. Musi mieć R=0
            if he.r != 0:
                continue

            vertices = graph.get_hyperedge_vertices(he.uid)
            
            if len(vertices) != 6:
                continue
            
            edges_found = self._get_boundary_edges(graph, vertices)
            if len(edges_found) != 6:
                continue

            candidates.append(he)

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        if match_node.r == 0:
            # 2. Ustawienie atrybutu R=1
            graph.update_hyperedge(match_node.uid, r=1)
            print(f"P9: Oznaczono element S={match_node.uid} (R=1) do rafinacji.")
        else:
            print(f"P9: Element S={match_node.uid} ma już R={match_node.r}. Brak zmian.")

    def _get_boundary_edges(self, graph: Graph, vertices: list) -> List[Hyperedge]:
        """
        Pomocnicza metoda znajdująca krawędzie 'E' łączące wierzchołki sześciokąta.
        """
        found_edges = set()
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                v1, v2 = vertices[i], vertices[j]
                common_edges = graph.get_hyperedges_between_vertices(v1.uid, v2.uid)
                for ce in common_edges:
                    if ce.label == 'E':
                        found_edges.add(ce)
        return list(found_edges)        
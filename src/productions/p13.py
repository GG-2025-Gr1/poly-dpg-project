from typing import List, Union
from ..graph import Graph
from ..elements import Hyperedge
from .production import Production

class ProductionP13(Production):
    """
    P13: Oznaczenie krawędzi elementu siedmiokątnego.
    Dla elementu T z R=1, ustawia R=1 wszystkim jego krawędziom (E).
    """

    def find_lhs(self, graph: Graph, target_id: Union[int, str] = None) -> List[Hyperedge]:
        candidates = []
        for node_id, data in graph.nx_graph.nodes(data=True):
            he = data.get("data")

            if not isinstance(he, Hyperedge):
                print(f"-> P13: Pomijam węzeł {he.uid}, nie jest Hyperedge.")
                continue

            if target_id is not None and he.uid != target_id:
                print(f"-> P13: Pomijam węzeł {he.uid}, nie pasuje do target_id.")
                continue

            if he.label != "T":
                print(f"-> P13: Pomijam węzeł {he.uid}, nie ma etykiety 'T'.")
                continue

            if he.r != 1:
                print(f"-> P13: Pomijam węzeł {he.uid}, R={he.r} (wymagane R=1).")
                continue

            vertices = graph.get_hyperedge_vertices(he.uid)
            if len(vertices) != 7:
                print(f"-> P13: Pomijam węzeł {he.uid}, ma {len(vertices)} wierzchołków (wymagane 7).")
                continue

            edges_found = self._get_boundary_edges(graph, vertices)

            if len(edges_found) != 7:
                print(f"-> P13: Pomijam węzeł {he.uid}, znaleziono tylko {len(edges_found)} krawędzi (wymagane 7).")
                continue

            candidates.append(he)

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        vertices = graph.get_hyperedge_vertices(match_node.uid)
        edges_to_mark = self._get_boundary_edges(graph, vertices)

        for edge in edges_to_mark:
            if edge.r == 0:
                graph.update_hyperedge(edge.uid, r=1)
                print(f"-> P13: Oznaczono krawędź {edge.uid} (R=1).")

    def _get_boundary_edges(self, graph: Graph, vertices: list) -> List[Hyperedge]:
            found_edges = set()

            for i in range(len(vertices)):
                for j in range(i + 1, len(vertices)):
                    v1, v2 = vertices[i], vertices[j]

                    common_edges = graph.get_hyperedges_between_vertices(v1.uid, v2.uid)

                    for ce in common_edges:
                        if ce.label == 'E':
                            found_edges.add(ce)

            return list(found_edges)
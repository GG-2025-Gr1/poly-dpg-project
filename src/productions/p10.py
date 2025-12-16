from typing import List, Union
from ..graph import Graph
from ..elements import Hyperedge
from .production import Production


class ProductionP10(Production):
    """
    P10: Oznaczenie krawędzi elementu sześciokątengo.
    Dla elementu S z R=1, ustawia R=1 wszystkim jego krawędziom (E).
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

            # 3. Musi mieć etykietę 'S'
            if he.label != 'S':
                continue

            # 4. Musi mieć R=1 (oznaczony do podziału)
            if he.r != 1:
                continue

            # 5. Sprawdzenie topologii: Musi mieć 6 wierzchołków
            vertices = graph.get_hyperedge_vertices(he.uid)
            if len(vertices) != 6:
                continue

            # Sprawdzamy czy wierzchołki są połączone krawędziami typu E
            # To jest "miękkie" sprawdzenie - szukamy czy da się znaleźć krawędzie do oznaczenia
            edges_found = self._get_boundary_edges(graph, vertices)

            # Wymagamy, aby element był otoczony krawędziami (powinien mieć 6 krawędzi)
            if len(edges_found) != 6:
                continue

            candidates.append(he)

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        vertices = graph.get_hyperedge_vertices(match_node.uid)
        edges_to_mark = self._get_boundary_edges(graph, vertices)

        for edge in edges_to_mark:
            if edge.r == 0:
                graph.update_hyperedge(edge.uid, r=1)
                print(f"-> P10: Oznaczono krawędź {edge.uid} (R=1).")

    def _get_boundary_edges(self, graph: Graph, vertices: list) -> List[Hyperedge]:
        """
        Pomocnicza metoda znajdująca krawędzie 'E' łączące wierzchołki sześciokąta.
        Zakłada, że wierzchołki tworzą cykl lub są połączone krawędziami.
        """
        found_edges = set()

        # Sprawdzamy każdą parę wierzchołków
        # W grafie PolyDPG krawędzie są niezależnymi węzłami Hyperedge łączącymi dwa Vertex
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                v1, v2 = vertices[i], vertices[j]

                # Pobierz hiperkrawędzie między v1 a v2
                common_edges = graph.get_hyperedges_between_vertices(v1.uid, v2.uid)

                # Szukamy takich, które są typu 'E'
                for ce in common_edges:
                    if ce.label == 'E':
                        found_edges.add(ce)

        return list(found_edges)

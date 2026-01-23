import math
from typing import List, Union, Optional
from ..graph import Graph
from ..elements import Hyperedge, Vertex
from .production import Production


class ProductionP14(Production):
    """
    P14: Podział elementu siedmiokątnego (T, R=1),
    jeśli wszystkie jego krawędzie zostały wcześniej podzielone
    """

    def find_lhs(
        self, graph: Graph, target_id: Union[int, str] = None
    ) -> List[Hyperedge]:
        candidates = []
        for node_id, data in graph.nx_graph.nodes(data=True):
            he = data.get("data")

            # 1. Musi to być Hyperedge typu 'Q' z R=1
            if not isinstance(he, Hyperedge) or he.label != "T" or he.r != 1:
                continue

            # 2. Opcjonalne filtrowanie po ID
            if target_id is not None and he.uid != target_id:
                continue

            # 3. Musi mieć dokładnie 7 wierzchołków
            corners = graph.get_hyperedge_vertices(he.uid)
            if len(corners) != 7:
                continue

            # 4. Sortujemy narożniki geometrycznie (przeciwnie do wskazówek zegara),
            # Jest to niezbędne, aby sprawdzić sąsiedztwo na bokach
            sorted_corners = self._sort_vertices_counter_clockwise(corners)

            # 5. Sprawdzamy warunek "all edges are broken"
            # Pomiędzy każdą parą sąsiednich narożników musi istnieć "midpoint" (węzeł wiszący)
            # połączony krawędziami E.
            is_broken = True
            for i in range(7):
                v_curr = sorted_corners[i]
                v_next = sorted_corners[(i + 1) % 7]

                midpoint = self._find_midpoint_between(graph, v_curr, v_next)
                if midpoint is None:
                    is_broken = False
                    break
            if is_broken:
                candidates.append(he)

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        # 1. Pobieramy i sortujemy narożniki starego Q
        corners = graph.get_hyperedge_vertices(match_node.uid)
        corners = self._sort_vertices_counter_clockwise(corners)

        # 2. Midpointy na krawędziach
        midpoints = []
        for i in range(7):
            v_curr = corners[i]
            v_next = corners[(i + 1) % 7]
            midpoint = self._find_midpoint_between(graph, v_curr, v_next)
            midpoints.append(midpoint)

        # 3. Obliczenie środka
        center_x = sum(v.x for v in corners) / 7
        center_y = sum(v.y for v in corners) / 7

        center_uid = f"{match_node.uid}_center"
        center = Vertex(uid=center_uid, x=center_x, y=center_y)
        graph.add_vertex(center)

        # 4. Usunięcie starego Q
        graph.remove_node(match_node.uid)

        # 5. Tworzenie 7 nowych Q (R=0)
        for i in range(7):
            q_uid = f"{match_node.uid}_sub_Q{i}"
            new_q = Hyperedge(uid=q_uid, label="Q", r=0, b=0)
            graph.add_hyperedge(new_q)

            v1 = corners[i]
            v2 = midpoints[i]
            v3 = center
            v4 = midpoints[(i - 1) % 7]

            for v in [v1, v2, v3, v4]:
                graph.connect(q_uid, v.uid)

        # 6. Nowe wewnętrzne krawędzie E (R=0, B=0)
        for i, mid in enumerate(midpoints):
            e_uid = f"{match_node.uid}_inner_E{i}"
            new_e = Hyperedge(uid=e_uid, label="E", r=0, b=0)
            graph.add_hyperedge(new_e)

            graph.connect(e_uid, mid.uid)
            graph.connect(e_uid, center.uid)

        print(f"-> P14: Podzielono siedmiokąt Q {match_node.uid}")

    # -----------------------------------------------------------------

    def _sort_vertices_counter_clockwise(self, vertices: List[Vertex]) -> List[Vertex]:
        cx = sum(v.x for v in vertices) / len(vertices)
        cy = sum(v.y for v in vertices) / len(vertices)

        return sorted(vertices, key=lambda v: math.atan2(v.y - cy, v.x - cx))

    def _find_midpoint_between(
        self, graph: Graph, v1: Vertex, v2: Vertex
    ) -> Optional[Vertex]:

        v1_edges = [e for e in graph.get_vertex_hyperedges(v1.uid) if e.label == "E"]
        v2_edges = [e for e in graph.get_vertex_hyperedges(v2.uid) if e.label == "E"]

        for e1 in v1_edges:
            for candidate in graph.get_hyperedge_vertices(e1.uid):
                if candidate in (v1, v2):
                    continue
                if not candidate.hanging:
                    continue

                for e2 in v2_edges:
                    if candidate in graph.get_hyperedge_vertices(e2.uid):
                        return candidate

        return None


import math
from typing import List, Union

from .production import Production
from ..graph import Graph
from ..elements import Hyperedge, Vertex


class ProductionP12(Production):
    """
    P12: Oznaczenie elementu do zmiany.
    Ustawia R=1 dla węzła o etykiecie Q, jeśli R było 0.
    """

    DEBUG = True

    def find_lhs(
        self, graph: Graph, target_id: Union[int, str] = None
    ) -> List[Hyperedge]:
        candidates: List[Hyperedge] = []
        for _, data in graph._nx_graph.nodes(data=True):
            if self.DEBUG:
                print(f"[P12] Sprawdzam węzeł: {data}")
            hyperedge_obj = data.get("data")
            # 1. For starters we only consider Hyperedge nodes as candidates
            #    as those constraints are the easiest to check
            #    and we need to change R 0 -> 1 in the P12's RHS
            if not isinstance(hyperedge_obj, Hyperedge):
                if self.DEBUG:
                    print("[P12] - pomijam, nie jest Hyperedge.")
                continue

            # 2. If target_id is given, only consider that specific node
            if target_id is not None and hyperedge_obj.uid != target_id:
                if self.DEBUG:
                    print(f"[P12] - pomijam, nie jest celem (target_id={target_id}).")
                continue

            # 3. It must have label Q
            if hyperedge_obj.label != "Q":
                if self.DEBUG:
                    print("[P12] - pomijam, nie jest Q.")
                continue

            # 4. It must have R=0
            if hyperedge_obj.r != 0:
                if self.DEBUG:
                    print("[P12] - pomijam, R != 0.")
                continue

            hyperedge_vertices = graph.get_hyperedge_vertices(hyperedge_obj.uid)
            if self.DEBUG:
                print(
                    f"[P12] - znalezione wierzchołki hiperkrawędzi: {hyperedge_vertices}"
                )

            # 5. It must be connected to exactly 7 vertices
            if len(hyperedge_vertices) != 7:
                if self.DEBUG:
                    print("[P12] - pomijam, nie ma 6 wierzchołków.")
                continue

            sorted_vertices = self._sort_vertices_counter_clockwise(hyperedge_vertices)

            should_continue = False
            for i, vertex in enumerate(sorted_vertices):
                if self.DEBUG:
                    print(f"[P12] - sprawdzam wierzchołek {vertex}")
                hyperedges = graph.get_hyperedges_between_vertices(
                    vertex_uid1=vertex.uid, vertex_uid2=sorted_vertices[(i + 1) % 7].uid
                )

                if self.DEBUG:
                    print(
                        f"[P12] -- hiperkrawędzie między {vertex.uid} a {sorted_vertices[(i + 1) % 7].uid}: {hyperedges}"
                    )

                if len(list(filter(lambda he: he.label == "E", hyperedges))) == 0:
                    should_continue = True
                    if self.DEBUG:
                        print(
                            "[P12] - pomijam, brak hiperkrawędzi E między wierzchołkami."
                        )

                if should_continue:
                    break
            if should_continue:
                continue

            if self.DEBUG:
                print(f"[P12] - znaleziono kandydata: {hyperedge_obj}")
            candidates.append(hyperedge_obj)

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        graph.update_hyperedge(match_node.uid, r=1)
        print(f"-> P12: Oznaczono element {match_node.uid} do podziału (R=1).")

    def _sort_vertices_counter_clockwise(self, vertices: List[Vertex]) -> List[Vertex]:
        """Sortuje wierzchołki geometrycznie wokół ich środka ciężkości."""
        if not vertices:
            return []

        # Środek ciężkości
        cx = sum(v.x for v in vertices) / len(vertices)
        cy = sum(v.y for v in vertices) / len(vertices)

        def angle_from_center(v):
            return math.atan2(v.y - cy, v.x - cx)

        return sorted(vertices, key=angle_from_center)

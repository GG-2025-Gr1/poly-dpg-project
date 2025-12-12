from typing import List, Union

from .production import Production
from ..graph import Graph
from ..elements import Hyperedge


class ProductionP0(Production):
    """
    P0: Oznaczenie elementu do zmiany.
    Ustawia R=1 dla węzła o etykiecie Q, jeśli R było 0.
    """

    DEBUG = True

    def find_lhs(
        self, graph: Graph, target_id: Union[int, str] = None
    ) -> List[Hyperedge]:
        candidates: List[Hyperedge] = []
        for _, data in graph._nx_graph.nodes(data=True):
            if self.DEBUG:
                print(f"[P0] Sprawdzam węzeł: {data}")
            hyperedge_obj = data.get("data")
            # 1. For starters we only consider Hyperedge nodes as candidates
            #    as those constraints are the easiest to check
            #    and we need to change R 0 -> 1 in the P0's RHS
            if not isinstance(hyperedge_obj, Hyperedge):
                if self.DEBUG:
                    print("[P0] - pomijam, nie jest Hyperedge.")
                continue

            # 2. If target_id is given, only consider that specific node
            if target_id is not None and hyperedge_obj.uid != target_id:
                if self.DEBUG:
                    print(f"[P0] - pomijam, nie jest celem (target_id={target_id}).")
                continue

            # 3. It must have label Q
            if hyperedge_obj.label != "Q":
                if self.DEBUG:
                    print("[P0] - pomijam, nie jest Q.")
                continue

            # 4. It must have R=0
            if hyperedge_obj.r != 0:
                if self.DEBUG:
                    print("[P0] - pomijam, R != 0.")
                continue

            hyperedge_vertices = graph.get_hyperedge_vertices(hyperedge_obj.uid)
            if self.DEBUG:
                print(
                    f"[P0] - znalezione wierzchołki hiperkrawędzi: {hyperedge_vertices}"
                )

            # 5. It must be connected to exactly 4 vertices
            if len(hyperedge_vertices) != 4:
                if self.DEBUG:
                    print("[P0] - pomijam, nie ma 4 wierzchołków.")
                continue

            should_continue = False
            for vertex in hyperedge_vertices:
                if self.DEBUG:
                    print(f"[P0] - sprawdzam wierzchołek {vertex}")
                vertex_neighbors = graph.get_neighbors(vertex.uid)
                if self.DEBUG:
                    print(
                        f"[P0] - sprawdzam sąsiadów wierzchołka {vertex}: {vertex_neighbors}"
                    )
                for vertex_neighbor in vertex_neighbors:
                    hyperedges = graph.get_hyperedges_between_vertices(
                        vertex_uid1=vertex.uid, vertex_uid2=vertex_neighbor.uid
                    )
                    if self.DEBUG:
                        print(
                            f"[P0] -- hiperkrawędzie między {vertex.uid} a {vertex_neighbor.uid}: {hyperedges}"
                        )
                    if vertex_neighbor not in hyperedge_vertices:
                        if self.DEBUG:
                            print(
                                f"[P0] - sąsiad {vertex_neighbor} nie należy do analizowanych wierzchołków, nie trzeba go brać pod uwagę."
                            )
                        continue

                    # Those 4 vertices must be connected by at least one of the following cases:
                    #   Case 1. Q hyperedge between pair of vertices (diagonal case)
                    #   Case 2. Q and E hyperedges between pair of vertices (edge case)
                    if hyperedge_obj not in hyperedges:
                        should_continue = True
                        if self.DEBUG:
                            print(
                                f"[P0] - pomijam, hiperkrawędź {hyperedge_obj} nie łączy tych wierzchołków."
                            )
                        break

                    hyperedges.remove(hyperedge_obj)

                    if (
                        len(hyperedges) != 0
                        and len(list(filter(lambda he: he.label == "E", hyperedges)))
                        == 0
                    ):
                        should_continue = True
                        if self.DEBUG:
                            print(
                                "[P0] - pomijam, brak hiperkrawędzi E między wierzchołkami."
                            )
                        break

                if should_continue:
                    break
            if should_continue:
                continue

            if self.DEBUG:
                print(f"[P0] - znaleziono kandydata: {hyperedge_obj}")
            candidates.append(hyperedge_obj)

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        graph.update_hyperedge(match_node.uid, r=1)
        print(f"-> P0: Oznaczono element {match_node.uid} do podziału (R=1).")

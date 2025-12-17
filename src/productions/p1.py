from itertools import combinations


from ..graph import Graph
from ..elements import Hyperedge
from .production import Production


class ProductionP1(Production):
    """
    P1: Oznaczenie krawędzi do zamiany.
    Ustawia R=1 dla krawędzi węzła o etykiecie Q, jeśli R było 1.
    """
    def __init__(self):
        pass

    def find_lhs(
        self, graph: Graph, target_id: str | int | None = None
    ) -> list[Hyperedge]:
        candidates: list[Hyperedge] = []
        for _, data in graph._nx_graph.nodes(data=True):
            hyperedge_obj = data.get("data")
            if not isinstance(hyperedge_obj, Hyperedge):
                continue

            if target_id is not None and hyperedge_obj.uid != target_id:
                continue

            # 3. It must have label Q
            if hyperedge_obj.label != "Q":
                continue

            # 4. It must have R=1
            if hyperedge_obj.r != 1:
                continue

            hyperedge_vertices = graph.get_hyperedge_vertices(hyperedge_obj.uid)

            # 5. It must be connected to exactly 4 vertices
            if len(hyperedge_vertices) != 4:
                continue

            should_continue = False
            for vertex in hyperedge_vertices:
                vertex_neighbors = graph.get_neighbors(vertex.uid)
                for vertex_neighbor in vertex_neighbors:
                    hyperedges = graph.get_hyperedges_between_vertices(
                        vertex_uid1=vertex.uid, vertex_uid2=vertex_neighbor.uid
                    )
                    if vertex_neighbor not in hyperedge_vertices:
                        continue

                    # Those 4 vertices must be connected by at least one of the following cases:
                    #   Case 1. Q hyperedge between pair of vertices (diagonal case)
                    #   Case 2. Q and E hyperedges between pair of vertices (edge case)
                    if hyperedge_obj not in hyperedges:
                        should_continue = True
                        break

                    hyperedges.remove(hyperedge_obj)

                    if (
                        len(hyperedges) != 0
                        and len(list(filter(lambda he: he.label == "E", hyperedges)))
                        == 0
                    ):
                        should_continue = True
                        break

                if should_continue:
                    break
            if should_continue:
                continue
            
            candidates.append(hyperedge_obj)

        return candidates
      
    def apply_rhs(self, graph: Graph, match: Hyperedge):
        # Set R=1 for the edges with label E between the 4 vertices of the matched Q hyperedge
        hyperedge_vertices = graph.get_hyperedge_vertices(match.uid)
        for vertex1, vertex2 in combinations(hyperedge_vertices, 2):
            hyperedges = graph.get_hyperedges_between_vertices(
                vertex_uid1=vertex1.uid, vertex_uid2=vertex2.uid
            )
            for he in hyperedges:
                if he.label == "E":
                    he.r = 1
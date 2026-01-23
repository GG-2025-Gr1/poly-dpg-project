from typing import List, Optional, Tuple, Set
import networkx as nx
from itertools import combinations
import uuid
import re

from ..graph import Graph
from ..elements import Hyperedge, Vertex
from .production import Production


class ProductionP2(Production):
    """
    P2: Breaking Shared Edges (Execution).
    If a hyperedge labeled 'E' is marked for refinement (R=1) and is a shared edge (B=0),
    check if the break has already occurred in the neighbor (isomorphism check).
    If so, sync the break.
    """

    def find_lhs(
        self, graph: Graph, target_id: Optional[str | int] = None
    ) -> List[Hyperedge]:
        candidates: List[Hyperedge] = []

        # Iterate over all nodes in the graph to find potential 'E' edges
        for node_id, data in graph._nx_graph.nodes(data=True):
            hyperedge_obj = data.get("data")

            # 1. Must be a Hyperedge
            if not isinstance(hyperedge_obj, Hyperedge):
                continue

            # Optional: Filter by target_id if provided (useful for focused application)
            if target_id is not None and hyperedge_obj.uid != target_id:
                continue

            # 2. Label must be 'E'
            if hyperedge_obj.label != "E":
                continue

            # 3. Must be marked for refinement (R=1)
            if hyperedge_obj.r != 1:
                continue

            # 4. Must NOT be a boundary edge (B=0)
            # "Shared edge" implies it's internal between elements.
            if hyperedge_obj.b != 0:
                continue

            # 5. Check structural conditions (Isomorphism)
            # The edge E connects two vertices, say v1 and v2.
            # We need to check if there exists a "neighboring structure" that has already split this connection.
            # Specifically, we look for a path v1 - E_new - v3 - E_new - v2
            # where v3 is the "hanging node" (midpoint) created by the neighbor.

            vertices = graph.get_hyperedge_vertices(hyperedge_obj.uid)
            if len(vertices) != 2:
                # Malformed edge E, should have exactly 2 vertices
                continue

            v1, v2 = vertices[0], vertices[1]

            # Look for a common neighbor v3 that is connected to both v1 and v2 via 'E' edges
            # AND those 'E' edges are NOT the current hyper_edge_obj.

            matching_neighbor_found = False

            # Get neighbors of v1
            v1_neighbors = graph.get_neighbors(v1.uid)

            for v3 in v1_neighbors:
                if v3.uid == v2.uid:
                    continue  # This is just v2, skipping

                # Check if v3 is connected to v2
                v3_neighbors = graph.get_neighbors(v3.uid)
                # Note: get_neighbors returns Vertex objects. We need to check if v2 is in this list.
                # However, Vertex objects equality depends on implementation. Best to check UIDs.
                if not any(n.uid == v2.uid for n in v3_neighbors):
                    continue

                # Now we have v1 -- v3 -- v2 connectivity.
                # We need to check the TYPE of connections.
                # Is v1 connected to v3 via an 'E' edge?
                edges_v1_v3 = graph.get_hyperedges_between_vertices(v1.uid, v3.uid)
                has_E_v1_v3 = any(h.label == "E" for h in edges_v1_v3)

                if not has_E_v1_v3:
                    continue

                # Is v3 connected to v2 via an 'E' edge?
                edges_v3_v2 = graph.get_hyperedges_between_vertices(v3.uid, v2.uid)
                has_E_v3_v2 = any(h.label == "E" for h in edges_v3_v2)

                if not has_E_v3_v2:
                    continue

                # If we found such a v3, then this E(v1, v2) is eligible for P2.
                # We interpret this structure as: the neighbor has already split the edge.
                matching_neighbor_found = True
                break

            if matching_neighbor_found:
                candidates.append(hyperedge_obj)

        return candidates

    def apply_rhs(self, graph: Graph, match: Hyperedge):
        """
        Replaces the matched edge E(v1, v2) with two new edges E(v1, v3) and E(v3, v2),
        where v3 is the existing 'hanging node' found in find_lhs.
        Updates R attributes to 0.
        """
        # 1. Identify v1, v2, and v3 again
        vertices = graph.get_hyperedge_vertices(match.uid)
        if len(vertices) != 2:
            return  # Safety check

        v1, v2 = vertices[0], vertices[1]

        # We need to find v3 again (the implementation in find_lhs didn't return it,
        # but it's cheap to find again).
        # Ideally find_lhs could return a tuple/object with matches, but adhering to the interface List[Hyperedge].

        v3 = None
        v1_neighbors = graph.get_neighbors(v1.uid)
        for cand_v in v1_neighbors:
            if cand_v.uid == v2.uid:
                continue

            # Check v2 connection
            cand_v_neighbors = graph.get_neighbors(cand_v.uid)
            if not any(n.uid == v2.uid for n in cand_v_neighbors):
                continue

            # Check edge types
            edges_v1_c = graph.get_hyperedges_between_vertices(v1.uid, cand_v.uid)
            if not any(h.label == "E" for h in edges_v1_c):
                continue

            edges_c_v2 = graph.get_hyperedges_between_vertices(cand_v.uid, v2.uid)
            if not any(h.label == "E" for h in edges_c_v2):
                continue

            # Found it
            v3 = cand_v
            break

        if v3 is None:
            # Should not happen if apply_rhs is called on a valid match
            print(f"[P2] Error: Could not find hanging node v3 for edge {match.uid}")
            return

        # 2. Create two new E hyperedges
        # Properties: label='E', r=0, b=0 (since matched edge was b=0)
        # We assume b=0 for the new edges because they are internal parts of the split.

        h1_uid = graph.get_hyperedges_between_vertices(v1.uid, v3.uid)[0].uid
        h2_uid = graph.get_hyperedges_between_vertices(v2.uid, v3.uid)[0].uid
        max_edge_id = max(
            [
                int(re.search(r"\d+", node_id).group())
                for node_id, data in graph._nx_graph.nodes(data=True)
                if isinstance(data.get("data"), Hyperedge)
                and str(node_id).startswith("E")
            ],
            default=0,
        )
        edge1_id = f"E{max_edge_id + 1}"
        edge2_id = f"E{max_edge_id + 2}"

        new_h1 = Hyperedge(uid=edge1_id, label="E", r=0, b=0)
        new_h2 = Hyperedge(uid=edge2_id, label="E", r=0, b=0)

        graph.add_hyperedge(new_h1)
        graph.add_hyperedge(new_h2)

        # 3. Connect new edges
        # E1 connects v1 and v3
        graph.connect(new_h1.uid, v1.uid)
        graph.connect(new_h1.uid, v3.uid)

        # E2 connects v3 and v2
        graph.connect(new_h2.uid, v3.uid)
        graph.connect(new_h2.uid, v2.uid)

        # 4. Remove the old hyperedge match
        # We need to remove the node from the graph.
        # graph.remove_node handles removing edges connected to it too.
        graph.remove_node(match.uid)
        # graph.remove_node(v3.uid)
        # graph.remove_node(h1_uid)
        # graph.remove_node(h2_uid)

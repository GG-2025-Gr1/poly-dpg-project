from typing import List, Optional, Any

from ..graph import Graph
from ..elements import Hyperedge
from .production import Production


class ProductionP6(Production):
    """
    P6: Marking Pentagonal Elements (Marking).
    Targets a hyperedge labeled 'P' (Pentagon).
    Changes the interior refinement attribute R from 0 to 1.
    Preconditions: R=0, Refinement Criterion (RFC) met. (RFC assumed true)
    """

    def find_lhs(
        self, graph: Graph, target_id: Optional[str | int] = None
    ) -> List[Hyperedge]:
        candidates: List[Hyperedge] = []

        # Iterate over all nodes in the graph
        for _, data in graph._nx_graph.nodes(data=True):
            hyperedge_obj = data.get("data")
            
            # 1. Must be a Hyperedge
            if not isinstance(hyperedge_obj, Hyperedge):
                continue
                
            # Optional target filter
            if target_id is not None and hyperedge_obj.uid != target_id:
                continue

            # 2. Label must be 'P' (Pentagon)
            if hyperedge_obj.label != "P":
                continue

            # 3. Must be unrefined (R=0)
            if hyperedge_obj.r != 0:
                continue

            # 4. Check connectivity (Must be a pentagon - 5 vertices)
            # This is technically implicit in label 'P', but good to verify structure.
            vertices = graph.get_hyperedge_vertices(hyperedge_obj.uid)
            if len(vertices) != 5:
                # Malformed P hyperedge
                continue

            # RFC check is assumed True for now (or passed via kwargs if implemented)
            candidates.append(hyperedge_obj)

        return candidates

    def apply_rhs(self, graph: Graph, match: Hyperedge):
        """
        Marks the pentagon for refinement (R=1).
        """
        # Simply update the hyperedge attribute R
        # Use update_hyperedge for graph-consistent update if needed, or direct object update
        # Using graph method is safer for consistency
        
        graph.update_hyperedge(match.uid, r=1)

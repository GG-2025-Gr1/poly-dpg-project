from typing import List, Optional, Any

from ..graph import Graph
from ..elements import Hyperedge
from .production import Production


class ProductionP12(Production):
    """
    P12: Marking Septagonal Elements (Marking).
    Targets a hyperedge labeled 'T' (Septagon ? - assuming T stands for something with 7 vertices or 'T'ype 7).
    User description: "Production P12 marks an element for refinement"
    Context implies this follows P9 (Hex) series, so likely for 7-gon.
    Changes the interior refinement attribute R from 0 to 1.
    """

    def find_lhs(
        self, graph: Graph, target_id: Optional[str | int] = None
    ) -> List[Hyperedge]:
        candidates: List[Hyperedge] = []

        for _, data in graph._nx_graph.nodes(data=True):
            hyperedge_obj = data.get("data")
            
            if not isinstance(hyperedge_obj, Hyperedge):
                continue
                
            if target_id is not None and hyperedge_obj.uid != target_id:
                continue

            # Label must be 'T' (Septagon/Triangle? Assuming Septagon based on P13/P14 context)
            if hyperedge_obj.label != "T":
                continue

            # Must be unrefined (R=0)
            if hyperedge_obj.r != 0:
                continue

            vertices = graph.get_hyperedge_vertices(hyperedge_obj.uid)
            if len(vertices) != 7:
                # Malformed T hyperedge
                continue

            candidates.append(hyperedge_obj)

        return candidates

    def apply_rhs(self, graph: Graph, match: Hyperedge):
        """
        Marks the septagon for refinement (R=1).
        """
        graph.update_hyperedge(match.uid, r=1)
        print(f"-> P12: Oznaczono element T {match.uid} (R=1).")

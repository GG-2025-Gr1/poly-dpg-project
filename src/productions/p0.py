from typing import List, Union

from .production import Production
from ..graph import Graph
from ..elements import Hyperedge


class ProductionP0(Production):
    """
    P0: Oznaczenie elementu do refiniacji.
    Ustawia R=1 dla węzła typu Q, jeśli R było 0.
    """

    def find_lhs(
        self, graph: Graph, target_id: Union[int, str] = None
    ) -> List[Hyperedge]:
        # P0 jest selektywne - wymaga podania ID
        if target_id is None:
            return []

        node = graph.get_node(target_id)

        # Sprawdzamy, czy to odpowiedni typ i czy spełnia warunki (LHS)
        if isinstance(node, Hyperedge):
            if node.label == "Q" and node.r == 0:
                return [node]  # Zwracamy LISTĘ zawierającą ten obiekt

        return []

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        # RHS: Zmieniamy R na 1

        # 1. Aktualizacja obiektu Pythonowego (logika biznesowa)
        match_node.r = 1

        # 2. Aktualizacja wewnętrznego grafu NetworkX (dla wizualizacji i spójności)
        # Odwołujemy się do graph.nx_graph, bo klasa Graph to wrapper
        if match_node.uid in graph.nx_graph.nodes:
            graph.nx_graph.nodes[match_node.uid]["R"] = 1

        print(f"-> P0: Oznaczono element {match_node.uid} do podziału (R=1).")

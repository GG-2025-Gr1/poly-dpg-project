from abc import ABC, abstractmethod
from typing import List, Any
from graph import Graph  # Importujemy Twoją klasę Graph, nie networkx bezpośrednio

class Production(ABC):
    """
    Klasa bazowa realizująca wzorzec Template Method.
    Oddziela sprawdzanie dopasowania (LHS) od wykonania zmian (RHS).
    """

    def apply(self, graph: Graph, *args, **kwargs) -> Graph:
        """
        Metoda szablonowa.
        Przyjmuje *args i **kwargs, aby przekazać np. target_id do P0.
        """
        
        # 1. Znajdź wszystkie wystąpienia lewej strony (LHS)
        matches = self.find_lhs(graph, *args, **kwargs)
        
        if not matches:
            # To nie jest błąd - po prostu brak dopasowań w tej chwili
            return graph

        print(f"[{self.__class__.__name__}] Znaleziono {len(matches)} dopasowań. Aplikuję RHS.")

        # 2. Dla każdego dopasowania zastosuj prawą stronę (RHS)
        for match in matches:
            self.apply_rhs(graph, match)
            
        return graph

    @abstractmethod
    def find_lhs(self, graph: Graph, *args, **kwargs) -> List[Any]:
        """
        Zwraca listę dopasowań.
        Dla P0: lista jednoelementowa [Hyperedge] lub pusta [].
        Dla P1: lista wielu Hyperedge lub krawędzi.
        """
        pass

    @abstractmethod
    def apply_rhs(self, graph: Graph, match: Any):
        """
        Modyfikuje graf, przekształcając dopasowany fragment LHS w RHS.
        """
        pass
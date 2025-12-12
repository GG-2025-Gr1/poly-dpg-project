from abc import ABC, abstractmethod
from typing import List, Any

from ..graph import Graph


class Production(ABC):
    def apply(self, graph: Graph, *args, **kwargs) -> Graph:
        """
        Metoda szablonowa.
        Przyjmuje *args i **kwargs, aby przekazać np. target_id do P0.
        """

        # 1. Znajdź wszystkie wystąpienia lewej strony (LHS)
        matches = self.find_lhs(graph, *args, **kwargs)

        if not matches:
            return graph

        print(
            f"[{self.__class__.__name__}] Znaleziono {len(matches)} dopasowań. Aplikuję RHS."
        )

        # 2. Dla każdego dopasowania zastosuj prawą stronę (RHS)
        for match in matches:
            self.apply_rhs(graph, match)

        return graph

    @abstractmethod
    def find_lhs(self, graph: Graph, *args, **kwargs) -> List[Any]:
        """
        Zwraca listę dopasowań.
        """
        pass

    @abstractmethod
    def apply_rhs(self, graph: Graph, match: Any):
        """
        Modyfikuje graf, przekształcając dopasowany fragment LHS w RHS.
        """
        pass

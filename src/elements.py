from dataclasses import dataclass
from typing import Union


@dataclass
class Vertex:
    """
    Reprezentuje geometryczny wierzchołek 2D (x, y).
    """

    uid: Union[int, str]
    x: float
    y: float
    hanging: bool = False  # Czy węzeł jest wiszący (hanging node)

    def __post_init__(self):
        # Obejście dla dataclass, aby uid był dostępny (jeśli używamy go poza NetworkX)
        pass

    def __repr__(self):
        return f"V(id={self.uid}, x={self.x}, y={self.y}, h={self.hanging})"

    def __hash__(self):
        return hash(self.uid)


@dataclass
class Hyperedge:
    """
    Reprezentuje element logiczny: Wnętrze (Q, P, S) lub Krawędź (E).
    """

    uid: Union[int, str]
    label: str  # 'Q', 'E', 'P', 'S'
    r: int = 0  # Refinement flag (0 lub 1)
    b: int = 0  # Boundary flag (0 lub 1)

    def __repr__(self):
        return f"{self.label}(id={self.uid}, R={self.r}, B={self.b})"

    def __hash__(self):
        return hash(self.uid)

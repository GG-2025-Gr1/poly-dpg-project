from src.productions.p0 import ProductionP0
from src.utils.visualization import visualize_graph

from tests.graphs import get_2x2_grid_graph


if __name__ == "__main__":
    print("=== START SYMULACJI SIATKI 2x2 ===")

    # 1. Inicjalizacja siatki 2x2
    graph = get_2x2_grid_graph()
    visualize_graph(
        graph,
        "Siatka 2x2 - Stan Poczatkowy",
        filepath="tests/test_p0/a/grid_initial.png",
    )

    # 2. Wykonanie Produkcji P0 na lewym górnym elemencie (Q3)
    # Zgodnie z obrazkiem, chcemy oznaczyć jeden konkretny element.
    p0 = ProductionP0()

    print("\n--- Aplikacja P0 na elemencie Q3 (Lewy-Górny) ---")
    graph = p0.apply(graph)

    # 3. Wizualizacja wyniku
    # Spodziewany efekt: Q3 ma R=1, reszta (Q1, Q2, Q4) ma R=0
    visualize_graph(
        graph, "Siatka 2x2 - Po P0 na Q3", filepath="tests/test_p0/a/grid_after_p0.png"
    )

    print("\n=== KONIEC SYMULACJI ===")

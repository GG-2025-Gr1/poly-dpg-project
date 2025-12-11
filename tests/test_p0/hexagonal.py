from src.productions.p0 import ProductionP0
from src.utils.visualization import visualize_graph

from tests.graphs import get_hexagonal_test_graph


if __name__ == "__main__":
    print("=== TEST WIZUALIZACJI SZEŚCIOKĄTA JAKO Q ===")

    # 1. Inicjalizacja
    graph = get_hexagonal_test_graph()

    # Wizualizacja powinna umieścić czerwone Q idealnie w środku okręgu
    visualize_graph(
        graph,
        "Szesciokat jako Q - Przed P0",
        filepath="tests/test_p0/b/test_hex_Q_init.png",
    )

    # 2. Wykonanie Produkcji P0
    # P0 szuka 'Q' z R=0. Nasz sześciokąt spełnia te warunki.
    p0 = ProductionP0()

    print("\n--- Aplikacja P0 na elemencie Q1 ---")
    graph = p0.apply(graph, target_id="Q1")

    # TODO:
    # We expect that the P0 was not applied because the Q is connected to 6 vertices, not 4.

    # 3. Wynik
    # Oczekujemy, że czerwone Q w środku sześciokąta zmieni opis na R=1
    visualize_graph(
        graph,
        "Szesciokat jako Q - Po P0",
        filepath="tests/test_p0/b/test_hex_Q_result.png",
    )

    print("\n=== KONIEC TESTU ===")

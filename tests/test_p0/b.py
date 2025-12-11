import math

from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p0 import ProductionP0  # Używamy standardowego P0
from src.utils.visualization import visualize_graph


def get_hexagonal_test_graph():
    """
    Tworzy geometrię sześciokąta, ale środek nazywa 'Q'.
    Służy do testowania wizualizacji i mechanizmu P0.
    """
    g = Graph()

    # --- 1. Geometria (6 wierzchołków na okręgu) ---
    radius = 2.0
    center_x, center_y = 3.0, 3.0  # Przesunięcie środka

    vertices_ids = [1, 2, 3, 4, 5, 6]

    for i, vid in enumerate(vertices_ids):
        # Kąt co 60 stopni
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)

        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)

        # Tworzymy wierzchołki geometryczne
        g.add_vertex(Vertex(uid=vid, x=round(x, 2), y=round(y, 2)))

    # --- 2. Krawędzie (E) ---
    # Łączymy w pętlę 1-2-3-4-5-6-1
    for i in range(len(vertices_ids)):
        curr_v = vertices_ids[i]
        next_v = vertices_ids[(i + 1) % len(vertices_ids)]

        eid = f"E{i + 1}"
        # Tworzymy krawędzie (zielone kwadraty w wizualizacji)
        g.add_hyperedge(Hyperedge(uid=eid, label="E", r=0, b=1))
        g.connect(eid, curr_v)
        g.connect(eid, next_v)

    # --- 3. Wnętrze (Q) - TEST ---
    # Tutaj robimy "oszustwo" dla testu.
    # Geometrycznie to sześciokąt, ale logicznie dajemy label='Q'.
    # Dzięki temu wizualizacja pokaże czerwony kwadrat, a P0 zadziała.
    q_id = "Q1"
    g.add_hyperedge(Hyperedge(uid=q_id, label="Q", r=0, b=0))

    # Podłączamy Q do wszystkich 6 wierzchołków
    for vid in vertices_ids:
        g.connect(q_id, vid)

    return g


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

    # 3. Wynik
    # Oczekujemy, że czerwone Q w środku sześciokąta zmieni opis na R=1
    visualize_graph(
        graph,
        "Szesciokat jako Q - Po P0",
        filepath="tests/test_p0/b/test_hex_Q_result.png",
    )

    print("\n=== KONIEC TESTU ===")

from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p0 import ProductionP0
from src.utils.visualization import visualize_graph


def get_2x2_grid_graph():
    """
    Tworzy siatkę 2x2 elementy (4 czworokąty), zgodną z przesłanym obrazkiem.

    Układ wierzchołków (ID):
    7 -- 8 -- 9  (y=2.0)
    | Q3 | Q4 |
    4 -- 5 -- 6  (y=1.0)
    | Q1 | Q2 |
    1 -- 2 -- 3  (y=0.0)
    """
    g = Graph()

    # --- 1. Wierzchołki (Vertex) ---
    # Generujemy 9 wierzchołków w siatce 3x3 punkty
    vertices_data = [
        (1, 0.0, 0.0),
        (2, 1.0, 0.0),
        (3, 2.0, 0.0),  # Rząd dolny
        (4, 0.0, 1.0),
        (5, 1.0, 1.0),
        (6, 2.0, 1.0),  # Rząd środkowy
        (7, 0.0, 2.0),
        (8, 1.0, 2.0),
        (9, 2.0, 2.0),  # Rząd górny
    ]

    for uid, x, y in vertices_data:
        g.add_vertex(Vertex(uid=uid, x=x, y=y))

    # --- 2. Elementy Wnętrza (Q) ---
    # Definiujemy 4 elementy. Lewy-górny to Q3.
    # Atrybut R=0 na starcie.
    quads = [
        Hyperedge(uid="Q1", label="Q", r=0, b=0),  # Lewy-dół
        Hyperedge(uid="Q2", label="Q", r=0, b=0),  # Prawy-dół
        Hyperedge(uid="Q3", label="Q", r=0, b=0),  # Lewy-góra (TARGET)
        Hyperedge(uid="Q4", label="Q", r=0, b=0),  # Prawy-góra
    ]
    for q in quads:
        g.add_hyperedge(q)

    # Definicja połączeń Q z wierzchołkami (kolejność zazwyczaj przeciwna do ruchu wskazówek zegara lub zgodna)
    q_conns = {
        "Q1": [1, 2, 5, 4],
        "Q2": [2, 3, 6, 5],
        "Q3": [4, 5, 8, 7],  # To jest element, który chcemy oznaczyć
        "Q4": [5, 6, 9, 8],
    }
    for q_uid, v_ids in q_conns.items():
        for v_id in v_ids:
            g.connect(q_uid, v_id)

    # --- 3. Krawędzie (E) ---
    # Dodajemy krawędzie, aby graf był kompletny (ważne: krawędzie wewnętrzne są współdzielone!)
    # Format: (ID, v1, v2, Boundary_Flag)
    edges_data = [
        # Zewnętrzne (Boundary B=1)
        ("E1", 1, 2, 1),
        ("E2", 2, 3, 1),  # Dół
        ("E3", 3, 6, 1),
        ("E4", 6, 9, 1),  # Prawa
        ("E5", 9, 8, 1),
        ("E6", 8, 7, 1),  # Góra
        ("E7", 7, 4, 1),
        ("E8", 4, 1, 1),  # Lewa
        # Wewnętrzne (Internal B=0) - to są krawędzie współdzielone między Q
        (
            "E9",
            4,
            5,
            0,
        ),  # Pozioma środek (między Q1/Q3 a Q2/Q4 - nie, to między Q1 a Q3)
        ("E10", 5, 6, 0),  # Pozioma środek
        ("E11", 2, 5, 0),  # Pionowa środek
        ("E12", 5, 8, 0),  # Pionowa środek
    ]

    for eid, v1, v2, b_flag in edges_data:
        e = Hyperedge(uid=eid, label="E", r=0, b=b_flag)
        g.add_hyperedge(e)
        g.connect(eid, v1)
        g.connect(eid, v2)

    return g


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
    graph = p0.apply(graph, target_id="Q3")

    # 3. Wizualizacja wyniku
    # Spodziewany efekt: Q3 ma R=1, reszta (Q1, Q2, Q4) ma R=0
    visualize_graph(
        graph, "Siatka 2x2 - Po P0 na Q3", filepath="tests/test_p0/a/grid_after_p0.png"
    )

    print("\n=== KONIEC SYMULACJI ===")

from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p0 import ProductionP0
from src.utils.visualization import visualize_graph


def get_initial_graph():
    """
    Tworzy graf początkowy: jeden czworokąt.
    Struktura zgodna z dokumentacją
    """
    g = Graph()

    # --- 1. Wierzchołki (V) ---
    v1 = Vertex(uid=1, x=0.0, y=0.0)
    v2 = Vertex(uid=2, x=2.0, y=0.0)
    v3 = Vertex(uid=3, x=2.0, y=2.0)
    v4 = Vertex(uid=4, x=0.0, y=2.0)

    for v in [v1, v2, v3, v4]:
        g.add_vertex(v)

    # --- 2. Krawędzie logiczne (E) ---
    # Boundary=1 (bo to pojedynczy element)
    e1 = Hyperedge(uid="E1", label="E", r=0, b=1)  # Dolna
    e2 = Hyperedge(uid="E2", label="E", r=0, b=1)  # Prawa
    e3 = Hyperedge(uid="E3", label="E", r=0, b=1)  # Górna
    e4 = Hyperedge(uid="E4", label="E", r=0, b=1)  # Lewa

    g.add_hyperedge(e1)
    g.connect("E1", 1)
    g.connect("E1", 2)

    g.add_hyperedge(e2)
    g.connect("E2", 2)
    g.connect("E2", 3)

    g.add_hyperedge(e3)
    g.connect("E3", 3)
    g.connect("E3", 4)

    g.add_hyperedge(e4)
    g.connect("E4", 4)
    g.connect("E4", 1)

    # --- 3. Wnętrze (Q) ---
    # To jest cel naszej produkcji P0
    q1 = Hyperedge(uid="Q1", label="Q", r=0, b=0)
    g.add_hyperedge(q1)

    # Q połączone z wierzchołkami narożnymi
    for vid in [1, 2, 3, 4]:
        g.connect("Q1", vid)

    return g


if __name__ == "__main__":
    print("=== START SYMULACJI ===")

    # 1. Inicjalizacja
    graph = get_initial_graph()
    visualize_graph(graph, "Stan poczatkowy (R=0)", filepath="step_0_init.png")

    # 2. Wykonanie Produkcji P0
    # Decyzja: chcemy podzielić element 'Q1'
    p0 = ProductionP0()

    print("\n--- Aplikacja P0 ---")
    graph = p0.apply(graph)

    # 3. Wizualizacja wyniku
    # Oczekujemy, że w pliku png przy Q zobaczymy R=1
    visualize_graph(graph, "Po produkcji P0 (R=1)", filepath="step_1_after_p0.png")

    print("\n=== KONIEC SYMULACJI ===")

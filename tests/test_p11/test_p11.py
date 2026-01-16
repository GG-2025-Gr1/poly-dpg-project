import pytest
from src.productions.p11 import ProductionP11
from src.graph import Graph
from src.elements import Vertex, Hyperedge

# Używamy Twojej funkcji z projektu:
from src.utils.visualization import visualize_graph
import matplotlib

matplotlib.use("Agg")

# --- KONFIGURACJA ---
VIS_DIR = "tests/test_p11"


def create_base_graph():
    """Tworzy poprawny graf wejściowy dla P11 (LHS)."""
    graph = Graph()

    # Narożniki
    v = [
        Vertex(1, 4, 0),
        Vertex(2, 10, 0),
        Vertex(3, 10, 8),
        Vertex(4, 4, 8),
        Vertex(5, 14, 4),
        Vertex(6, 0, 4),
    ]

    # Midpoints (wiszące)
    m = [
        Vertex(7, 7, 0, hanging=True),
        Vertex(8, 2, 2, hanging=True),
        Vertex(9, 2, 6, hanging=True),
        Vertex(10, 7, 8, hanging=True),
        Vertex(11, 12, 6, hanging=True),
        Vertex(12, 12, 2, hanging=True),
    ]

    for x in v:
        graph.add_vertex(x)

    for x in m:
        graph.add_vertex(x)

    # Element Q (R=1)
    q = Hyperedge("Q1", "Q", r=1, b=0)
    graph.add_hyperedge(q)
    for i in range(1, 7):
        graph.connect("Q1", i)

    # Krawędzie obwodu (niezbędne dla P11)
    edges = [
        ("E1a", 1, 7),
        ("E1b", 7, 2),
        ("E2a", 2, 12),
        ("E2b", 12, 5),
        ("E3a", 5, 11),
        ("E3b", 11, 3),
        ("E4a", 3, 10),
        ("E4b", 10, 4),
        ("E5a", 4, 9),
        ("E5b", 9, 6),
        ("E6a", 6, 8),
        ("E6b", 8, 1),
    ]
    for e, u, v in edges:
        graph.add_hyperedge(Hyperedge(e, "E", 0, 1))
        graph.connect(e, u)
        graph.connect(e, v)

    return graph


# === SCENARIUSZ 1: STANDARDOWE WYKONANIE ===
def test_vis_standard_execution():
    """Generuje obrazki dla poprawnego wykonania produkcji."""
    graph = create_base_graph()

    # 1. Przed
    visualize_graph(graph, "P11: LHS (Standard)", f"{VIS_DIR}/scenariusz1_przed.png")

    # 2. Wykonanie
    p11 = ProductionP11()
    p11.apply(graph)

    # 3. Po
    visualize_graph(graph, "P11: RHS (Standard)", f"{VIS_DIR}/scenariusz1_po.png")


# === SCENARIUSZ 2: GRAF JAKO PODGRAF (Izomorfizm) ===
def test_vis_subgraph_execution():
    """Generuje obrazki, gdy element jest częścią większego grafu."""
    graph = create_base_graph()

    # Dodajemy "niezwiązane" elementy (sztuczny tłum)
    graph.add_vertex(Vertex(99, 20, 20))  # Daleko
    graph.add_hyperedge(Hyperedge("E_extra", "E", 0, 1))
    graph.connect("E_extra", 99)

    # 1. Przed
    visualize_graph(
        graph, "P11: LHS (Podgraf)", f"{VIS_DIR}/scenariusz2_podgraf_przed.png"
    )

    p11 = ProductionP11()
    p11.apply(graph)

    # 2. Po (Sprawdzamy czy węzeł 99 nadal tam jest)
    visualize_graph(
        graph, "P11: RHS (Podgraf)", f"{VIS_DIR}/scenariusz2_podgraf_po.png"
    )


# === SCENARIUSZ 3: BŁĄD - BRAK WIERZCHOŁKA ===
def test_vis_error_missing_vertex():
    """Generuje obrazek niepoprawnego grafu (brak jednego mid-pointa)."""
    graph = create_base_graph()

    # Usuwamy wierzchołek nr 10 (u góry po środku)
    # Uwaga: remove_node w NetworkX usuwa też przyległe krawędzie
    graph.remove_node(10)

    visualize_graph(
        graph,
        "P11 Error: Brak wierzcholka 10",
        f"{VIS_DIR}/scenariusz3_error_brak_v.png",
    )

    # Próba wykonania (nie powinna nic zmienić)
    p11 = ProductionP11()
    matches = p11.find_lhs(graph)
    assert len(matches) == 0  # Upewniamy się w teście, że nie działa


# === SCENARIUSZ 4: BŁĄD - BRAK KRAWĘDZI (Broken Edge) ===
def test_vis_error_missing_edge():
    """Generuje obrazek, gdzie krawędź nie jest 'połamana' (brak węzła w środku)."""
    graph = create_base_graph()

    # Usuwamy całą dolną strukturę (E-M-E) i wstawiamy jedną krawędź bezpośrednią
    # To symuluje sytuację, gdzie bok NIE został wcześniej podzielony przez P3
    graph.remove_node(7)  # Usuwamy midpoint
    graph.remove_node("E1a")  # Usuwamy małe krawędzie
    graph.remove_node("E1b")

    # Dodajemy "całą" krawędź między 1 a 2
    graph.add_hyperedge(Hyperedge("E_whole", "E", 0, 1))
    graph.connect("E_whole", 1)
    graph.connect("E_whole", 2)

    visualize_graph(
        graph,
        "P11 Error: Bok niepodzielony",
        f"{VIS_DIR}/scenariusz4_error_caly_bok.png",
    )

    p11 = ProductionP11()
    matches = p11.find_lhs(graph)
    assert len(matches) == 0


# === SCENARIUSZ 5: BŁĄD - ZŁA ETYKIETA ===
def test_vis_error_wrong_attribute():
    """Generuje obrazek grafu z błędnym atrybutem (R=0 zamiast R=1)."""
    graph = create_base_graph()

    # Psujemy atrybut R
    graph.update_hyperedge("Q1", label="S")

    visualize_graph(
        graph,
        "P11 Error: Q ma etykietę S",
        f"{VIS_DIR}/scenariusz5_error_zla_etykieta.png",
    )

    p11 = ProductionP11()
    matches = p11.find_lhs(graph)
    assert len(matches) == 0


# === SCENARIUSZ 6: WIELE DOPASOWAŃ (Double Match) ===
def test_vis_multiple_matches():
    """
    Tworzy graf z DWOMA niezależnymi elementami gotowymi do podziału.
    Sprawdza, czy produkcja wykona się dla obu miejsc.
    """

    # --- Pierwszy sześciokąt (dolny) ---
    graph = create_base_graph()

    # --- Drugi sześciokąt (górny) ---
    # Narożniki
    v = [
        Vertex(13, 0, 12),
        Vertex(14, 4, 16),
        Vertex(15, 10, 16),
        Vertex(16, 14, 12),
    ]

    # Midpoints (wiszące)
    m = [
        Vertex(17, 2, 10, hanging=True),
        Vertex(18, 2, 14, hanging=True),
        Vertex(19, 7, 16, hanging=True),
        Vertex(20, 12, 14, hanging=True),
        Vertex(21, 12, 10, hanging=True),
    ]

    for x in v:
        graph.add_vertex(x)

    for x in m:
        graph.add_vertex(x)

    # Element Q (R=1)
    q = Hyperedge("Q2", "Q", r=1, b=0)
    graph.add_hyperedge(q)
    for i in [3, 4, 13, 14, 15, 16]:
        graph.connect("Q2", i)

    # Krawędzie obwodu (niezbędne dla P11)
    edges = [
        ("E7a", 4, 17),
        ("E7b", 17, 13),
        ("E8a", 13, 18),
        ("E8b", 18, 14),
        ("E9a", 14, 19),
        ("E9b", 19, 15),
        ("E10a", 15, 20),
        ("E10b", 20, 16),
        ("E11a", 16, 21),
        ("E11b", 21, 3),
    ]
    for e, u, v in edges:
        graph.add_hyperedge(Hyperedge(e, "E", 0, 1))
        graph.connect(e, u)
        graph.connect(e, v)

    visualize_graph(
        graph, "P11: LHS (Dwa sześciokąty)", f"{VIS_DIR}/scenariusz6_multi_przed.png"
    )

    p11 = ProductionP11()
    matches = p11.find_lhs(graph)
    assert len(matches) == 2, f"Powinien znaleźć 2 dopasowania, znalazł {len(matches)}"

    p11.apply(graph)

    visualize_graph(
        graph, "P11: RHS (Dwa sześciokąty)", f"{VIS_DIR}/scenariusz6_multi_po.png"
    )

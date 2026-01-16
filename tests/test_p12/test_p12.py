from src.productions.p12 import ProductionP12
from tests.graphs import get_hexagonal_graph_marked
from src.utils.visualization import visualize_graph
from src.elements import Hyperedge, Vertex
from src.graph import Graph
import matplotlib

matplotlib.use("Agg")

# --- KONFIGURACJA ---
VIS_DIR = "tests/test_p12"


def create_base_graph():
    """Tworzy poprawny graf wejściowy dla P12 (LHS)."""
    graph = Graph()

    # Narożniki
    v = [
        Vertex(1, 2, 0),
        Vertex(2, 0, 3),
        Vertex(3, 3, 6),
        Vertex(4, 9, 6),
        Vertex(5, 12, 3),
        Vertex(6, 10, 0),
        Vertex(7, 6, 0),
    ]

    for x in v:
        graph.add_vertex(x)

    # Element Q (R=1)
    q = Hyperedge("Q1", "Q", r=0, b=0)
    graph.add_hyperedge(q)
    for i in range(1, 8):
        graph.connect("Q1", i)

    # Krawędzie obwodu (niezbędne dla P11)
    edges = [
        ("E1", 1, 2),
        ("E2", 2, 3),
        ("E3", 3, 4),
        ("E4", 4, 5),
        ("E5", 5, 6),
        ("E6", 6, 7),
        ("E7", 7, 1),
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
    visualize_graph(graph, "P12: LHS (Standard)", f"{VIS_DIR}/scenariusz1_przed.png")

    assert graph.get_hyperedge("Q1").r == 0

    # 2. Wykonanie
    p12 = ProductionP12()
    p12.apply(graph)

    assert graph.get_hyperedge("Q1").r == 1

    # 3. Po
    visualize_graph(graph, "P12: RHS (Standard)", f"{VIS_DIR}/scenariusz1_po.png")


# === SCENARIUSZ 2: BŁĘDNA WARTOŚĆ R ===
def test_vis_bad_r_value():
    """Generuje obrazek niepoprawnergo grafu (zła wartość R dla wierzchołka Q)"""
    graph = create_base_graph()
    graph.update_hyperedge("Q1", r=2)

    # 1. Przed
    visualize_graph(
        graph, "P12: LHS (Błędna etykieta)", f"{VIS_DIR}/scenariusz2_przed.png"
    )

    # 2. Wykonanie
    p12 = ProductionP12()
    p12.apply(graph)

    assert graph.get_hyperedge("Q1").r != 1


# === SCENARIUSZ 3: GRAF JAKO PODGRAF (Izomorfizm) ===
def test_vis_subgraph_execution():
    """Generuje obrazki, gdy element jest częścią większego grafu."""
    graph = create_base_graph()

    # Dodajemy "niezwiązane" elementy (sztuczny tłum)
    graph.add_vertex(Vertex(99, 20, 20))  # Daleko
    graph.add_hyperedge(Hyperedge("E_extra", "E", 0, 1))
    graph.connect("E_extra", 99)

    # 1. Przed
    visualize_graph(
        graph, "P12: LHS (Podgraf)", f"{VIS_DIR}/scenariusz3_podgraf_przed.png"
    )

    p12 = ProductionP12()
    p12.apply(graph)

    # 2. Po (Sprawdzamy czy węzeł 99 nadal tam jest)
    visualize_graph(
        graph, "P12: RHS (Podgraf)", f"{VIS_DIR}/scenariusz3_podgraf_po.png"
    )


# === SCENARIUSZ 4: BŁĄD - BRAK WIERZCHOŁKA ===
def test_vis_error_missing_vertex():
    """Generuje obrazek niepoprawnego grafu (brak jednego wierzchołka)."""
    graph = create_base_graph()

    # Usuwamy wierzchołek nr 7 (na dole po środku)
    # Uwaga: remove_node w NetworkX usuwa też przyległe krawędzie
    graph.remove_node(7)
    graph.connect(1, 6)

    visualize_graph(
        graph,
        "P12 Error: Brak wierzcholka 7",
        f"{VIS_DIR}/scenariusz4_error_brak_v.png",
    )

    # Próba wykonania (nie powinna nic zmienić)
    p12 = ProductionP12()
    matches = p12.find_lhs(graph)
    assert len(matches) == 0  # Upewniamy się w teście, że nie działa


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

    p12 = ProductionP12()
    matches = p12.find_lhs(graph)
    assert len(matches) == 0


# === SCENARIUSZ 6: WIELE DOPASOWAŃ (Double Match) ===
def test_vis_multiple_matches():
    """
    Tworzy graf z DWOMA niezależnymi elementami gotowymi do podziału.
    Sprawdza, czy produkcja wykona się dla obu miejsc.
    """

    # --- Pierwszy siedmiokąt (dolny) ---
    graph = create_base_graph()

    # --- Drugi siedmiokąt (górny) ---
    v = [
        Vertex(8, 0, 9),
        Vertex(9, 2, 12),
        Vertex(10, 6, 12),
        Vertex(11, 10, 12),
        Vertex(12, 12, 9),
    ]

    for x in v:
        graph.add_vertex(x)

    q = Hyperedge("Q2", "Q", r=0, b=0)
    graph.add_hyperedge(q)
    for i in [3, 4, 8, 9, 10, 11, 12]:
        graph.connect("Q2", i)

    edges = [
        ("E8", 3, 8),
        ("E9", 8, 9),
        ("E10", 9, 10),
        ("E11", 10, 11),
        ("E12", 11, 12),
        ("E13", 12, 4),
    ]
    for e, u, v in edges:
        graph.add_hyperedge(Hyperedge(e, "E", 0, 1))
        graph.connect(e, u)
        graph.connect(e, v)

    visualize_graph(
        graph, "P12: LHS (Dwa siedmiokąty)", f"{VIS_DIR}/scenariusz6_multi_przed.png"
    )

    p12 = ProductionP12()
    matches = p12.find_lhs(graph)
    assert len(matches) == 2, f"Powinien znaleźć 2 dopasowania, znalazł {len(matches)}"

    p12.apply(graph)

    visualize_graph(
        graph, "P12: RHS (Dwa siedmiokąty)", f"{VIS_DIR}/scenariusz6_multi_po.png"
    )

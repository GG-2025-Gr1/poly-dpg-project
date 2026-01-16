from src.productions.p12 import ProductionP12
from tests.graphs import get_hexagonal_graph_marked
from src.utils.visualization import visualize_graph
from src.elements import Hyperedge, Vertex
from src.graph import Graph
import matplotlib

matplotlib.use("Agg")

VIS_DIR = "tests/test_p12"


def create_base_graph():
    """Tworzy poprawny graf wejściowy dla P12 (LHS)."""
    graph = Graph()

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

    t = Hyperedge("T1", "T", r=0, b=0)
    graph.add_hyperedge(t)
    for i in range(1, 8):
        graph.connect("T1", i)

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


def test_vis_standard_execution():
    """Generuje obrazki dla poprawnego wykonania produkcji."""
    graph = create_base_graph()

    visualize_graph(graph, "P12: LHS (Standard)", f"{VIS_DIR}/scenariusz1_przed.png")

    assert graph.get_hyperedge("T1").r == 0

    p12 = ProductionP12()
    p12.apply(graph)

    assert graph.get_hyperedge("T1").r == 1

    visualize_graph(graph, "P12: RHS (Standard)", f"{VIS_DIR}/scenariusz1_po.png")


def test_vis_bad_r_value():
    """Generuje obrazek niepoprawnergo grafu (zła wartość R dla wierzchołka T)"""
    graph = create_base_graph()
    graph.update_hyperedge("T1", r=2)

    visualize_graph(
        graph, "P12: LHS (Błędna etykieta)", f"{VIS_DIR}/scenariusz2_przed.png"
    )

    p12 = ProductionP12()
    p12.apply(graph)

    assert graph.get_hyperedge("T1").r != 1


def test_vis_error_missing_vertex():
    """Generuje obrazek niepoprawnego grafu (brak jednego wierzchołka)."""
    graph = create_base_graph()

    graph.remove_node(7)
    graph.connect(1, 6)

    visualize_graph(
        graph,
        "P12 Error: Brak wierzcholka 7",
        f"{VIS_DIR}/scenariusz3_error_brak_v.png",
    )

    p12 = ProductionP12()
    matches = p12.find_lhs(graph)
    assert len(matches) == 0


def test_vis_error_wrong_attribute():
    """Generuje obrazek grafu z błędnym atrybutem (R=0 zamiast R=1)."""
    graph = create_base_graph()

    graph.update_hyperedge("T1", label="S")

    visualize_graph(
        graph,
        "P11 Error: T ma etykietę S",
        f"{VIS_DIR}/scenariusz4_error_zla_etykieta.png",
    )

    p12 = ProductionP12()
    matches = p12.find_lhs(graph)
    assert len(matches) == 0


def test_vis_multiple_matches():
    """
    Tworzy graf z DWOMA niezależnymi elementami gotowymi do podziału.
    Sprawdza, czy graf produkcja wykona się gdy graf izomorficzny jest podgrafem innego grafu.
    Sprawdza, czy produkcja wykona się dla obu miejsc.
    """

    graph = create_base_graph()

    v = [
        Vertex(8, 0, 9),
        Vertex(9, 2, 12),
        Vertex(10, 6, 12),
        Vertex(11, 10, 12),
        Vertex(12, 12, 9),
    ]

    for x in v:
        graph.add_vertex(x)

    t = Hyperedge("T2", "T", r=0, b=0)
    graph.add_hyperedge(t)
    for i in [3, 4, 8, 9, 10, 11, 12]:
        graph.connect("T2", i)

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
        graph, "P12: LHS (Dwa siedmiokąty)", f"{VIS_DIR}/scenariusz5_multi_przed.png"
    )

    p12 = ProductionP12()
    matches = p12.find_lhs(graph)
    assert len(matches) == 2, f"Powinien znaleźć 2 dopasowania, znalazł {len(matches)}"

    p12.apply(graph)

    visualize_graph(
        graph, "P12: RHS (Dwa siedmiokąty)", f"{VIS_DIR}/scenariusz5_multi_po.png"
    )

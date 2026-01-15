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
    ]

    for x in v:
        graph.add_vertex(x)

    for x in m:
        graph.add_vertex(x)

    # Element Q (R=1)
    q = Hyperedge("Q1", "Q", r=0, b=0)
    graph.add_hyperedge(q)
    for i in range(1, 7):
        graph.connect("Q1", i)

    # Krawędzie obwodu (niezbędne dla P11)
    edges = [
        ("E1a", 1, 7),
        ("E1b", 7, 2),
        ("E2", 2, 5),
        ("E3", 5, 3),
        ("E4", 3, 4),
        ("E5", 4, 6),
        ("E6", 6, 1),
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
def test_vis_standard_execution():
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


# === SCENARIUSZ 3: BŁĄD - BRAK WIERZCHOŁKA ===
def test_vis_error_missing_vertex():
    """Generuje obrazek niepoprawnego grafu (brak jednego mid-pointa)."""
    graph = create_base_graph()

    # Usuwamy wierzchołek nr 7 (na dole po środku)
    # Uwaga: remove_node w NetworkX usuwa też przyległe krawędzie
    graph.remove_node(7)

    visualize_graph(
        graph,
        "P12 Error: Brak wierzcholka 10",
        f"{VIS_DIR}/scenariusz3_error_brak_v.png",
    )

    # Próba wykonania (nie powinna nic zmienić)
    p12 = ProductionP12()
    matches = p12.find_lhs(graph)
    assert len(matches) == 0  # Upewniamy się w teście, że nie działa


# def get_graph_with_unmarked_element() -> Graph:
#     """
#     Tworzy graf z elementem S (P1) z R=0 (nieoznaczony).
#     """
#     graph = create_base_graph()
#     # Zmieniamy domyślne R=1 na R=0 dla elementu P1 (Label='S')
#     graph.update_hyperedge("P1", r=0)
#     return graph
#
#
# def get_graph_with_marked_element() -> Graph:
#     """
#     Tworzy graf z elementem S (P1) z R=1 (oznaczony).
#     """
#     # get_hexagonal_graph_marked domyślnie tworzy P1 z R=1
#     return get_hexagonal_graph_marked()
#
#
# def test_p12_isomorphism_and_application():
#     """
#     Sprawdza, czy P12 poprawnie znajduje element S z R=0 i ustawia mu R=1.
#     """
#     graph = get_graph_with_unmarked_element()
#
#     visualize_graph(graph, "P12: Przed", filepath="tests/test_p12/before_p12.png")
#
#     p12 = ProductionP12()
#     matches = p12.find_lhs(graph)
#
#     assert len(matches) == 1
#     assert matches[0].uid == "P1"
#
#     graph = p12.apply(graph)
#     visualize_graph(graph, "P12: Po", filepath="tests/test_p12/after_p12.png")
#
#     element_p1 = graph.get_hyperedge("P1")
#     assert element_p1.r == 1, "Element P1 (S) powinien mieć R=1 po zastosowaniu P12"
#
#
# def test_p12_ignored_if_element_is_already_marked_r1():
#     """
#     P12 nie powinna działać na elemencie S (P1), który ma już R=1.
#     """
#     graph = get_graph_with_marked_element()
#
#     p12 = ProductionP12()
#     matches = p12.find_lhs(graph)
#
#     assert len(matches) == 0, "P12 nie powinna znaleźć dopasowania dla elementu z R=1"
#
#
# def test_p12_selects_unmarked_among_many():
#     """
#     Sprawdza, czy P12 wybiera tylko element S z R=0, ignorując elementy S z R=1.
#     """
#     graph = get_graph_with_unmarked_element()
#
#     # Dodajemy S2 (oznaczony R=1)
#     s2 = Hyperedge(uid="S2", label="S", r=1, b=0)
#     graph.add_hyperedge(s2)
#     graph.connect("S2", 1)
#     graph.connect("S2", 2)
#     graph.connect("S2", 3)
#
#     p12 = ProductionP12()
#     matches = p12.find_lhs(graph)
#
#     # Powinno znaleźć tylko P1 (R=0)
#     assert len(matches) == 1
#     assert matches[0].uid == "P1"
#
#     graph = p12.apply(graph)
#     assert graph.get_hyperedge("P1").r == 1
#     assert graph.get_hyperedge("S2").r == 1
#
#
# def test_p12_only_targets_label_s():
#     """
#     P12 powinna dopasowywać tylko element 'S', ignorując inne elementy (np. 'E') z R=0.
#     """
#     graph = get_graph_with_unmarked_element()
#
#     # E1 jest krawędzią (label='E', R=0) w hexagonal_graph_marked
#     edge_e = graph.get_hyperedge("E1")
#     assert edge_e.r == 0
#     assert edge_e.label == "E"
#
#     p12 = ProductionP12()
#     matches = p12.find_lhs(graph)
#
#     # Powinno znaleźć tylko P1 (label='S', R=0)
#     assert len(matches) == 1
#     assert matches[0].uid == "P1"
#     assert matches[0].label == "S"
#
#
# def test_p12_broken_topology_missing_vertex():
#     """
#     P12 nie powinna działać, jeśli element S (P1) nie ma 6 wierzchołków.
#     """
#     graph = get_graph_with_unmarked_element()
#
#     # Odłączamy wierzchołek 6 od P1
#     graph.remove_edge("P1", 6)
#
#     p12 = ProductionP12()
#     matches = p12.find_lhs(graph)
#
#     assert len(matches) == 0, (
#         "P12 powinna zignorować S, który nie jest połączony z 6 wierzchołkami"
#     )
#
#
# def test_p12_broken_topology_wrong_label_r0():
#     """
#     P12 ignoruje element z R=0, który ma poprawną topologię (6 wierzchołków), ale niepoprawną etykietę ('Q').
#     """
#     graph = get_graph_with_unmarked_element()
#
#     # Ustawiamy P1 (S) na R=1, żeby wykluczyć go z dopasowania
#     graph.update_hyperedge("P1", r=1)
#
#     # Tworzymy nowy element Q1 (R=0, 6 wierzchołków)
#     q1 = Hyperedge(uid="Q1", label="Q", r=0, b=0)
#     graph.add_hyperedge(q1)
#
#     # Podłączamy Q1 do 6 wierzchołków (1..6)
#     for vid in range(1, 7):
#         graph.connect("Q1", vid)
#
#     p12 = ProductionP12()
#     matches = p12.find_lhs(graph)
#
#     assert len(matches) == 0, (
#         "P12 powinna zignorować Q1, ponieważ jego label to nie 'S'"
#     )
#
#
# def test_p12_missing_boundary_edge():
#     """
#     P12 nie powinna działać, jeśli brakuje choć jednej krawędzi 'E' na obwodzie.
#     """
#     graph = get_graph_with_unmarked_element()
#
#     # Usuwamy jedną krawędź brzegową (np. E1)
#     graph.remove_node("E1")
#
#     p12 = ProductionP12()
#     matches = p12.find_lhs(graph)
#
#     assert len(matches) == 0, (
#         "P12 nie powinna znaleźć dopasowania, gdy brakuje krawędzi E"
#     )

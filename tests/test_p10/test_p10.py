from src.productions.p10 import ProductionP10
from tests.graphs import get_hexagonal_graph_marked
from src.utils.visualization import visualize_graph


def test_p10_isomorphism_and_application():
    """
    Sprawdza czy P10 poprawnie oznacza krawędzie sześciokąta.
    """
    graph = get_hexagonal_graph_marked()
    visualize_graph(graph, "P10: Przed", filepath="tests/test_p10/before_p10.png")

    p10 = ProductionP10()
    matches = p10.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "P1"

    graph = p10.apply(graph)
    visualize_graph(graph, "P10: Po", filepath="tests/test_p10/after_p10.png")

    # Weryfikacja: Wszystkie 6 krawędzi E1..E6 powinno mieć teraz R=1
    for i in range(1, 7):
        eid = f"E{i}"
        edge = graph.get_hyperedge(eid)
        assert edge.r == 1, f"Krawędź {eid} powinna mieć R=1"


def test_p10_ignored_if_r_is_zero():
    """
    P10 nie powinna ruszać P, który ma R=0.
    """
    graph = get_hexagonal_graph_marked()
    graph.update_hyperedge("P1", r=0)

    p10 = ProductionP10()
    matches = p10.find_lhs(graph)
    assert len(matches) == 0


def test_p10_broken_topology_missing_vertex():
    """
    P10 nie powinna działać, jeśli P nie ma 6 wierzchołków.
    """
    graph = get_hexagonal_graph_marked()
    # Odłączamy wierzchołek 6 od P1
    graph.remove_edge("P1", 6)

    p10 = ProductionP10()
    matches = p10.find_lhs(graph)
    assert len(matches) == 0


def test_p10_broken_topology_missing_edge():
    """
    P10 wymaga, aby wierzchołki P były połączone krawędziami E.
    Usuwamy jedną krawędź E3.
    """
    graph = get_hexagonal_graph_marked()
    # Usuwamy E3
    graph.remove_node("E3")

    p10 = ProductionP10()
    matches = p10.find_lhs(graph)
    # Jeśli brakuje otaczającej krawędzi, produkcja może nie znaleźć pełnego dopasowania
    # Zależnie od implementacji - w mojej sprawdzam len(edges_found) == 6
    assert len(matches) == 0

import pytest
from src.productions.p7 import ProductionP7
from tests.graphs import get_pentagonal_graph_marked_extended, get_pentagonal_graph_marked_simple
from src.utils.visualization import visualize_graph


@pytest.mark.parametrize("graph_func,desc", [
    (get_pentagonal_graph_marked_simple, "simple"),
    (get_pentagonal_graph_marked_extended, "complex"),
])
def test_p7_isomorphism_and_application(graph_func, desc):
    """
    Sprawdza czy P7 poprawnie oznacza krawędzie pięciokąta.
    """
    graph = graph_func()
    visualize_graph(graph, f"P7 ({desc}): Przed", filepath=f"tests/test_p7/before_p7_{desc}.png")

    p7 = ProductionP7()
    matches = p7.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "P1"

    graph = p7.apply(graph)
    visualize_graph(graph, f"P7 ({desc}): Po", filepath=f"tests/test_p7/after_p7_{desc}.png")

    # Weryfikacja: Wszystkie 5 krawędzi E1..E5 powinno mieć teraz R=1
    for i in range(1, 6):
        eid = f"E{i}"
        edge = graph.get_hyperedge(eid)
        assert edge.r == 1, f"Krawędź {eid} powinna mieć R=1"


def test_p7_ignored_if_r_is_zero():
    """
    P7 nie powinna ruszać P, który ma R=0.
    """
    graph = get_pentagonal_graph_marked_extended()
    graph.update_hyperedge("P1", r=0)

    p7 = ProductionP7()
    matches = p7.find_lhs(graph)
    assert len(matches) == 0


def test_p7_broken_topology_missing_vertex():
    """
    P7 nie powinna działać, jeśli P nie ma 5 wierzchołków.
    """
    graph = get_pentagonal_graph_marked_extended()
    # Odłączamy wierzchołek 5 od P1
    graph.remove_edge("P1", 5)

    p7 = ProductionP7()
    matches = p7.find_lhs(graph)
    assert len(matches) == 0


def test_p7_broken_topology_missing_edge():
    """
    P7 wymaga, aby wierzchołki P były połączone krawędziami E.
    Usuwamy jedną krawędź E3.
    """
    graph = get_pentagonal_graph_marked_extended()
    # Usuwamy E3
    graph.remove_node("E3")

    p7 = ProductionP7()
    matches = p7.find_lhs(graph)
    # Jeśli brakuje otaczającej krawędzi, produkcja może nie znaleźć pełnego dopasowania
    # Zależnie od implementacji - w mojej sprawdzam len(edges_found) == 5
    assert len(matches) == 0

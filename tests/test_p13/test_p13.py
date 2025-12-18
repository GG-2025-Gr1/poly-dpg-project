from src.productions.p13 import ProductionP13
from tests.graphs import get_heptagonal_graph_marked
from src.utils.visualization import visualize_graph

def test_p13_isomorphism_and_application():
    """
    Sprawdza czy P13 poprawnie oznacza krawędzie siedmiokąta.
    """
    graph = get_heptagonal_graph_marked()
    visualize_graph(graph, "P13: Przed", filepath="tests/test_p13/before_p13.png")

    p13 = ProductionP13()
    matches = p13.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "T"

    graph = p13.apply(graph)
    visualize_graph(graph, "P13: Po", filepath="tests/test_p13/after_p13.png")

    # Weryfikacja: Wszystkie 7 krawędzi E1..E7 powinno mieć teraz R=1
    for i in range(1, 8):
        eid = f"E{i}"
        edge = graph.get_hyperedge(eid)
        assert edge.r == 1, f"Krawędź {eid} powinna mieć R=1"
        
def test_p13_ignored_if_r_is_zero():
    """
    P13 nie powinna ruszać T, który ma R=0.
    """
    graph = get_heptagonal_graph_marked()
    graph.update_hyperedge("T", r=0)

    p13 = ProductionP13()
    matches = p13.find_lhs(graph)
    assert len(matches) == 0
    
def test_p13_broken_topology_missing_vertex():
    """
    P13 nie powinna działać, jeśli T nie ma 7 wierzchołków.
    """
    graph = get_heptagonal_graph_marked()
    # Odłączamy wierzchołek 7 od T1
    graph.remove_edge("T", 7)

    p13 = ProductionP13()
    matches = p13.find_lhs(graph)
    assert len(matches) == 0
    
def test_p13_broken_topology_missing_edge():
    """
    P13 wymaga, aby wierzchołki T były połączone krawędziami E.
    Usuwamy jedną krawędź E3.
    """
    graph = get_heptagonal_graph_marked()
    # Usuwamy E3
    graph.remove_node("E3")

    p13 = ProductionP13()
    matches = p13.find_lhs(graph)
    assert len(matches) == 0
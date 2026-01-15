from src.elements import Hyperedge, Vertex
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
    visualize_graph(graph, "P13: Przed (R=0)", filepath="tests/test_p13/before_p13_r0.png")

    p13 = ProductionP13()
    matches = p13.find_lhs(graph)
    assert len(matches) == 0

    visualize_graph(graph, "P13: Po (R=0)", filepath="tests/test_p13/after_p13_r0.png")

def test_p13_broken_topology_missing_vertex():
    """
    P13 nie powinna działać, jeśli T nie ma 7 wierzchołków.
    """
    graph = get_heptagonal_graph_marked()
    graph.remove_edge("T", 7)
    visualize_graph(graph, "P13: Przed (brak wierzchołka)", filepath="tests/test_p13/before_p13_missing_vertex.png")

    p13 = ProductionP13()
    matches = p13.find_lhs(graph)
    assert len(matches) == 0

    visualize_graph(graph, "P13: Po (brak wierzchołka)", filepath="tests/test_p13/after_p13_missing_vertex.png")
    
def test_p13_broken_topology_missing_edge():
    """
    P13 wymaga, aby wierzchołki T były połączone krawędziami E.
    Usuwamy jedną krawędź E3.
    """
    graph = get_heptagonal_graph_marked()
    graph.remove_node("E3")
    visualize_graph(graph, "P13: Przed (brak krawędzi)", filepath="tests/test_p13/before_p13_missing_edge.png")

    p13 = ProductionP13()
    matches = p13.find_lhs(graph)
    assert len(matches) == 0
    
    visualize_graph(graph, "P13: Po (brak krawędzi)", filepath="tests/test_p13/after_p13_missing_edge.png")
    
def test_p13_B0():
    """
    Sprawdza czy P13 poprawnie oznacza krawędzie siedmiokąta.
    """
    graph = get_heptagonal_graph_marked()
    graph.update_hyperedge("E3", b=0)
    visualize_graph(graph, "P13: Przed", filepath="tests/test_p13/before_p13_b.png")

    p13 = ProductionP13()
    matches = p13.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "T"

    graph = p13.apply(graph)
    visualize_graph(graph, "P13: Po", filepath="tests/test_p13/after_p13_b0.png")

    for i in range(1, 8):
        eid = f"E{i}"
        edge = graph.get_hyperedge(eid)
        assert edge.r == 1, f"Krawędź {eid} powinna mieć R=1"
        
def test_p13_as_subgraph():
    """
    Testuje P13 na większym grafie zawierającym siedmiokąt jako podgraf.
    """
    graph = get_heptagonal_graph_marked()
    
    extra_vertices = [
        (8, 0.5, 1.5),
        (9, -1.5, 0.0),
        (10, 0.5, -1.5),
    ]
    for vid, x, y in extra_vertices:
        v = Vertex(uid=vid, x=x, y=y)
        graph.add_vertex(v)
        
    extra_edges = [
        ("E1_8", "E", 0, 1, [1, 8]),
        ("E2_8", "E", 0, 1, [2, 8]),
        ("E3_9", "E", 0, 1, [3, 9]),
        ("E4_9", "E", 0, 1, [4, 9]),
        ("E5_10", "E", 0, 1, [5, 10]),
        ("E6_10", "E", 0, 1, [6, 10]),
    ]
    for eid, label, r, b, vertices in extra_edges:
        he = Hyperedge(eid, label, r, b)
        graph.add_hyperedge(he)
        for vid in vertices:
            graph.connect(eid, vid)
    
    visualize_graph(graph, "P13: Przed (podgraf)", filepath="tests/test_p13/before_p13_subgraph.png")

    p13 = ProductionP13()
    matches = p13.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "T"

    graph = p13.apply(graph)
    visualize_graph(graph, "P13: Po (podgraf)", filepath="tests/test_p13/after_p13_subgraph.png")

    for i in range(1, 8):
        eid = f"E{i}"
        edge = graph.get_hyperedge(eid)
        assert edge.r == 1, f"Krawędź {eid} powinna mieć R=1"
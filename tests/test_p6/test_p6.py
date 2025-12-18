import pytest
from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p6 import ProductionP6
from tests.graphs import get_pentagonal_graph_marked
from src.utils.visualization import visualize_graph

VIS_DIR = "tests/test_p6"

@pytest.fixture
def p6_test_graph_r0():
    """
    Returns a graph with a pentagon P1 marked as R=0.
    Based on get_pentagonal_graph_marked which returns R=1, we reset it.
    """
    graph = get_pentagonal_graph_marked()
    p_edge = graph.get_hyperedge("P1")
    p_edge.r = 0 # Reset to 0 for P6 test
    # Ensure graph state is updated if needed (object ref should be enough)
    return graph

def test_p6_valid_application(p6_test_graph_r0):
    """
    Test P6 on a valid Pentagon with R=0.
    """
    graph = p6_test_graph_r0
    p6 = ProductionP6()
    
    # LHS
    matches = p6.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "P1"
    
    visualize_graph(graph, title="P6 - Before", filepath=f"{VIS_DIR}/p6_before.png")

    # Apply
    p6.apply(graph)
    
    visualize_graph(graph, title="P6 - After", filepath=f"{VIS_DIR}/p6_after.png")
    
    # Check R=1
    p_edge = graph.get_hyperedge("P1")
    assert p_edge.r == 1

def test_p6_no_match_if_r_is_1(p6_test_graph_r0):
    """
    If R=1, P6 should not fire (already marked).
    """
    graph = p6_test_graph_r0
    p_edge = graph.get_hyperedge("P1")
    p_edge.r = 1 # Manually set to 1
    
    p6 = ProductionP6()
    matches = p6.find_lhs(graph)
    assert len(matches) == 0

def test_p6_no_match_if_label_q(p6_test_graph_r0):
    """
    If label is Q, should not fire.
    """
    graph = p6_test_graph_r0
    p_edge = graph.get_hyperedge("P1")
    p_edge.label = "Q"
    
    p6 = ProductionP6()
    matches = p6.find_lhs(graph)
    assert len(matches) == 0

def test_p6_no_match_if_vertices_not_5(p6_test_graph_r0):
    """
    If P has 4 vertices, it's not a valid Pentagon (malformed).
    """
    graph = p6_test_graph_r0
    
    # Remove a vertex from the P connection
    # Vertices are 1..5 matching P1
    # We disconnect one vertex from P1
    # graph.remove_edge usually removes edge between nodes.
    # Here P1 is connected to vertex 1.
    graph.remove_edge("P1", 1)
    
    p6 = ProductionP6()
    matches = p6.find_lhs(graph)
    assert len(matches) == 0

def test_p6_valid_application_with_noise(p6_test_graph_r0):
    """
    Test P6 works when Pentagon is part of a larger graph.
    """
    graph = p6_test_graph_r0
    
    # Add random noise vertex
    graph.add_vertex(Vertex(uid="noise", x=100, y=100))
    
    p6 = ProductionP6()
    matches = p6.find_lhs(graph)
    assert len(matches) == 1
    
    p6.apply(graph)
    assert graph.get_hyperedge("P1").r == 1

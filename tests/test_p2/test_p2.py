import pytest
from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p2 import ProductionP2
from src.utils.visualization import visualize_graph

VIS_DIR = "tests/test_p2"

@pytest.fixture
def p2_test_graph():
    """
    Creates a graph representing the state where a shared edge needs to be consistent with a neighbor.
    
    Structure:
    v1 (0,0) ----------- v2 (2,0)
    
    Edge E_old connects v1-v2 (The edge to be split by P2).
    
    Neighbor has already split this boundary:
    v_mid (1,0) exists.
    Edges E_n1 (v1-v_mid) and E_n2 (v_mid-v2) exist.
    
    E_old is marked R=1.
    """
    g = Graph()
    
    v1 = Vertex(uid=1, x=0, y=0)
    v2 = Vertex(uid=2, x=2, y=0)
    v_mid = Vertex(uid=3, x=1, y=0)
    
    g.add_vertex(v1)
    g.add_vertex(v2)
    g.add_vertex(v_mid)
    
    # The coarse edge that P2 should match
    e_old = Hyperedge(uid="E_old", label="E", r=1, b=0)
    g.add_hyperedge(e_old)
    g.connect("E_old", 1)
    g.connect("E_old", 2)
    
    # The neighbor's refined edges
    # They should have label 'E'. assuming standard properties.
    e_n1 = Hyperedge(uid="E_n1", label="E", r=0, b=0)
    e_n2 = Hyperedge(uid="E_n2", label="E", r=0, b=0)
    
    g.add_hyperedge(e_n1)
    g.connect("E_n1", 1)
    g.connect("E_n1", 3) # v1 - v_mid
    
    g.add_hyperedge(e_n2)
    g.connect("E_n2", 3) # v_mid
    g.connect("E_n2", 2) # v_mid - v2
    
    return g

def test_p2_valid_application(p2_test_graph):
    """
    Test that P2 correctly identifies the situation and splits E_old.
    """
    graph = p2_test_graph
    p2 = ProductionP2()
    
    # Verify LHS match
    matches = p2.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "E_old"
    
    visualize_graph(graph, title="P2 - Before", filepath=f"{VIS_DIR}/p2_before.png")

    # Apply
    p2.apply(graph)

    visualize_graph(graph, title="P2 - After", filepath=f"{VIS_DIR}/p2_after.png")
    
    # Verify E_old is gone
    with pytest.raises(ValueError):
        graph.get_hyperedge("E_old")
        
    # Verify new edges exist created by P2
    # We expect 2 NEW edges connecting (v1, v_mid) and (v_mid, v2)
    # Total edges between (v1, v_mid) should be 2 (one old neighbor, one new P2)
    edges_v1_mid = graph.get_hyperedges_between_vertices(1, 3)
    assert len(edges_v1_mid) == 2 
    
    edges_mid_v2 = graph.get_hyperedges_between_vertices(3, 2)
    assert len(edges_mid_v2) == 2
    
    # Check attributes of new edges
    # One of them is E_n1, the other is the new one.
    # The new one should have R=0.
    new_edges_1 = [e for e in edges_v1_mid if e.uid != "E_n1"]
    assert len(new_edges_1) == 1
    assert new_edges_1[0].r == 0
    
    new_edges_2 = [e for e in edges_mid_v2 if e.uid != "E_n2"]
    assert len(new_edges_2) == 1
    assert new_edges_2[0].r == 0

def test_p2_no_match_if_r_is_0(p2_test_graph):
    graph = p2_test_graph
    e_old = graph.get_hyperedge("E_old")
    e_old.r = 0 # Unmark
    
    p2 = ProductionP2()
    matches = p2.find_lhs(graph)
    assert len(matches) == 0

def test_p2_no_match_if_boundary(p2_test_graph):
    graph = p2_test_graph
    e_old = graph.get_hyperedge("E_old")
    e_old.b = 1 # Mark as boundary (not shared internal)
    
    p2 = ProductionP2()
    matches = p2.find_lhs(graph)
    assert len(matches) == 0

def test_p2_no_match_if_neighbor_not_split(p2_test_graph):
    """
    If the neighbor structure (v_mid, E_n1, E_n2) does not exist, P2 should not fire.
    """
    graph = p2_test_graph
    
    # Remove neighbor structure
    # Remove v_mid and connected edges
    graph.remove_node(3) # v_mid
    graph.remove_node("E_n1")
    graph.remove_node("E_n2")
    
    # Now we just have v1-E_old-v2
    p2 = ProductionP2()
    matches = p2.find_lhs(graph)
    assert len(matches) == 0

def test_p2_no_match_if_neighbor_partial_split(p2_test_graph):
    """
    If neighbor has v_mid but disconnected or wrong edges.
    """
    graph = p2_test_graph
    
    # Remove one edge E_n2
    graph.remove_node("E_n2")
    
    p2 = ProductionP2()
    matches = p2.find_lhs(graph)
    assert len(matches) == 0

def test_p2_valid_application_with_noise(p2_test_graph):
    """
    Test that P2 works correctly even when the target structure is embedded in a larger graph with noise.
    Verifies point: 'Isomorphism check when embedded in larger graph'.
    """
    graph = p2_test_graph
    
    # Add noise: unconnected vertices and edges
    noise_v = Vertex(uid="noise_v", x=10, y=10)
    graph.add_vertex(noise_v)
    
    noise_e = Hyperedge(uid="noise_e", label="E", r=0, b=1)
    graph.add_hyperedge(noise_e)
    graph.connect("noise_e", "noise_v")
    
    # Add noise connected to the structure but not breaking isomorphism
    # e.g., an extra edge connected to v1
    extra_e = Hyperedge(uid="extra_e", label="E", r=0, b=1)
    graph.add_hyperedge(extra_e)
    graph.connect("extra_e", 1) # Connected to v1
    
    p2 = ProductionP2()
    
    # Verify match still found
    matches = p2.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "E_old"
    
    # Apply
    p2.apply(graph)
    
    # Verify main structure was updated
    with pytest.raises(ValueError):
        graph.get_hyperedge("E_old")
        
    # Verify noise persists
    assert graph.get_hyperedge("noise_e") is not None
    assert graph.get_hyperedge("extra_e") is not None

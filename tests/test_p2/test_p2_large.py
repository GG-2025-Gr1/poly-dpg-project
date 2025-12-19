import pytest
from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p2 import ProductionP2
from src.utils.visualization import visualize_graph
from tests.graphs import get_2x2_grid_graph

VIS_DIR = "tests/test_p2"

def test_p2_on_2x2_grid():
    """
    Test P2 on a 2x2 element grid.
    We focus on the shared edge between Q1 (bottom-left) and Q2 (bottom-right).
    This edge is E11 in get_2x2_grid_graph, connecting nodes 2 and 5.
    
    Setup:
    - Q1 side (left) is the 'neighbor' that has already split.
    - We interpret E(v1, v2) as the edge belonging to the Unrefined element (Q2), while the Refined element (Q1) has already replaced its generic link with the split one.
    
    So:
    1. Start with 2x2 grid.
    2. Identify E11 (connects 2 and 5). This is our target. Mark R=1.
    3. Construct the "Refined Neighbor" structure on the left (Q1 side):
       - Create midpoint v_new.
       - Create edges (2, v_new) and (v_new, 5).
    """
    graph = get_2x2_grid_graph()
    
    # Target Edge: E11 connects 2 and 5.
    e_target = graph.get_hyperedge("E11")
    e_target.r = 1 # Mark for refinement
    
    # Verify coordinates for clarity (from graphs.py)
    # 2: (1.0, 0.0)
    # 5: (1.0, 1.0)
    # Midpoint of edge E11 is (1.0, 0.5).
    
    v2 = graph.get_vertex(2)
    v5 = graph.get_vertex(5)
    
    # Create the "Hanging Node" v_new
    # HYBRID VISUALIZATION STRATEGY:
    # 1. Initialize with OFFSET (x=0.7) for 'Before' visualization to show separation.
    v_new = Vertex(uid="v_hanging", x=0.7, y=0.5)
    graph.add_vertex(v_new)
    
    # Create the neighbor's split edges (simulating Q1 has refined)
    e_split1 = Hyperedge(uid="E_split1", label="E", r=0, b=0)
    e_split2 = Hyperedge(uid="E_split2", label="E", r=0, b=0)
    
    graph.add_hyperedge(e_split1)
    graph.add_hyperedge(e_split2)
    
    # Connect them to form v2 - v_hanging - v5
    graph.connect("E_split1", 2)
    graph.connect("E_split1", "v_hanging")
    
    graph.connect("E_split2", "v_hanging")
    graph.connect("E_split2", 5)
    
    # Verify setup visually - 'Before' state has offset
    visualize_graph(graph, title="P2 Large - Before", filepath=f"{VIS_DIR}/p2_large_before.png")

    # 2. Reset coordinates to GEOMETRIC CORRECTNESS (x=1.0) for P2 application and 'After' visualization.
    # This addresses the requirement: "After P2... without offset".
    graph.update_vertex("v_hanging", x=1.0)

    # Run P2
    p2 = ProductionP2()
    matches = p2.find_lhs(graph)
    
    # We expect E11 to match
    assert len(matches) == 1
    assert matches[0].uid == "E11"
    
    p2.apply(graph)
    
    visualize_graph(graph, title="P2 Large - After", filepath=f"{VIS_DIR}/p2_large_after.png")
    
    # Assertions
    # 1. E11 should be gone
    with pytest.raises(ValueError):
        graph.get_hyperedge("E11")
        
    # 2. We should have NEW edges connecting (2, v_hanging) and (v_hanging, 5)
    edges_2_new = graph.get_hyperedges_between_vertices(2, "v_hanging")
    assert len(edges_2_new) == 2
    
    edges_new_5 = graph.get_hyperedges_between_vertices("v_hanging", 5)
    assert len(edges_new_5) == 2

from itertools import combinations
import pytest

from src.productions.p1 import ProductionP1
from tests.graphs import get_2x2_grid_graph_marked

from src.utils.visualization import visualize_graph

POSSIBLE_Q_IDS = ["Q1", "Q2", "Q3", "Q4"]

VIS_DIR = "tests/test_p1"

def test_2x2_grid_initial_state_with_Q1_marked():
    """Test that all Q elements in the 2x2 grid have R=0 initially. except Q1 which has R=1."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])

    for q_id in POSSIBLE_Q_IDS:
        hyperedge = graph.get_hyperedge(q_id)
        assert hyperedge.label == "Q"
        if q_id == "Q1":
            assert hyperedge.r == 1, f"{q_id} should have R=1 initially"
        else:
            assert hyperedge.r == 0, f"{q_id} should have R=0 initially"
            
    visualize_graph(graph, title="Initial State with Q1 marked", filepath=f"{VIS_DIR}/initial_state_Q1_marked.png")
            
@pytest.mark.parametrize("target_q_id", POSSIBLE_Q_IDS)
def test_2x2_grid_p1_on_specific_q(target_q_id):
    """Test that P1 correctly marks E elements connected to a specific Q element as R=1."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=[target_q_id])
    
    visualize_graph(graph, title=f"Before P1 on {target_q_id}", filepath=f"{VIS_DIR}/before_P1_on_{target_q_id}.png")
    p1 = ProductionP1()

    # Apply P1 to specific Q
    result_graph = p1.apply(graph, target_id=target_q_id)

    # Check that the E edges connected to the target Q have R=1
    target_hyperedge = result_graph.get_hyperedge(target_q_id)
    hyperedge_vertices = result_graph.get_hyperedge_vertices(target_hyperedge.uid)
    for vertex1, vertex2 in combinations(hyperedge_vertices, 2):
        hyperedges = result_graph.get_hyperedges_between_vertices(
            vertex_uid1=vertex1.uid, vertex_uid2=vertex2.uid
        )
        for he in hyperedges:
            if he.label == "E":
                assert he.r == 1, f"E edge {he.uid} connected to {target_q_id} should have R=1 after P1"
                
    visualize_graph(result_graph, title=f"After P1 on {target_q_id}", filepath=f"{VIS_DIR}/after_P1_on_{target_q_id}.png")
import pytest

from src.productions.p0 import ProductionP0
from tests.graphs import get_2x2_grid_graph

POSSIBLE_Q_IDS = ["Q1", "Q2", "Q3", "Q4"]


def test_2x2_grid_initial_state():
    """Test that all Q elements in the 2x2 grid have R=0 initially."""
    graph = get_2x2_grid_graph()

    for q_id in POSSIBLE_Q_IDS:
        hyperedge = graph.get_hyperedge(q_id)
        assert hyperedge.label == "Q"
        assert hyperedge.r == 0, f"{q_id} should have R=0 initially"


@pytest.mark.parametrize("target_q_id", POSSIBLE_Q_IDS)
def test_2x2_grid_p0_on_specific_q(target_q_id):
    """Test that P0 correctly marks a specific Q element as R=1."""
    graph = get_2x2_grid_graph()
    p0 = ProductionP0()

    # Apply P0 to specific Q
    result_graph = p0.apply(graph, target_id=target_q_id)

    # Check that the target Q has R=1
    target_hyperedge = result_graph.get_hyperedge(target_q_id)
    assert target_hyperedge.r == 1, f"{target_q_id} should have R=1 after P0"

    # Check that other Q elements still have R=0
    other_q_ids = [qid for qid in POSSIBLE_Q_IDS if qid != target_q_id]
    for other_q_id in other_q_ids:
        other_hyperedge = result_graph.get_hyperedge(other_q_id)
        assert other_hyperedge.r == 0, f"{other_q_id} should still have R=0"


def test_2x2_grid_p0_automatic_all_candidates():
    """Test that P0 applies to all candidate Q elements automatically when no target is specified."""
    graph = get_2x2_grid_graph()
    p0 = ProductionP0()

    # Apply P0 without specifying target_id (should apply to all candidates)
    result_graph = p0.apply(graph)

    for q_id in POSSIBLE_Q_IDS:
        hyperedge = result_graph.get_hyperedge(q_id)
        assert hyperedge.r == 1, (
            f"{q_id} should have R=1 after P0 applied automatically"
        )

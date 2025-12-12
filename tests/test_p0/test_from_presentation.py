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


def test_2x2_grid_p0_automatic_one_q_modified_to_e():
    """Test that P0 skips Q elements that have been modified to E before application."""
    graph = get_2x2_grid_graph()

    Q_HYPEREDGE_TO_MODIFY = "Q2"
    graph.update_hyperedge(Q_HYPEREDGE_TO_MODIFY, label="E")

    p0 = ProductionP0()

    # Apply P0 without specifying target_id (should apply to all candidates)
    result_graph = p0.apply(graph)

    # Check that the modified Q hyperedge is not processed
    modified_hyperedge = result_graph.get_hyperedge(Q_HYPEREDGE_TO_MODIFY)
    assert modified_hyperedge.label == "E", (
        f"{Q_HYPEREDGE_TO_MODIFY} should remain labeled as 'E'"
    )
    assert modified_hyperedge.r == 0, (
        f"{Q_HYPEREDGE_TO_MODIFY} should have R=0 as it was not a 'Q' during P0"
    )

    q_ids_after_modification = [
        qid for qid in POSSIBLE_Q_IDS if qid != Q_HYPEREDGE_TO_MODIFY
    ]
    for q_id in q_ids_after_modification:
        hyperedge = result_graph.get_hyperedge(q_id)
        assert hyperedge.r == 1, (
            f"{q_id} should have R=1 after P0 applied automatically"
        )


def test_2x2_grid_p0_automatic_one_edge_removed():
    """Test that P0 skips Q elements that have been modified by removing an edge before application."""
    graph = get_2x2_grid_graph()

    EDGE_TO_REMOVE = ["Q2", 5]
    graph.remove_edge(*EDGE_TO_REMOVE)

    p0 = ProductionP0()

    # Apply P0 without specifying target_id (should apply to all candidates)
    result_graph = p0.apply(graph)

    # Check that the modified Q hyperedge is not processed
    modified_hyperedge = result_graph.get_hyperedge(EDGE_TO_REMOVE[0])
    assert modified_hyperedge.label == "Q", (
        f"{EDGE_TO_REMOVE[0]} should remain labeled as 'Q'"
    )
    assert modified_hyperedge.r == 0, (
        f"{EDGE_TO_REMOVE[0]} should have R=0 as it was not connected properly during P0"
    )

    q_ids_after_modification = [
        qid for qid in POSSIBLE_Q_IDS if qid != EDGE_TO_REMOVE[0]
    ]
    for q_id in q_ids_after_modification:
        hyperedge = result_graph.get_hyperedge(q_id)
        assert hyperedge.r == 1, (
            f"{q_id} should have R=1 after P0 applied automatically"
        )


def test_2x2_grid_p0_automatic_one_vertex_removed():
    """Test that P0 skips Q elements that have been modified by removing a vertex before application."""
    graph = get_2x2_grid_graph()

    EDGES_TO_REMOVE = [
        ("Q3", 7),
        ("E6", 8),
        ("E6", 7),
        ("E7", 7),
        ("E7", 4),
    ]
    for edge in EDGES_TO_REMOVE:
        graph.remove_edge(*edge)

    HYPEREDGES_TO_REMOVE = ["E6", "E7"]
    for hyperedge_id in HYPEREDGES_TO_REMOVE:
        graph.remove_node(hyperedge_id)

    VERTEX_TO_REMOVE = 7
    graph.remove_node(VERTEX_TO_REMOVE)

    MODIFIED_HYPEREDGE = "Q3"

    p0 = ProductionP0()

    # Apply P0 without specifying target_id (should apply to all candidates)
    result_graph = p0.apply(graph)

    # Check that the modified Q hyperedge is not processed
    modified_hyperedge = result_graph.get_hyperedge(MODIFIED_HYPEREDGE)
    assert modified_hyperedge.label == "Q", (
        f"{MODIFIED_HYPEREDGE} should remain labeled as 'Q'"
    )
    assert modified_hyperedge.r == 0, (
        f"{MODIFIED_HYPEREDGE} should have R=0 as it was not connected properly during P0"
    )

    q_ids_after_modification = [
        qid for qid in POSSIBLE_Q_IDS if qid != MODIFIED_HYPEREDGE
    ]
    for q_id in q_ids_after_modification:
        hyperedge = result_graph.get_hyperedge(q_id)
        assert hyperedge.r == 1, (
            f"{q_id} should have R=1 after P0 applied automatically"
        )

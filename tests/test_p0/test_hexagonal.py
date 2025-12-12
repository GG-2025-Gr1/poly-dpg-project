import pytest

from src.productions.p0 import ProductionP0
from tests.graphs import get_hexagonal_test_graph

HYPEREDGE_UID = "Q1"

def test_hexagonal_graph_initial_state():
    """Test that the hexagonal graph Q element has R=0 initially."""
    graph = get_hexagonal_test_graph()

    hyperedge = graph.get_hyperedge(HYPEREDGE_UID)

    assert hyperedge.label == "Q"
    assert hyperedge.r == 0, "Q element should have R=0 initially"


def test_hexagonal_graph_p0_not_applied():
    """Test that P0 is not applied to hexagonal Q (6 vertices instead of 4)."""
    graph = get_hexagonal_test_graph()
    p0 = ProductionP0()

    # Apply P0
    result_graph = p0.apply(graph, target_id=HYPEREDGE_UID)
    # Get the Q1 node after P0 attempt
    hyperedge = result_graph.get_hyperedge(HYPEREDGE_UID)

    # P0 should not be applied because Q is connected to 6 vertices, not 4
    assert hyperedge.r == 0, "P0 should not be applied to hexagonal Q (6 vertices)"

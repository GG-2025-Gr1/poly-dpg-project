import pytest

from src.productions.p4 import ProductionP4
from tests.graphs import get_2x2_grid_graph_marked
from src.utils.visualization import visualize_graph

VIS_DIR = "tests/test_p4"


def get_boundary_edges(graph):
    """Get all boundary edges (E with B=1) from the graph."""
    boundary_edges = []
    for _, data in graph._nx_graph.nodes(data=True):
        hyperedge_obj = data.get("data")
        if hasattr(hyperedge_obj, 'label') and hyperedge_obj.label == "E" and hyperedge_obj.b == 1:
            boundary_edges.append(hyperedge_obj)
    return boundary_edges


def get_internal_edges(graph):
    """Get all internal edges (E with B=0) from the graph."""
    internal_edges = []
    for _, data in graph._nx_graph.nodes(data=True):
        hyperedge_obj = data.get("data")
        if hasattr(hyperedge_obj, 'label') and hyperedge_obj.label == "E" and hyperedge_obj.b == 0:
            internal_edges.append(hyperedge_obj)
    return internal_edges


def mark_edges_for_refinement(graph, edge_ids):
    """Mark multiple edges as R=1."""
    for edge in edge_ids:
        edge_id = edge.uid if hasattr(edge, 'uid') else edge
        graph.update_hyperedge(edge_id, r=1)



def test_p4_finds_boundary_edges_with_r1_b1():
    """Test that P4 correctly identifies boundary edges with R=1 and B=1."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    
    boundary_edges = get_boundary_edges(graph)
    mark_edges_for_refinement(graph, boundary_edges)
    
    p4 = ProductionP4()
    candidates = p4.find_lhs(graph)
    
    assert len(candidates) == len(boundary_edges), "P4 should find boundary edges with R=1 and B=1"
    for candidate in candidates:
        assert candidate.label == "E"
        assert candidate.r == 1
        assert candidate.b == 1
    
    visualize_graph(graph, title="Initial state with boundary edge R=1", filepath=f"{VIS_DIR}/initial_state_boundary_r1.png")


def test_p4_splits_boundary_edge_correctly():
    """Test that P4 correctly splits a boundary edge into two new edges."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    
    boundary_edges = get_boundary_edges(graph)
    assert len(boundary_edges) > 0, "Test setup failed: no boundary edge found"
    
    boundary_edge = boundary_edges[0]
    graph.update_hyperedge(boundary_edge.uid, r=1)
    
    # Get original vertices
    original_vertices = graph.get_hyperedge_vertices(boundary_edge.uid)
    assert len(original_vertices) == 2, "Boundary edge should connect exactly 2 vertices"
    
    v1, v2 = original_vertices[0], original_vertices[1]
    expected_mid_x = (v1.x + v2.x) / 2.0
    expected_mid_y = (v1.y + v2.y) / 2.0
    
    # Count edges before
    edges_before = [n for n, d in graph._nx_graph.nodes(data=True) 
                   if hasattr(d.get("data"), 'label') and d.get("data").label == "E"]
    vertices_before = [n for n, d in graph._nx_graph.nodes(data=True) 
                      if d.get("type") == "vertex"]
    
    # Apply P4
    p4 = ProductionP4()
    result_graph = p4.apply(graph, target_id=boundary_edge.uid)
    
    # Count after
    edges_after = [n for n, d in result_graph._nx_graph.nodes(data=True) 
                  if hasattr(d.get("data"), 'label') and d.get("data").label == "E"]
    vertices_after = [n for n, d in result_graph._nx_graph.nodes(data=True) 
                     if d.get("type") == "vertex"]
    
    # Verify: +1 vertex (midpoint), +2 edges (new), -1 edge (old)
    assert len(vertices_after) == len(vertices_before) + 1, "Should have one new vertex"
    assert len(edges_after) == len(edges_before) + 1, "Should have net +1 edge (2 new - 1 old)"
    
    # Find the new vertex (should be at midpoint)
    new_vertices = [v for v in vertices_after if v not in vertices_before]
    assert len(new_vertices) == 1, "Should have exactly one new vertex"
    
    new_vertex_id = new_vertices[0]
    new_vertex = result_graph.get_vertex(new_vertex_id)
    
    assert abs(new_vertex.x - expected_mid_x) < 1e-6, "New vertex X coordinate should be at midpoint"
    assert abs(new_vertex.y - expected_mid_y) < 1e-6, "New vertex Y coordinate should be at midpoint"
    assert new_vertex.hanging == False, "Boundary vertex should not be hanging"
    
    # Verify new edges have correct attributes
    new_vertex_edges = result_graph.get_vertex_hyperedges(new_vertex_id)
    e_edges = [e for e in new_vertex_edges if e.label == "E"]
    
    assert len(e_edges) == 2, "New vertex should be connected to exactly 2 E edges"
    
    for edge in e_edges:
        assert edge.r == 0, f"New edge {edge.uid} should have R=0"
        assert edge.b == 1, f"New edge {edge.uid} should have B=1 (boundary)"
        
        # Verify connectivity
        edge_vertices = result_graph.get_hyperedge_vertices(edge.uid)
        assert len(edge_vertices) == 2, "Each new edge should connect 2 vertices"
        assert new_vertex in edge_vertices, "Each new edge should connect to the new vertex"


def test_p4_should_not_apply_if_r_is_0():
    """Test that P4 does not apply to edges with R=0."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=[])
    
    # All boundary edges should have R=0 by default
    p4 = ProductionP4()
    candidates = p4.find_lhs(graph)
    
    assert len(candidates) == 0, "P4 should not find candidates when all boundary edges have R=0"


def test_p4_should_not_apply_if_b_is_0():
    """Test that P4 does not apply to internal edges (B=0)."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    
    internal_edges = get_internal_edges(graph)
    assert len(internal_edges) > 0, "Test setup failed: no internal edges found"
    
    internal_edge = internal_edges[0]
    graph.update_hyperedge(internal_edge.uid, r=1)
    
    p4 = ProductionP4()
    candidates = p4.find_lhs(graph, target_id=internal_edge.uid)
    
    assert len(candidates) == 0, "P4 should not apply to internal edges (B=0)"


def test_p4_should_not_apply_if_edge_has_wrong_vertex_count():
    """Test that P4 does not apply if edge doesn't connect exactly 2 vertices."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    
    boundary_edges = get_boundary_edges(graph)
    assert len(boundary_edges) > 0, "Test setup failed: no boundary edges found"
    
    boundary_edge = boundary_edges[0]
    graph.update_hyperedge(boundary_edge.uid, r=1)
    
    # Get vertices and remove connection to one
    vertices = graph.get_hyperedge_vertices(boundary_edge.uid)
    assert len(vertices) >= 2

    graph.remove_edge(boundary_edge.uid, vertices[0].uid)
    
    p4 = ProductionP4()
    candidates = p4.find_lhs(graph, target_id=boundary_edge.uid)
    
    assert len(candidates) == 0, "P4 should not apply if edge doesn't have exactly 2 vertices"


def test_p4_preserves_original_vertices():
    """Test that P4 preserves the original vertices unchanged."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    
    boundary_edges = get_boundary_edges(graph)
    boundary_edge = boundary_edges[0]
    
    graph.update_hyperedge(boundary_edge.uid, r=1)
    
    # Store original vertices data
    original_vertices = graph.get_hyperedge_vertices(boundary_edge.uid)
    original_data = [(v.uid, v.x, v.y, v.hanging) for v in original_vertices]
    
    # Apply P4
    p4 = ProductionP4()
    result_graph = p4.apply(graph, target_id=boundary_edge.uid)
    
    # Verify original vertices are unchanged
    for uid, x, y, hanging in original_data:
        vertex = result_graph.get_vertex(uid)
        assert vertex.x == x, f"Vertex {uid} X coordinate should be unchanged"
        assert vertex.y == y, f"Vertex {uid} Y coordinate should be unchanged"
        assert vertex.hanging == hanging, f"Vertex {uid} hanging status should be unchanged"


def test_p4_multiple_applications():
    """Test that P4 can be applied multiple times to different edges."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    
    boundary_edges = get_boundary_edges(graph)
    mark_edges_for_refinement(graph, boundary_edges)
    
    initial_edge_count = len(boundary_edges)
    assert initial_edge_count > 0, "Test setup failed: no boundary edges found"
    
    p4 = ProductionP4()
    
    # Apply P4 to each boundary edge
    for i, edge in enumerate(boundary_edges):
        graph = p4.apply(graph, target_id=edge.uid)
        visualize_graph(graph, title=f"After P4 application {i+1}", filepath=f"{VIS_DIR}/after_p4_application_{i+1}.png")
    
    # Count final vertices and edges
    final_vertices = [n for n, d in graph._nx_graph.nodes(data=True) 
                     if d.get("type") == "vertex"]
    final_edges = [n for n, d in graph._nx_graph.nodes(data=True) 
                  if hasattr(d.get("data"), 'label') and d.get("data").label == "E"]
    
    print(f"Applied P4 to {initial_edge_count} edges")
    print(f"Final vertex count: {len(final_vertices)}")
    print(f"Final edge count: {len(final_edges)}")


@pytest.mark.parametrize("target_edge_suffix", ["1", "2", "3", "4"])
def test_p4_on_specific_boundary_edge(target_edge_suffix):
    """Test P4 application on specific boundary edges."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    
    target_edge_id = f"E{target_edge_suffix}"
    edge = graph.get_hyperedge(target_edge_id)
    assert edge.b == 1, f"Edge {target_edge_id} should be a boundary edge"
    
    graph.update_hyperedge(target_edge_id, r=1)
    
    visualize_graph(graph, title=f"Before P4 on {target_edge_id}", filepath=f"{VIS_DIR}/before_p4_on_{target_edge_id}.png")
    
    p4 = ProductionP4()
    result_graph = p4.apply(graph, target_id=target_edge_id)
    
    visualize_graph(result_graph, title=f"After P4 on {target_edge_id}", filepath=f"{VIS_DIR}/after_p4_on_{target_edge_id}.png")
    
    # Verify the edge was split
    with pytest.raises(ValueError):
        result_graph.get_hyperedge(target_edge_id)


def test_p4_isolation_does_not_affect_neighbors():
    """Test that P4 on one edge doesn't affect neighboring edges incorrectly."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    
    boundary_edges = get_boundary_edges(graph)
    assert len(boundary_edges) >= 2, "Test requires at least 2 boundary edges"
    
    # Mark only the first edge as R=1
    graph.update_hyperedge(boundary_edges[0].uid, r=1)
    
    # Store second edge state
    second_edge_id = boundary_edges[1].uid
    second_edge_before = graph.get_hyperedge(second_edge_id)
    
    # Apply P4 to first edge
    p4 = ProductionP4()
    result_graph = p4.apply(graph, target_id=boundary_edges[0].uid)
    
    # Verify second edge is unchanged
    second_edge_after = result_graph.get_hyperedge(second_edge_id)
    assert second_edge_after.r == second_edge_before.r, "Neighboring edge R should be unchanged"
    assert second_edge_after.b == second_edge_before.b, "Neighboring edge B should be unchanged"
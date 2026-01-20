import pytest
import math
from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p6 import ProductionP6
from src.utils.visualization import visualize_graph

VIS_DIR = "tests/test_p6"

def get_connected_pentagons_graph():
    """
    Creates two pentagons sharing an edge.
    P1: Vertices 1, 2, 3, 4, 5. Center approx (-2, 0)
    P2: Vertices 1, 2, 6, 7, 8. Center approx (2, 0)
    
    They share edge between v1 and v2.
    Geometry:
    - v1 at (0, 1)
    - v2 at (0, -1)
    - P1 extends to left (negative x)
    - P2 extends to right (positive x)
    """
    g = Graph()
    
    # Vertices
    # Shared
    v1 = Vertex(uid=1, x=0.0, y=1.0)
    v2 = Vertex(uid=2, x=0.0, y=-1.0)
    
    # P1 (Left side) - approximated pentagon shape
    v3 = Vertex(uid=3, x=-1.5, y=-1.5)
    v4 = Vertex(uid=4, x=-2.5, y=0.0)
    v5 = Vertex(uid=5, x=-1.5, y=1.5)
    
    # P2 (Right side)
    v6 = Vertex(uid=6, x=1.5, y=-1.5)
    v7 = Vertex(uid=7, x=2.5, y=0.0)
    v8 = Vertex(uid=8, x=1.5, y=1.5)
    
    for v in [v1, v2, v3, v4, v5, v6, v7, v8]:
        g.add_vertex(v)
        
    # Hyperedges (Pentagons)
    # P1 covers 1,2,3,4,5
    p1 = Hyperedge(uid="P1", label="P", r=0, b=0)
    g.add_hyperedge(p1)
    for vid in [1, 2, 3, 4, 5]:
        g.connect("P1", vid)
        
    # P2 covers 1,2,6,7,8
    p2 = Hyperedge(uid="P2", label="P", r=0, b=0)
    g.add_hyperedge(p2)
    for vid in [1, 2, 6, 7, 8]:
        g.connect("P2", vid)
        
    # Edges (Standard graph edges, for visualization mostly)
    # Shared
    e_shared = Hyperedge(uid="E_shared", label="E", r=0, b=0)
    g.add_hyperedge(e_shared)
    g.connect("E_shared", 1)
    g.connect("E_shared", 2)
    
    # P1 loop: 2-3, 3-4, 4-5, 5-1
    edges_p1 = [(2,3), (3,4), (4,5), (5,1)]
    for u, v in edges_p1:
        eid = f"E_{u}_{v}"
        g.add_hyperedge(Hyperedge(uid=eid, label="E", r=0, b=1))
        g.connect(eid, u)
        g.connect(eid, v)
        
    # P2 loop: 2-6, 6-7, 7-8, 8-1
    edges_p2 = [(2,6), (6,7), (7,8), (8,1)]
    for u, v in edges_p2:
        eid = f"E_{u}_{v}"
        g.add_hyperedge(Hyperedge(uid=eid, label="E", r=0, b=1))
        g.connect(eid, u)
        g.connect(eid, v)
        
    return g

def test_p6_on_connected_pentagons():
    g = get_connected_pentagons_graph()
    
    visualize_graph(g, title="P6 Large - Before", filepath=f"{VIS_DIR}/p6_large_before.png")
    
    p6 = ProductionP6()
    
    # LHS check
    matches = p6.find_lhs(g)
    assert len(matches) == 2 # Both P1 and P2 should match
    
    # Apply to all matches
    # Create copy of match list to avoid iteration issues if any
    for m in list(matches):
        p6.apply_rhs(g, m)
    
    visualize_graph(g, title="P6 Large - After", filepath=f"{VIS_DIR}/p6_large_after.png")
    
    # Verify
    assert g.get_hyperedge("P1").r == 1
    assert g.get_hyperedge("P2").r == 1

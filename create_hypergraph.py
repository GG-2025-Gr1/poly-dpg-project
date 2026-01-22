from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.utils.visualization import visualize_graph

def create_target_graph():
    g = Graph()

    # --- 1. Wierzchołki (V) ---
    # Inner Rectangle (Centrum)
    # y range: -0.5 to 0.5
    # x range: -1.0 to 1.0
    v1 = Vertex(uid=1, x=-1.0, y=0.5)   # TL Inner
    v2 = Vertex(uid=2, x=1.0, y=0.5)    # TR Inner
    v3 = Vertex(uid=3, x=1.0, y=-0.5)   # BR Inner
    v4 = Vertex(uid=4, x=-1.0, y=-0.5)  # BL Inner

    # Outer Boundary Corners (Trapezoids Top/Bottom)
    # Expansion y: 1.5
    # Expansion x: 2.0 (corners of trapezoids)
    v5 = Vertex(uid=5, x=-2.0, y=1.5)   # TL Outer
    v6 = Vertex(uid=6, x=2.0, y=1.5)    # TR Outer
    v7 = Vertex(uid=7, x=2.0, y=-1.5)   # BR Outer
    v8 = Vertex(uid=8, x=-2.0, y=-1.5)  # BL Outer

    # Left Hexagon Main Vertices (Nose)
    # To make it a visual hexagon, we add a vertical segment at the tip
    # x = -3.0
    v9 = Vertex(uid=9, x=-3.0, y=0.5, hanging=True)
    v10 = Vertex(uid=10, x=-3.0, y=-0.5, hanging=True)

    # Right Hexagon Main Vertices (Nose)
    # x = 3.0
    v11 = Vertex(uid=11, x=3.0, y=0.5, hanging=True)
    v12 = Vertex(uid=12, x=3.0, y=-0.5, hanging=True)


    all_vertices = [v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12]
    for v in all_vertices:
        g.add_vertex(v)

    # --- 2. Krawędzie (Hyperedges E) ---
    def add_edge(uid, v_ids, boundary=0):
        # r defaults to 0
        e = Hyperedge(uid=uid, label="E", r=0, b=boundary)
        g.add_hyperedge(e)
        for vid in v_ids:
            g.connect(uid, vid)

    # Inner Loop (B=0)
    add_edge("E1", [1, 2], boundary=0)  # Top Inner
    add_edge("E2", [2, 3], boundary=0)  # Right Inner
    add_edge("E3", [3, 4], boundary=0)  # Bottom Inner
    add_edge("E4", [4, 1], boundary=0)  # Left Inner

    # Connecting Edges (Join Inner to Outer)
    add_edge("E5", [1, 5], boundary=0)  # TL
    add_edge("E6", [2, 6], boundary=0)  # TR
    add_edge("E7", [3, 7], boundary=0)  # BR
    add_edge("E8", [4, 8], boundary=0)  # BL

    # Outer Boundary (B=1)
    # Top
    add_edge("E9", [5, 6], boundary=1)
    
    # Right Side (3 segments for Hexagon)
    add_edge("E10", [6, 11], boundary=1)
    add_edge("E11", [11, 12], boundary=1) # The "nose" tip
    add_edge("E12", [12, 7], boundary=1)

    # Bottom
    add_edge("E13", [7, 8], boundary=1) # Note: v7 is BR, v8 is BL

    # Left Side (3 segments for Hexagon)
    add_edge("E14", [8, 10], boundary=1)
    add_edge("E15", [10, 9], boundary=1) # The "nose" tip
    add_edge("E16", [9, 5], boundary=1)

    # --- 3. Regiony (Hyperedges Q/S) ---
    def add_region(uid, label, v_ids):
        node = Hyperedge(uid=uid, label=label, r=0, b=0)
        g.add_hyperedge(node)
        for vid in v_ids:
            g.connect(uid, vid)

    # Center (Q)
    add_region("Q1", "Q", [1, 2, 3, 4])

    # Top (Q)
    add_region("Q2", "Q", [1, 2, 6, 5])

    # Bottom (Q)
    add_region("Q3", "Q", [4, 3, 7, 8])

    # Left (S - Hexagon)
    # Path: 1 -> 4 -> 8 -> 10 -> 9 -> 5
    add_region("S1", "S", [1, 4, 8, 10, 9, 5])

    # Right (S - Hexagon)
    # Path: 2 -> 6 -> 11 -> 12 -> 7 -> 3
    add_region("S2", "S", [2, 6, 11, 12, 7, 3])

    return g

if __name__ == "__main__":
    graph = create_target_graph()
    visualize_graph(graph, "Target Hypergraph (Visual Hexagons)", filepath="target_hypergraph_final.png")

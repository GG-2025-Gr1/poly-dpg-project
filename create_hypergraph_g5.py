from src.graph import Graph
from src.elements import Vertex, Hyperedge

def create_hypergraph_g5():
    g = Graph()

    # --- WIERZCHOŁKI ---
    v_coords = {
        "1": (0.0, 0.0),    "2": (12.5, 0.0),
        "3": (-2.0, 5.0),   "4": (2.0, 5.0),    "5": (10.0, 5.0),
        "6": (20.0, 7.5),
        "7": (-2.0, 10.0),  "8": (2.0, 10.0),   "9": (10.0, 10.0),
        "10": (0.0, 15.0),  "11": (12.5, 15.0)
    }

    for uid, (x, y) in v_coords.items():
        g.add_vertex(Vertex(uid=uid, x=x, y=y))

    # --- KRAWĘDZIE ---
    # Directions aligned to form proper cycles where possible
    edges = [
        # Dół (Q_bottom)
        ("E1", "1", "2", 1), 
        ("E2", "1", "3", 1), 
        ("E3", "1", "4", 0),   
        
        # Środek (Q_center)
        ("E4", "4", "5", 0),   
        ("E5", "2", "5", 0),   
        
        # P_right
        ("E6", "2", "6", 1), 
        
        # S_left
        ("E7", "3", "7", 1), 
        ("E8", "4", "8", 0),   
        
        # Q_center
        ("E9", "8", "9", 0),   # 8->9
        ("E10", "5", "9", 0),  
        
        # Q_top (8,9,11,10) - Cycle: 8->9->11->10->8
        ("E13", "9", "11", 1), # 9->11 (Boundary)
        ("E14", "11", "10", 1),# 11->10 (Boundary) - FIXED DIRECTION
        ("E11", "10", "8", 1), # 10->8 (Boundary) - FIXED DIRECTION
        
        ("E12", "7", "10", 1), # S_left top
        ("E15", "6", "11", 1)  # P_right top
    ]

    for uid, u, v, b in edges:
        g.add_hyperedge(Hyperedge(uid=uid, label="E", r=0, b=b))
        g.connect(uid, u)
        g.connect(uid, v)

    # --- ELEMENTY (INTERIORS) ---
    
    # 1. Q_bottom
    q_bottom = Hyperedge(uid="Q_bottom", label="Q", r=0, b=0)
    g.add_hyperedge(q_bottom)
    for v in ["1", "2", "5", "4"]: g.connect("Q_bottom", v)

    # 2. Q_center
    q_center = Hyperedge(uid="Q_center", label="Q", r=0, b=0)
    g.add_hyperedge(q_center)
    for v in ["4", "5", "9", "8"]: g.connect("Q_center", v)

    # 3. Q_top (8, 9, 11, 10)
    q_top = Hyperedge(uid="Q_top", label="Q", r=0, b=0)
    g.add_hyperedge(q_top)
    for v in ["8", "9", "11", "10"]: g.connect("Q_top", v)

    # 4. S_left
    s_left = Hyperedge(uid="S_left", label="S", r=0, b=0)
    g.add_hyperedge(s_left)
    for v in ["1", "4", "8", "10", "7", "3"]: g.connect("S_left", v)

    # 5. P_right (2, 6, 11, 9, 5)
    p_right = Hyperedge(uid="P_right", label="P", r=0, b=0)
    g.add_hyperedge(p_right)
    for v in ["2", "6", "11", "9", "5"]: g.connect("P_right", v)

    return g
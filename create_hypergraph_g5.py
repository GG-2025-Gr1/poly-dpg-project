from src.graph import Graph
from src.elements import Vertex, Hyperedge

def create_hypergraph_g5():
    g = Graph()

    v_coords = {
        "1": (0.0, 0.0),    "2": (12.5, 0.0),
        "3": (-2.0, 5.0),   "4": (2.0, 5.0),    "5": (10.0, 5.0),
        "6": (20.0, 7.5),
        "7": (-2.0, 10.0),  "8": (2.0, 10.0),   "9": (10.0, 10.0),
        "10": (0.0, 15.0),  "11": (12.5, 15.0)
    }

    for uid, (x, y) in v_coords.items():
        g.add_vertex(Vertex(uid=uid, x=x, y=y))

    # --- KRAWĘDZIE  ---
    edges = [
        ("E1", "1", "2", 1),   # Dół Q_main
        ("E2", "1", "3", 1),   # Dół S_left
        ("E3", "1", "4", 0),   # Wspólna S_left <-> Q_main
        ("E4", "4", "5", 0),   # Wspólna Q_main <-> Q_top
        ("E5", "2", "5", 0),   # Wspólna Q_main <-> P_right
        ("E6", "2", "6", 1),   # P_right dół
        ("E7", "3", "7", 1),   # S_left lewo
        ("E8", "4", "8", 0),   # Wspólna S_left <-> Q_top_left?
        ("E9", "8", "9", 0),   # Wewnątrz
        ("E10", "5", "9", 0),  # Wewnątrz
        ("E11", "8", "10", 1), # Góra
        ("E12", "7", "10", 1), # Góra S_left
        ("E13", "9", "11", 1), # Góra
        ("E14", "10", "11", 1),# Góra
        ("E15", "6", "11", 1)  # P_right góra
    ]

    for uid, u, v, b in edges:
        g.add_hyperedge(Hyperedge(uid=uid, label="E", r=0, b=b))
        g.connect(uid, u)
        g.connect(uid, v)

    # --- ELEMENTY (INTERIORS) ---
    # Musimy zdefiniować, co jest Czworokątem (Q), a co Sześciokątem (S)
    
    # 1. Q_main (Czworokąt na środku)
    # Wierzchołki: 1, 2, 5, 4
    q_main = Hyperedge(uid="Q_main", label="Q", r=0, b=0)
    g.add_hyperedge(q_main)
    for v in ["1", "2", "5", "4"]: g.connect("Q_main", v)

    # 2. S_left (Sześciokąt po lewej)
    # Wierzchołki: 1, 4, 8, 10, 7, 3
    # (Pasuje do krawędzi E3, E8, E11(fragment), E12, E7, E2)
    s_left = Hyperedge(uid="S_left", label="S", r=0, b=0)
    g.add_hyperedge(s_left)
    for v in ["1", "4", "8", "10", "7", "3"]: g.connect("S_left", v)

    # Dodatkowe elementy, żeby b=0 miało sens (sąsiedzi)
    # P_right (Pięciokąt po prawej): 2, 6, 11, 9, 5
    p_right = Hyperedge(uid="P_right", label="P", r=0, b=0)
    g.add_hyperedge(p_right)
    for v in ["2", "6", "11", "9", "5"]: g.connect("P_right", v)

    # Q_top (Czworokąt u góry): 4, 5, 9, 8
    q_top = Hyperedge(uid="Q_top", label="Q", r=0, b=0)
    g.add_hyperedge(q_top)
    for v in ["4", "5", "9", "8"]: g.connect("Q_top", v)

    return g
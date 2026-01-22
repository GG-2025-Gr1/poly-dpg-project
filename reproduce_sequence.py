import networkx as nx
import math
from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.utils.visualization import visualize_graph
from create_hypergraph import create_target_graph

def get_midpoint_if_exists(g: Graph, v1: Vertex, v2: Vertex):
    """Checks if there is a vertex strictly 'between' v1 and v2 connected by E edges."""
    neighbors_v1 = g.get_neighbors(v1.uid)
    for mid in neighbors_v1:
        if mid.uid == v2.uid: continue
        
        neighbors_v2 = g.get_neighbors(v2.uid)
        
        # Check if mid is neighbor of v2 (by UID equality)
        if not any(n.uid == mid.uid for n in neighbors_v2):
            continue

        edges_1 = g.get_hyperedges_between_vertices(v1.uid, mid.uid)
        edges_2 = g.get_hyperedges_between_vertices(v2.uid, mid.uid)
        
        has_e1 = any(e.label == 'E' for e in edges_1)
        has_e2 = any(e.label == 'E' for e in edges_2)

        if has_e1 and has_e2:
            return mid
    return None

def split_edge(g: Graph, v1: Vertex, v2: Vertex):
    """
    Splits the edge between v1 and v2.
    If already split, returns existing midpoint.
    Otherwise creates new midpoint and updates edges.
    """
    # 1. Check existing
    existing_mid = get_midpoint_if_exists(g, v1, v2)
    if existing_mid:
        return existing_mid

    # 2. Find the E-edge to remove
    edges = g.get_hyperedges_between_vertices(v1.uid, v2.uid)
    e_edge = next((e for e in edges if e.label == 'E'), None)
    
    # Calculate pos
    mx = (v1.x + v2.x) / 2
    my = (v1.y + v2.y) / 2
    
    mid_uid = f"v_mid_{v1.uid}_{v2.uid}"
    mid = Vertex(uid=mid_uid, x=mx, y=my)
    g.add_vertex(mid)

    if e_edge:
        # Inherit boundary flag
        b_val = e_edge.b
        g.remove_node(e_edge.uid)
    else:
        # Fallback if no E edge existed (shouldn't happen in valid mesh)
        b_val = 0

    # Create new edges
    e1 = Hyperedge(uid=f"E_{v1.uid}_{mid_uid}", label="E", r=0, b=b_val)
    e2 = Hyperedge(uid=f"E_{mid_uid}_{v2.uid}", label="E", r=0, b=b_val)
    
    g.add_hyperedge(e1)
    g.connect(e1.uid, v1.uid)
    g.connect(e1.uid, mid.uid)
    
    g.add_hyperedge(e2)
    g.connect(e2.uid, mid.uid)
    g.connect(e2.uid, v2.uid)

    return mid

def break_element(g: Graph, element_uid: str):
    """
    Generic split for a polygon element (Quad, Hexagon, etc.) into N Quads around a center.
    """
    print(f"Breaking element {element_uid}...")
    el = g.get_hyperedge(element_uid)
    corners = g.get_hyperedge_vertices(element_uid)
    
    # Sort corners angularly around centroid to ensure correct order
    cx = sum(v.x for v in corners) / len(corners)
    cy = sum(v.y for v in corners) / len(corners)
    corners.sort(key=lambda v: math.atan2(v.y - cy, v.x - cx))
    
    n = len(corners)
    midpoints = []

    # Split all edges
    for i in range(n):
        v_curr = corners[i]
        v_next = corners[(i + 1) % n]
        mid = split_edge(g, v_curr, v_next)
        midpoints.append(mid)

    # Create center vertex
    center_uid = f"v_center_{element_uid}"
    center = Vertex(uid=center_uid, x=cx, y=cy)
    g.add_vertex(center)

    # Create N new Quads
    for i in range(n):
        idx_curr = i
        idx_next = (i + 1) % n
        
        v_corner = corners[idx_next]
        v_mid_prev = midpoints[idx_curr]
        v_mid_next = midpoints[idx_next]
        
        # New Quad Q'
        q_new_uid = f"{element_uid}_sub_{i}"
        
        # Determine R flag: newly created might be 0
        new_q = Hyperedge(uid=q_new_uid, label='Q', r=0, b=0)
        g.add_hyperedge(new_q)
        
        for v in [v_corner, v_mid_prev, center, v_mid_next]:
            g.connect(q_new_uid, v.uid)
            
        # Internal edge (Center -> Midpoint)
        # We need to add internal edges. Each internal edge connects center to a midpoint.
        # There are N midpoints.
        # We should check if edge exists before adding (shared between sub-quads)
        
        # Check/Add edge Center-MidNext
        existing_edges = g.get_hyperedges_between_vertices(center.uid, v_mid_next.uid)
        if not any(e.label == 'E' for e in existing_edges):
            e_in = Hyperedge(uid=f"E_in_{center.uid}_{v_mid_next.uid}", label="E", r=0, b=0)
            g.add_hyperedge(e_in)
            g.connect(e_in.uid, center.uid)
            g.connect(e_in.uid, v_mid_next.uid)

    # Remove old element
    g.remove_node(element_uid)
    return [f"{element_uid}_sub_{i}" for i in range(n)]

def run_sequence():
    # 0. Load
    g = create_target_graph()
    visualize_graph(g, "Start", "iter_0_start.png")

    # 1. Break Bottom Rectangle (Q3)
    # Q3 is the bottom one
    break_element(g, "Q3")
    visualize_graph(g, "Iteracja 1: Złamany dolny prostokąt", "iter_1.png")

    # 2. Break Right Hexagon (S2)
    break_element(g, "S2")
    visualize_graph(g, "Iteracja 2: Złamany prawy sześciokąt", "iter_2.png")

    # 3. Break Center Square (Q1)
    # It returns list of new UIDs. Q1 is replaced.
    sub_q1_ids = break_element(g, "Q1")
    visualize_graph(g, "Iteracja 3: Złamany środkowy kwadrat", "iter_3.png")

    # 4. Break Bottom-Right Square FROM the Center break (Q1 children)
    # We need to find which sub-element of Q1 is in the bottom-right.
    # Q1 was at (0,0). Bottom-Right means x > 0, y < 0.
    # Centroid of Q1 was (0,0).
    # We iterate over the children and check their centroids.
    
    target_uid = None
    best_dist = float('inf')
    # Ideal BR center is approx (0.5, -0.25) relative to (0,0) scale? 
    # Q1 was: (-1,0.5) to (1,-0.5). Center (0,0).
    # Quadrants:
    # TL: center (-0.5, 0.25)
    # TR: center (0.5, 0.25)
    # BL: center (-0.5, -0.25)
    # BR: center (0.5, -0.25)
    
    target_x, target_y = 0.5, -0.25
    
    for uid in sub_q1_ids:
        # Calculate centroid of this sub-quad
        verts = g.get_hyperedge_vertices(uid)
        cx = sum(v.x for v in verts) / 4
        cy = sum(v.y for v in verts) / 4
        
        dist = (cx - target_x)**2 + (cy - target_y)**2
        if dist < best_dist:
            best_dist = dist
            target_uid = uid
            
    if target_uid:
        print(f"Identified BR sub-quad: {target_uid}")
        break_element(g, target_uid)
    else:
        print("Could not find BR sub-quad!")

    visualize_graph(g, "Iteracja 4: Złamany dolny-prawy kwadrat środka", "iter_4.png")

if __name__ == "__main__":
    run_sequence()

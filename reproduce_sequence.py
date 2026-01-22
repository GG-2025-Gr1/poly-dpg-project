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

def save_snapshots(g, prefix, title, highlight_ids=None):
    # Save standard view (Cleaner, highlighted)
    visualize_graph(g, title, f"{prefix}.png", show_attributes=False, highlight_nodes=highlight_ids)
    # Save detailed view (Full details, all attributes)
    visualize_graph(g, f"{title} (Szczegóły)", f"{prefix}_attrs.png", show_attributes=True)

def break_element(g: Graph, element_uid: str, iter_name: str, iter_title_base: str):
    """
    Generic split for a polygon element (Quad, Hexagon, etc.) into N Quads around a center.
    Saves an intermediate snapshot after edges are broken but before the element is replaced.
    """
    print(f"Breaking element {element_uid}...")
    el = g.get_hyperedge(element_uid)
    corners = g.get_hyperedge_vertices(element_uid)
    
    # Sort corners angularly around centroid
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

    # Pre-create internal edges (Center -> Midpoints) for visualization
    internal_edge_ids = []
    for mid in midpoints:
        e_in_uid = f"E_in_{center.uid}_{mid.uid}"
        # Check if exists (paranoia check)
        existing = g.get_hyperedges_between_vertices(center.uid, mid.uid)
        if not any(e.label == 'E' for e in existing):
            e_in = Hyperedge(uid=e_in_uid, label="E", r=0, b=0)
            g.add_hyperedge(e_in)
            g.connect(e_in.uid, center.uid)
            g.connect(e_in.uid, mid.uid)
            internal_edge_ids.append(e_in_uid)

    # --- INTERMEDIATE SNAPSHOT: Edges Broken & Connected ---
    # Highlight the element, new midpoints/edges, and the internal structure
    edge_ids = []
    # Collect ids of edges forming the boundary now
    for i in range(n):
         v_curr = corners[i]
         v_next = corners[(i + 1) % n]
         mid = midpoints[i]
         e_1 = g.get_hyperedges_between_vertices(v_curr.uid, mid.uid)
         e_2 = g.get_hyperedges_between_vertices(mid.uid, v_next.uid)
         edge_ids.extend([e.uid for e in e_1 if e.label=='E'])
         edge_ids.extend([e.uid for e in e_2 if e.label=='E'])
         
    save_snapshots(g, 
                   f"{iter_name}_edges_broken", 
                   f"{iter_title_base} (Krawędzie Podzielone)", 
                   highlight_ids=[element_uid, center_uid] + edge_ids + internal_edge_ids)

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
            
        # Internal edges are already created above

    # Remove old element
    g.remove_node(element_uid)
    return [f"{element_uid}_sub_{i}" for i in range(n)]

def mark_sequence(g, target_uid, prefix, iter_title_base, elem_prod_name, edge_prod_name):
    """
    Performs a 2-step marking sequence:
    1. Mark the element itself (R=1).
    2. Mark its boundary edges (R=1).
    Saves snapshots for both states with specific production titles.
    """
    # --- Step 1: Mark Element ---
    print(f"Marking element {target_uid} using {elem_prod_name}...")
    el = g.get_hyperedge(target_uid)
    el.r = 1
    
    save_snapshots(g, 
                   f"{prefix}_marked_elem", 
                   f"{iter_title_base}: {elem_prod_name} (Oznaczenie Elementu)", 
                   highlight_ids=[target_uid])

    # --- Step 2: Mark Edges ---
    print(f"Marking edges of {target_uid} using {edge_prod_name}...")
    # Find boundary 'E' edges
    vertices = g.get_hyperedge_vertices(target_uid)
    # Sort vertices
    cx = sum(v.x for v in vertices) / len(vertices)
    cy = sum(v.y for v in vertices) / len(vertices)
    vertices.sort(key=lambda v: math.atan2(v.y - cy, v.x - cx))

    n = len(vertices)
    marked_edges = []
    
    for i in range(n):
        v1 = vertices[i]
        v2 = vertices[(i + 1) % n]
        
        edges = g.get_hyperedges_between_vertices(v1.uid, v2.uid)
        for e in edges:
            if e.label == 'E':
                e.r = 1
                g.update_hyperedge(e.uid, r=1)
                marked_edges.append(e.uid)

    save_snapshots(g, 
                   f"{prefix}_marked_edges", 
                   f"{iter_title_base}: {edge_prod_name} (Oznaczenie Krawędzi)", 
                   highlight_ids=[target_uid] + marked_edges)

def run_sequence():
    # 0. Load
    g = create_target_graph()
    save_snapshots(g, "iter_0_start", "Stan Początkowy")

    # 1. Break Bottom Rectangle (Q3)
    # P0: Mark Quad, P1: Mark Edges, P5: Split
    mark_sequence(g, "Q3", "iter_1", "Iteracja 1", "Produkcja P0", "Produkcja P1")
    new_ids = break_element(g, "Q3", "iter_1", "Iteracja 1: Produkcja P5")
    # Final result snapshot (optional for report but good for debug)
    # save_snapshots(g, "iter_1_final", "Iteracja 1: Wynik P5", highlight_ids=new_ids)

    # 2. Break Right Hexagon (S2)
    # P9: Mark Hex, P10: Mark Edges, P11: Split
    mark_sequence(g, "S2", "iter_2", "Iteracja 2", "Produkcja P9", "Produkcja P10")
    new_ids = break_element(g, "S2", "iter_2", "Iteracja 2: Produkcja P11")

    # 3. Break Center Square (Q1)
    # P0, P1, P5
    mark_sequence(g, "Q1", "iter_3", "Iteracja 3", "Produkcja P0", "Produkcja P1")
    sub_q1_ids = break_element(g, "Q1", "iter_3", "Iteracja 3: Produkcja P5")

    # 4. Break Bottom-Right Square FROM the Center break (Q1 children)
    target_uid = None
    best_dist = float('inf')
    target_x, target_y = 0.5, -0.25
    
    for uid in sub_q1_ids:
        verts = g.get_hyperedge_vertices(uid)
        cx = sum(v.x for v in verts) / 4
        cy = sum(v.y for v in verts) / 4
        
        dist = (cx - target_x)**2 + (cy - target_y)**2
        if dist < best_dist:
            best_dist = dist
            target_uid = uid
            
    if target_uid:
        print(f"Identified BR sub-quad: {target_uid}")
        # P0, P1, P5
        mark_sequence(g, target_uid, "iter_4", "Iteracja 4", "Produkcja P0", "Produkcja P1")
        new_ids = break_element(g, target_uid, "iter_4", "Iteracja 4: Produkcja P5")
    else:
        print("Could not find BR sub-quad!")
        save_snapshots(g, "iter_4_error", "Iteracja 4: Error")


if __name__ == "__main__":
    run_sequence()

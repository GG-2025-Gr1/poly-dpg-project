import os
import math
from itertools import combinations
from src.graph import Graph
from src.utils.visualization import visualize_graph
from create_hypergraph_g5 import create_hypergraph_g5
from src.elements import Hyperedge

# PRODUKCJE
from src.productions.p0 import ProductionP0
from src.productions.p1 import ProductionP1
from src.productions.p5 import ProductionP5
from src.productions.p6 import ProductionP6
from src.productions.p7 import ProductionP7
from src.productions.p8 import ProductionP8
from src.productions.p2 import ProductionP2
from src.productions.p3 import ProductionP3
from src.productions.p4 import ProductionP4

OUTPUT_DIR = "visualizations/wywod_grupa_5"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_step(graph, step_num, step_name):
    filepath = os.path.join(OUTPUT_DIR, f"step_{step_num}_{step_name}.png")
    title = f"Krok {step_num}: {step_name.replace('_', ' ')}"
    visualize_graph(graph, title, filepath)

def break_all_marked_edges(graph):
    """Pętla łamiąca krawędzie."""
    p2, p3, p4 = ProductionP2(), ProductionP3(), ProductionP4()
    while True:
        p2_m = p2.find_lhs(graph)
        p3_m = p3.find_lhs(graph)
        p4_m = p4.find_lhs(graph)
        
        if not (p2_m or p3_m or p4_m):
            break
        
        if p2_m: p2.apply_rhs(graph, p2_m[0])
        if p3_m: 
            target = p3_m[0]
            p3.apply_rhs(graph, target)
            try: graph.remove_node(target.uid)
            except: pass
        if p4_m: p4.apply_rhs(graph, p4_m[0])
            
    return graph

def force_mark_edges_of_quad(graph, q_uid):
    """Agresywnie oznacza krawędzie należące do elementu Q."""
    print(f"  [FORCE MARK] Oznaczam krawędzie dla {q_uid}...")
    try:
        vertices = graph.get_hyperedge_vertices(q_uid)
        v_ids = {v.uid for v in vertices}
        count = 0
        for n, d in graph.nx_graph.nodes(data=True):
            edge = d.get('data')
            if isinstance(edge, Hyperedge) and edge.label == "E" and edge.r == 0:
                neighbors = graph.get_hyperedge_vertices(edge.uid)
                if len(neighbors) == 2 and neighbors[0].uid in v_ids and neighbors[1].uid in v_ids:
                    edge.r = 1
                    count += 1
        print(f"  [FORCE MARK] Oznaczono {count} krawędzi.")
    except: pass

def run_derivation():
    print("--- START WYWODU GRUPA 5 ---")
    graph = create_hypergraph_g5()
    save_step(graph, "00", "Stan_Poczatkowy")

    # ========================================================
    # KROK 1: Podział P_right (Pięciokąt)
    # ========================================================
    print("\n--- KROK 1: Podział P_right ---")
    
    p6 = ProductionP6()
    matches = p6.find_lhs(graph)
    target = next((m for m in matches if m.uid == "P_right"), None)
    if target: p6.apply_rhs(graph, target)
    else: graph.update_hyperedge("P_right", r=1)
    save_step(graph, "01", "Oznaczenie_P_right")

    p7 = ProductionP7()
    matches = p7.find_lhs(graph)
    target = next((m for m in matches if m.uid == "P_right"), None)
    if target: p7.apply_rhs(graph, target)
    save_step(graph, "02", "Oznaczenie_Krawedzi_P")

    break_all_marked_edges(graph)
    save_step(graph, "03", "Po_Lamaniu_P")

    p8 = ProductionP8()
    matches = p8.find_lhs(graph)
    target_match = None
    for m in matches:
        uid = m.get('p_hyperedge').uid if isinstance(m, dict) else m.uid
        if uid == "P_right": target_match = m; break
    if not target_match and matches: target_match = matches[0]

    if target_match:
        p8.apply_rhs(graph, target_match)
        save_step(graph, "04", "Podzial_P_right")
    else:
        print("BŁĄD: P8 nie widzi P_right!")

    # ========================================================
    # KROK 2: Podział Q_top
    # ========================================================
    print("\n--- KROK 2: Podział Q_top ---")
    
    graph.update_hyperedge("Q_top", r=1)
    save_step(graph, "05", "Oznaczenie_Q_top")
    
    # Używamy force_mark zamiast P1, żeby obsłużyć połamane krawędzie
    force_mark_edges_of_quad(graph, "Q_top")
    save_step(graph, "06", "Oznaczenie_Krawedzi_Q_top")
        
    print("  Łamanie krawędzi Q_top...")
    break_all_marked_edges(graph)
    save_step(graph, "07", "Po_Lamaniu_Q_top")
    
    p5 = ProductionP5()
    matches = p5.find_lhs(graph)
    target = next((m for m in matches if m.uid == "Q_top"), None)
    if target:
        p5.apply_rhs(graph, target)
        save_step(graph, "08", "Podzial_Q_top_Gotowy")
    else:
        print("BŁĄD: P5 nie widzi Q_top!")

    # ========================================================
    # KROK 3: Podział sub-Q
    # ========================================================
    print("\n--- KROK 3: Podział sub-Q w Q_top ---")
    
    # Cel: Prawy górny róg Q_top (x>6, y>12.5)
    best_q = None
    for n, d in graph.nx_graph.nodes(data=True):
        obj = d.get('data')
        if isinstance(obj, Hyperedge) and obj.label == 'Q' and obj.r == 0:
            vs = graph.get_hyperedge_vertices(obj.uid)
            cx = sum(v.x for v in vs)/len(vs)
            cy = sum(v.y for v in vs)/len(vs)
            if cx > 6.0 and cy > 12.5: 
                best_q = obj
                break
    
    if best_q:
        print(f"  Wybrano sub-Q: {best_q.uid}")
        graph.update_hyperedge(best_q.uid, r=1)
        force_mark_edges_of_quad(graph, best_q.uid)
        break_all_marked_edges(graph)
        
        matches = p5.find_lhs(graph)
        tgt = next((m for m in matches if m.uid == best_q.uid), None)
        if tgt: p5.apply_rhs(graph, tgt)
        save_step(graph, "09", "Podzial_Sub_Q_top")
    else:
        print("  Nie znaleziono sub-Q!")

    # ========================================================
    # KROK 4: Adaptacja
    # ========================================================
    print("\n--- KROK 4: Adaptacja ---")
    
    candidates = []
    p1 = ProductionP1()
    for n, d in graph.nx_graph.nodes(data=True):
        obj = d.get('data')
        if isinstance(obj, Hyperedge) and obj.label == 'Q' and obj.r == 0:
            obj.r = 1 
            if p1.find_lhs(graph, target_id=obj.uid):
                candidates.append(obj)
            else:
                obj.r = 0 
                
    if candidates:
        for cand in candidates:
            print(f"  Adaptacja: {cand.uid}")
            force_mark_edges_of_quad(graph, cand.uid)
            break_all_marked_edges(graph)
            
            ms = p5.find_lhs(graph)
            t = next((m for m in ms if m.uid == cand.uid), None)
            if t: p5.apply_rhs(graph, t)
            
        save_step(graph, "10", "Koncowa_Adaptacja")
    else:
        print("  Brak elementów wymagających adaptacji.")

    print("--- KONIEC ---")

if __name__ == "__main__":
    run_derivation()
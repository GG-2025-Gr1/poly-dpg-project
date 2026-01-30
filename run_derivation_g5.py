import os
import math
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
    """
    Pętla łamiąca krawędzie.
    Działa do skutku, aż żadna produkcja P2/P3/P4 nie będzie miała dopasowania.
    Nie usuwa ręcznie węzłów - polega na produkcjach.
    """
    p2, p3, p4 = ProductionP2(), ProductionP3(), ProductionP4()
    while True:
        p2_m = p2.find_lhs(graph)
        p3_m = p3.find_lhs(graph)
        p4_m = p4.find_lhs(graph)
        
        if not (p2_m or p3_m or p4_m):
            break
        
        if p2_m: 
            print(f"    -> P2 na {p2_m[0].uid}")
            p2.apply_rhs(graph, p2_m[0])
            continue
        if p3_m: 
            print(f"    -> P3 na {p3_m[0].uid}")
            p3.apply_rhs(graph, p3_m[0])
            continue
        if p4_m: 
            print(f"    -> P4 na {p4_m[0].uid}")
            p4.apply_rhs(graph, p4_m[0])
            continue
            
    return graph

def run_derivation():
    print("--- START WYWODU GRUPA 5 ---")
    graph = create_hypergraph_g5()
    save_step(graph, "00", "Stan_Poczatkowy")

    # ========================================================
    # KROK 1: Podział P_right (Pięciokąt)
    # ========================================================
    print("\n--- KROK 1: Podział P_right ---")
    
    # 1. P6: Oznaczenie elementu P
    p6 = ProductionP6()
    matches = p6.find_lhs(graph)
    target = next((m for m in matches if m.uid == "P_right"), None)
    if target: 
        p6.apply_rhs(graph, target)
    else: 
        graph.update_hyperedge("P_right", r=1)
    
    save_step(graph, "01", "P6_Oznaczenie_P")

    # 2. P7: Oznaczenie krawędzi P
    p7 = ProductionP7()
    matches = p7.find_lhs(graph)
    target = next((m for m in matches if m.uid == "P_right"), None)
    if target: 
        p7.apply_rhs(graph, target)
        
    save_step(graph, "02", "P7_Oznaczenie_Krawedzi")

    # 3. Łamanie krawędzi
    break_all_marked_edges(graph)
    save_step(graph, "03", "Po_Lamaniu_P")

    # 4. P8: Podział P
    p8 = ProductionP8()
    matches = p8.find_lhs(graph)
    target_match = None
    for m in matches:
        uid = m.get('p_hyperedge').uid if isinstance(m, dict) else m.uid
        if uid == "P_right": target_match = m; break
    if not target_match and matches: target_match = matches[0]

    if target_match:
        p8.apply_rhs(graph, target_match)
        save_step(graph, "04", "P8_Podzial_P_right")
    else:
        print("BŁĄD: P8 nie widzi P_right!")

    # ========================================================
    # KROK 2: Podział Q_top (Górny Czworokąt)
    # ========================================================
    print("\n--- KROK 2: Podział Q_top ---")
    
    # 1. P0: Oznaczenie Q
    graph.update_hyperedge("Q_top", r=1)
    save_step(graph, "05", "P0_Oznaczenie_Q_top")
    
    # 2. P1: Oznaczenie krawędzi Q
    p1 = ProductionP1()
    matches = p1.find_lhs(graph)
    target = next((m for m in matches if m.uid == "Q_top"), None)
    
    if target:
        print(f"  Zastosowano P1 na {target.uid}")
        p1.apply_rhs(graph, target)
    else:
        print("  UWAGA: P1 nie chwyciło Q_top automatycznie (może geometria?). Próbuję kontynuować.")
    
    save_step(graph, "06", "P1_Oznaczenie_Krawedzi")
        
    break_all_marked_edges(graph)
    save_step(graph, "07", "Po_Lamaniu_Q_top")
    
    # 4. P5: Podział Q
    p5 = ProductionP5()
    matches = p5.find_lhs(graph)
    target = next((m for m in matches if m.uid == "Q_top"), None)
    if target:
        p5.apply_rhs(graph, target)
        save_step(graph, "08", "P5_Podzial_Q_top")
    else:
        print("BŁĄD: P5 nie widzi Q_top!")

    # ========================================================
    # KROK 3: Podział sub-Q (Prawy Górny w Q_top)
    # ========================================================
    print("\n--- KROK 3: Podział sub-Q ---")
    
    best_q = None
    for n, d in graph.nx_graph.nodes(data=True):
        obj = d.get('data')
        if isinstance(obj, Hyperedge) and obj.label == 'Q' and obj.r == 0:
            vs = graph.get_hyperedge_vertices(obj.uid)
            cx = sum(v.x for v in vs)/len(vs)
            cy = sum(v.y for v in vs)/len(vs)
            if cx > 6.0 and cy > 12.5: 
                best_q = obj; break
    
    if best_q:
        print(f"  Wybrano sub-Q: {best_q.uid}")
        graph.update_hyperedge(best_q.uid, r=1)
        
        matches = p1.find_lhs(graph) # P1
        tgt = next((m for m in matches if m.uid == best_q.uid), None)
        if tgt: p1.apply_rhs(graph, tgt)
        
        break_all_marked_edges(graph) # Break
        
        matches = p5.find_lhs(graph) # P5
        tgt = next((m for m in matches if m.uid == best_q.uid), None)
        if tgt: 
            p5.apply_rhs(graph, tgt)
            save_step(graph, "09", "P5_Podzial_Sub_Q")
    else:
        print("BŁĄD: Nie znaleziono sub-Q!")

    # ========================================================
    # KROK 4: Adaptacja (Sąsiad z P_right)
    # ========================================================
    print("\n--- KROK 4: Adaptacja ---")
    
    target_adapt_point = (11.25, 12.5)
    cand_q = None
    min_dist = float('inf')

    for n, d in graph.nx_graph.nodes(data=True):
        obj = d.get('data')
        if isinstance(obj, Hyperedge) and obj.label == 'Q' and obj.r == 0:
            if str(obj.uid).startswith("Q_P_right"):
                vs = graph.get_hyperedge_vertices(obj.uid)
                cx = sum(v.x for v in vs)/len(vs)
                cy = sum(v.y for v in vs)/len(vs)
                dist = math.sqrt((cx - target_adapt_point[0])**2 + (cy - target_adapt_point[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    cand_q = obj

    if cand_q:
        print(f"  Adaptacja elementu: {cand_q.uid}")
        graph.update_hyperedge(cand_q.uid, r=1)
        
        matches = p1.find_lhs(graph)
        tgt = next((m for m in matches if m.uid == cand_q.uid), None)
        if tgt: p1.apply_rhs(graph, tgt)
        
        break_all_marked_edges(graph)
        
        ms = p5.find_lhs(graph)
        t = next((m for m in ms if m.uid == cand_q.uid), None)
        if t: 
            p5.apply_rhs(graph, t)
            save_step(graph, "10", "Koncowa_Adaptacja")
        else:
            print("  BŁĄD: P5 nie zadziałało na adaptowany element.")
    else:
        print("  Brak elementu do adaptacji.")

    print("--- KONIEC ---")

if __name__ == "__main__":
    run_derivation()
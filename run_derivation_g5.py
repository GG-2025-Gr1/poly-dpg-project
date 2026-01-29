import os
import math
from src.graph import Graph
from src.utils.visualization import visualize_graph
from create_hypergraph_g5 import create_hypergraph_g5
from src.elements import Hyperedge

# PRODUKCJE DLA CZWOROKĄTÓW
from src.productions.p0 import ProductionP0   # Oznacza Q (R=1)
from src.productions.p1 import ProductionP1   # Oznacza krawędzie Q
from src.productions.p5 import ProductionP5   # Dzieli Q

# PRODUKCJE DLA PIĘCIOKĄTÓW (Zgodnie z PDF)
from src.productions.p6 import ProductionP6   # Oznacza P (R=1)
from src.productions.p7 import ProductionP7   # Oznacza krawędzie P
from src.productions.p8 import ProductionP8   # Dzieli P

# PRODUKCJE ŁAMIĄCE KRAWĘDZIE
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
    """Pętla łamiąca krawędzie (P2, P3, P4) do skutku."""
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
        if p3_m: 
            # Fix dla P3 (usuwanie starej krawędzi)
            target = p3_m[0]
            print(f"    -> P3 na {target.uid}")
            p3.apply_rhs(graph, target)
            try: graph.remove_node(target.uid)
            except: pass
        if p4_m: 
            print(f"    -> P4 na {p4_m[0].uid}")
            p4.apply_rhs(graph, p4_m[0])
            
    return graph

def run_derivation():
    print("--- START WYWODU GRUPA 5 (P6/P7/P8 + P0/P1/P5) ---")
    
    # KROK 0: Stan Początkowy
    graph = create_hypergraph_g5()
    save_step(graph, "00", "Stan_Poczatkowy")

    # ========================================================
    # KROK 1: Podział Pięciokąta na prawo (P_right)
    # ========================================================
    print("\n--- KROK 1: Podział P_right (Pięciokąt) ---")
    
    # 1. P6: Oznacz element P (R=0 -> R=1)
    # Używamy P6 zamiast ręcznego update'u jeśli to możliwe, ale P6 może nie mieć target_id
    # Spróbujmy znaleźć P_right i użyć P6
    p6 = ProductionP6()
    matches = p6.find_lhs(graph)
    target = next((m for m in matches if m.uid == "P_right"), None)
    
    if target:
        print(f"  Zastosowano P6 na {target.uid}")
        p6.apply_rhs(graph, target)
    else:
        print("  Info: Wymuszam R=1 na P_right ręcznie (P6 nie znalazło)")
        graph.update_hyperedge("P_right", r=1)
    save_step(graph, "01", "Oznaczenie_P_right")

    # 2. P7: Oznaczenie krawędzi Pięciokąta
    p7 = ProductionP7()
    # P7 w find_lhs szuka P(R=1). Powinno znaleźć P_right.
    matches = p7.find_lhs(graph)
    target = next((m for m in matches if m.uid == "P_right"), matches[0] if matches else None)
    
    if target:
        print(f"  Zastosowano P7 na {target.uid} (oznaczanie krawędzi)")
        p7.apply_rhs(graph, target)
    else:
        print("  BŁĄD: P7 nie widzi P_right (z R=1)!")
    save_step(graph, "02", "Oznaczenie_Krawedzi_P")

    # 3. Łamanie krawędzi
    print("  Łamanie krawędzi...")
    break_all_marked_edges(graph)
    save_step(graph, "03", "Po_Lamaniu_P")

    # 4. P8: Finalny podział Pięciokąta
    p8 = ProductionP8()
    matches = p8.find_lhs(graph)
    
    # POPRAWKA: P8 zwraca słowniki, a nie obiekty Hyperedge!
    target_match = None
    for m in matches:
        # m to słownik {'p_hyperedge': obj, ...}
        p_node = m['p_hyperedge']
        if p_node.uid == "P_right":
            target_match = m
            break
    
    # Jeśli nie znaleziono po ID, bierzemy pierwszy (jeśli jest)
    if not target_match and matches:
        target_match = matches[0]
    
    if target_match:
        # Do loga bierzemy UID z obiektu wewnątrz słownika
        uid = target_match['p_hyperedge'].uid
        print(f"  Zastosowano P8 na {uid} -> Podział na 5 Q")
        p8.apply_rhs(graph, target_match)
        save_step(graph, "04", "Podzial_P_right_Gotowy")
    else:
        print("  BŁĄD: P8 nie widzi P_right do podziału! (Sprawdź czy wszystkie boki są połamane)")

    # ========================================================
    # KROK 2: Podział Czworokąta na górze (Q_top)
    # ========================================================
    print("\n--- KROK 2: Podział Q_top (Czworokąt) ---")
    # P0 -> P1 -> Break -> P5
    
    p0, p1, p5 = ProductionP0(), ProductionP1(), ProductionP5()
    
    # 1. P0 (Oznacz Q)
    matches = p0.find_lhs(graph)
    target = next((m for m in matches if m.uid == "Q_top"), None)
    if target:
        p0.apply_rhs(graph, target)
    else:
        graph.update_hyperedge("Q_top", r=1)
    
    # 2. P1 (Oznacz krawędzie)
    matches = p1.find_lhs(graph) # Szuka Q(R=1)
    target = next((m for m in matches if m.uid == "Q_top"), matches[0] if matches else None)
    if target:
        p1.apply_rhs(graph, target)
        
    # 3. Łamanie
    break_all_marked_edges(graph)
    
    # 4. P5 (Podział Q)
    matches = p5.find_lhs(graph)
    target = next((m for m in matches if m.uid == "Q_top"), None)
    if target:
        print(f"  Zastosowano P5 na {target.uid}")
        p5.apply_rhs(graph, target)
        save_step(graph, "05", "Podzial_Q_top")
    else:
        print("  BŁĄD: P5 nie widzi Q_top!")

    # ========================================================
    # KROK 3: Podział prawego górnego sub-czworokąta w Q_top
    # ========================================================
    print("\n--- KROK 3: Podział sub-Q w Q_top (Prawy Górny) ---")
    # Q_top (4,5,9,8). Prawy górny róg to okolice wierzchołka 9 (10.0, 10.0)
    # Środek Q_top był gdzieś w (6.0, 7.5).
    # Szukamy sub-elementu najbliżej (10.0, 10.0).
    
    target_point = (10.0, 10.0)
    best_q = None
    min_dist = float('inf')
    
    for n, d in graph.nx_graph.nodes(data=True):
        obj = d.get('data')
        if isinstance(obj, Hyperedge) and obj.label == 'Q' and obj.r == 0:
            vs = graph.get_hyperedge_vertices(obj.uid)
            cx = sum(v.x for v in vs)/len(vs)
            cy = sum(v.y for v in vs)/len(vs)
            dist = math.sqrt((cx - target_point[0])**2 + (cy - target_point[1])**2)
            if dist < min_dist:
                min_dist = dist
                best_q = obj
    
    if best_q:
        print(f"  Wybrano sub-Q: {best_q.uid}")
        # P0 -> P1 -> Break -> P5
        graph.update_hyperedge(best_q.uid, r=1) # P0 manualnie
        
        matches = p1.find_lhs(graph) # target_id support weak
        # Znajdź ten konkretny match
        tgt = next((m for m in matches if m.uid == best_q.uid), None)
        if tgt: p1.apply_rhs(graph, tgt)
        
        break_all_marked_edges(graph)
        
        matches = p5.find_lhs(graph)
        tgt = next((m for m in matches if m.uid == best_q.uid), None)
        if tgt: p5.apply_rhs(graph, tgt)
        
        save_step(graph, "06", "Podzial_Sub_Q_top")
    else:
        print("  Nie znaleziono sub-Q!")

    # ========================================================
    # KROK 4: Adaptacja sąsiada z podzielonego Pięciokąta
    # ========================================================
    print("\n--- KROK 4: Adaptacja sąsiada (z P_right) ---")
    # P_right (po prawej) został podzielony na 5 Quadów.
    # Q_top (u góry) został podzielony, w tym jego prawy górny róg.
    # Na styku tych dwóch obszarów mógł powstać wiszący węzeł.
    # Szukamy Quada, który ma wiszący węzeł na boku i wymaga podziału.
    
    candidates = []
    # Sprawdzamy wszystkie Q czy P1 (dla R=1) by je chwyciło
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
            # Już ma R=1
            matches = p1.find_lhs(graph)
            tgt = next((m for m in matches if m.uid == cand.uid), None)
            if tgt: p1.apply_rhs(graph, tgt)
            
            break_all_marked_edges(graph)
            
            matches = p5.find_lhs(graph)
            tgt = next((m for m in matches if m.uid == cand.uid), None)
            if tgt: p5.apply_rhs(graph, tgt)
            
        save_step(graph, "07", "Koncowa_Adaptacja")
    else:
        print("  Brak elementów do adaptacji (może geometria się zgodziła bez wiszących węzłów).")

    print("--- KONIEC ---")

if __name__ == "__main__":
    run_derivation()
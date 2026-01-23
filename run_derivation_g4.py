import os
from src.graph import Graph
from src.utils.visualization import visualize_graph
from create_hypergraph_g4 import create_initial_graph_g4

from src.productions.p0 import ProductionP0
from src.productions.p1 import ProductionP1
from src.productions.p2 import ProductionP2
from src.productions.p3 import ProductionP3
from src.productions.p4 import ProductionP4
from src.productions.p5 import ProductionP5
from src.productions.p9 import ProductionP9
from src.productions.p10 import ProductionP10
from src.productions.p11 import ProductionP11

OUTPUT_DIR = "visualizations/grupa-4"


def save_step(graph, step_num, step_name, highlight=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"step_{step_num}_{step_name}.png")
    title = f"Krok {step_num}: {step_name.replace('_', ' ')}"
    visualize_graph(graph, title, filepath, highlight_ids=highlight)


def break_all_marked_edges(graph):
    p2, p3, p4 = ProductionP2(), ProductionP3(), ProductionP4()
    while True:
        p2_m = p2.find_lhs(graph)
        p3_m = p3.find_lhs(graph)
        p4_m = p4.find_lhs(graph)
        if not (p2_m or p3_m or p4_m):
            break
        graph = p2.apply(graph)
        graph = p3.apply(graph)
        graph = p4.apply(graph)
    return graph


def run_derivation():
    p0, p1, p5 = ProductionP0(), ProductionP1(), ProductionP5()
    p9, p10, p11 = ProductionP9(), ProductionP10(), ProductionP11()

    graph = create_initial_graph_g4()
    save_step(graph, "0", "Stan_Poczatkowy")

    # Prawy Sześciokąt
    graph = p9.apply(graph, target_id="S_right")
    save_step(graph, "1a", "P9_Oznaczenie_S", ["S_right"])
    graph = p10.apply(graph, target_id="S_right")
    save_step(graph, "1b", "P10_Oznaczenie_krawedzi", ["S_right", "E11", "E12", "E7", "E6", "E2", "E10"])
    graph = break_all_marked_edges(graph)
    graph = p11.apply(graph, target_id="S_right")
    save_step(graph, "1c", "P11_Podzial_S")

    # Górny Czworokąt
    graph = p0.apply(graph, target_id="Q_top")
    save_step(graph, "2a", "P0_Oznaczenie_Q", ["Q_top"])
    graph = p1.apply(graph, target_id="Q_top")
    save_step(graph, "2b", "P1_Oznaczenie_krawedzi", ["Q_top", "E1", "E5", "E9", "E6"])
    graph = break_all_marked_edges(graph)
    graph = p5.apply(graph, target_id="Q_top")
    save_step(graph, "2c", "P5_Podzial_Q")

    # Środkowy Czworokąt
    graph = p0.apply(graph, target_id="Q_center")
    save_step(graph, "3a", "P0_Oznaczenie_Q", ["Q_center"])
    graph = p1.apply(graph, target_id="Q_center")
    save_step(graph, "3b", "P1_Oznaczenie_krawedzi", ["Q_center", "E1", "E2", "E3", "E4"])
    graph = break_all_marked_edges(graph)
    graph = p5.apply(graph, target_id="Q_center")
    save_step(graph, "3c", "P5_Podzial_Q")

    # Lokalna adaptacja - Górna prawa ćwiartka środka
    sub_q_nodes = [n for n, d in graph.nx_graph.nodes(data=True) if str(n).startswith("Q_center_sub_Q")]
    target = None
    for n in sub_q_nodes:
        verts = graph.get_hyperedge_vertices(n)
        # Szukamy elementu, którego środek ma x > 0 i y > 0
        if sum(v.x for v in verts)/4 > 0 and sum(v.y for v in verts)/4 > 0:
            target = graph.get_hyperedge(n)
            break

    if target:
        print(f"Zidentyfikowano cel (Górny-Prawy): {target.uid}")
        graph = p0.apply(graph, target_id=target.uid)
        save_step(graph, "4a", "P0_Lokalne_Oznaczenie", [target.uid])
        graph = p1.apply(graph, target_id=target.uid)
        graph = break_all_marked_edges(graph)
        graph = p5.apply(graph, target_id=target.uid)
        save_step(graph, "4b", "P5_Lokalny_Podzial")

    save_step(graph, "5", "Stan_Koncowy")


if __name__ == "__main__":
    run_derivation()

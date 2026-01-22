from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p0 import ProductionP0
from src.productions.p2 import ProductionP2
from src.utils.visualization import visualize_graph
from src.graph import Graph
from src.productions.p0 import ProductionP0
from src.productions.p1 import ProductionP1
from src.productions.p2 import ProductionP2
from src.productions.p3 import ProductionP3
from src.productions.p4 import ProductionP4
from src.productions.p5 import ProductionP5
from src.productions.p6 import ProductionP6
from src.productions.p7 import ProductionP7
from src.productions.p8 import ProductionP8
from src.productions.p9 import ProductionP9
from src.productions.p10 import ProductionP10
from src.productions.p11 import ProductionP11
from src.productions.p12 import ProductionP12

def get_custom_graph():
    """
    Tworzy graf z obrazka - czworokąt u góry, prostokąt w środku, czworokąt na dole.
    """
    g = Graph()

    # Wierzchołki - górna część (lewy czworokąt)
    v1 = Vertex(uid=1, x=1.0, y=4.0)
    v2 = Vertex(uid=2, x=0.0, y=3.0)
    v3 = Vertex(uid=3, x=0.0, y=2.0)
    v4 = Vertex(uid=4, x=1.0, y=1.0)
    
    # Wierzchołki - środkowa część (prostokąt)
    v5 = Vertex(uid=5, x=2.0, y=3)
    v6 = Vertex(uid=6, x=2.0, y=2)
    v7 = Vertex(uid=7, x=3.0, y=3)
    v8 = Vertex(uid=8, x=3.0, y=2)
    
    # Wierzchołki - dolna część (prawy czworokąt - symetryczny do górnego)
    v9 = Vertex(uid=9, x=4.0, y=4.0)
    v10 = Vertex(uid=10, x=5.0, y=3.0)
    v11 = Vertex(uid=11, x=5.0, y=2.0)
    v12 = Vertex(uid=12, x=4.0, y=1.0)
    
    for v in [v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12]:
        g.add_vertex(v)

    # Krawędzie zewnętrzne (boundary=1)
    edges_boundary = [
        ("E1", 1, 2),
        ("E2", 2, 3),
        ("E3", 3, 4),
        ("E4", 4, 12),
        ("E5", 12, 11),
        ("E6", 11, 10),
        ("E7", 10, 9),
        ("E8", 9, 1),
    ]
    
    for eid, v1_id, v2_id in edges_boundary:
        e = Hyperedge(uid=eid, label="E", r=0, b=1)
        g.add_hyperedge(e)
        g.connect(eid, v1_id)
        g.connect(eid, v2_id)

    # Krawędzie wewnętrzne (boundary=0)
    edges_internal = [
        ("E9", 1, 5),
        ("E10", 5, 6),
        ("E11", 6, 4),
        ("E12", 5, 7),
        ("E13", 6, 8),
        ("E14", 7, 8),
        ("E15", 9, 7),
        ("E16", 8, 12),
    ]
    
    for eid, v1_id, v2_id in edges_internal:
        e = Hyperedge(uid=eid, label="E", r=0, b=0)
        g.add_hyperedge(e)
        g.connect(eid, v1_id)
        g.connect(eid, v2_id)

    # 11 - lewy szesciokat 
    s1 = Hyperedge(uid="S1", label="S", r=0, b=0)
    g.add_hyperedge(s1)
    for vid in [1, 2, 3, 4, 5, 6]:
        g.connect("S1", vid)
    
    # Q1 - środkowy prostokąt (wierzchołki 5, 6, 7, 8)
    q2 = Hyperedge(uid="Q1", label="Q", r=0, b=0)
    g.add_hyperedge(q2)
    for vid in [5, 6, 7, 8]:
        g.connect("Q1", vid)
    
    # S2 - prawy szesciokat
    s2 = Hyperedge(uid="S2", label="S", r=0, b=0)
    g.add_hyperedge(s2)
    for vid in [7, 8, 9, 10, 11, 12]:
        g.connect("S2", vid)
    # Q2 górny czworokąt
    q2 = Hyperedge(uid="Q2", label="Q", r=0, b=0)
    g.add_hyperedge(q2)
    for vid in [1,5,7,9]:
        g.connect("Q2", vid)
    # Q3 dolny czworokąt
    q3 = Hyperedge(uid="Q3", label="Q", r=0, b=0)
    g.add_hyperedge(q3)
    for vid in [4,6,8,12]:
        g.connect("Q3", vid)

    return g

if __name__ == "__main__":
    p0 = ProductionP0()
    p1 = ProductionP1()
    p2 = ProductionP2()
    p3 = ProductionP3()
    p4 = ProductionP4()
    p5 = ProductionP5()
    p6 = ProductionP6()
    p7 = ProductionP7()
    p8 = ProductionP8()
    p9 = ProductionP9()
    p10 = ProductionP10()
    p11 = ProductionP11()
    p12 = ProductionP12()
    graph = get_custom_graph()
    visualize_graph(graph, "Graf z obrazka", filepath="visualizations/step0.png")
    p9.apply(graph, target_id="S2")
    visualize_graph(graph, "Po zastosowaniu P9", filepath="visualizations/step1.png")
    p0.apply(graph, target_id="Q2")
    visualize_graph(graph, "Po zastosowaniu P0", filepath="visualizations/step2.png")
    p10.apply(graph)
    visualize_graph(graph, "Po zastosowaniu P10", filepath="visualizations/step3.png")
    p4.apply(graph)
    visualize_graph(graph, "Po zastosowaniu P4", filepath="visualizations/step4.png")
    p3.apply(graph)
    visualize_graph(graph, "Po zastosowaniu P3", filepath="visualizations/step5.png")
    p11.apply(graph)
    visualize_graph(graph, "Po zastosowaniu P11", filepath="visualizations/step6.png")
    p1.apply(graph)
    visualize_graph(graph, "Po zastosowaniu P1", filepath="visualizations/step7.png")
    p4.apply(graph) 
    visualize_graph(graph, "Po zastosowaniu P4 ponownie", filepath="visualizations/step8.png")
    p2.apply(graph)
    visualize_graph(graph, "Po zastosowaniu P2", filepath="visualizations/step9.png")
    p3.apply(graph)
    visualize_graph(graph, "Po zastosowaniu P3 ponownie", filepath="visualizations/step10.png")
    p5.apply(graph)
    visualize_graph(graph, "Po zastosowaniu P5", filepath="visualizations/step11.png")

    


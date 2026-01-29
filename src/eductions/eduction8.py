import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.elements import Hyperedge, Vertex
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
from src.productions.p13 import ProductionP13
from src.productions.p14 import ProductionP14
from src.utils.visualization import visualize_graph


def create_custom_graph():
    import math
    
    graph = Graph()

    R_hex = 3.0
    center_hex_x = -5.0
    center_hex_y = 0.0
    angles_hex = [math.radians(90 - 60 * i) for i in range(6)]
    for i in range(6):
        angle = angles_hex[i]
        x = center_hex_x + R_hex * math.cos(angle)
        y = center_hex_y + R_hex * math.sin(angle)
        v = Vertex(uid=i + 1, x=x, y=y)
        graph.add_vertex(v)


    positions_hept = {
        7: (5.0, 3.0),
        8: (7.5, 2.0),
        9: (8.5, 0.0),
        10: (7.5, -2.0),
        11: (5.0, -3.0),
        12: (2.5, -1.5),
        13: (2.5, 1.5),
    }
    for uid, (x, y) in positions_hept.items():
        v = Vertex(uid=uid, x=x, y=y)
        graph.add_vertex(v)

    edge_number = 1

    hex_edges = [(1,2,0), (2,3,0), (3,4,0), (4,5,1), (5,6,1), (6,1,1)]
    for idx, (u, v, b) in enumerate(hex_edges):
        e = Hyperedge(f"E{edge_number}", "E", r=0, b=b)
        graph.add_hyperedge(e)
        graph.connect(e.uid, u)
        graph.connect(e.uid, v)
        edge_number += 1

    hept_edges = [(7,8,1), (8,9,1), (9,10,1), (10,11,1), (11,12,0), (12,13,0), (13,7,0)]
    for idx, (u, v, b) in enumerate(hept_edges):
        e = Hyperedge(f"E{edge_number}", "E", r=0, b=b)
        graph.add_hyperedge(e)
        graph.connect(e.uid, u)
        graph.connect(e.uid, v)
        edge_number += 1

    inter_edges = [(1,7,1), (2,13,0), (3,12,0), (4,11,1)]
    for idx, (u, v, b) in enumerate(inter_edges):
        e = Hyperedge(f"E{edge_number}", "E", r=0, b=b)
        graph.add_hyperedge(e)
        graph.connect(e.uid, u)
        graph.connect(e.uid, v)
        edge_number += 1

    s_hex = Hyperedge("S_hex", "S", r=0, b=0)
    graph.add_hyperedge(s_hex)
    for v in [1,2,3,4,5,6]:
        graph.connect(s_hex.uid, v)

    t_hept = Hyperedge("T_hept", "T", r=0, b=0)
    graph.add_hyperedge(t_hept)
    for v in [7,8,9,10,11,12,13]:
        graph.connect(t_hept.uid, v)

    q1 = Hyperedge("Q1", "Q", r=0, b=0)
    graph.add_hyperedge(q1)
    for v in [1,2,13,7]:
        graph.connect(q1.uid, v)

    q2 = Hyperedge("Q2", "Q", r=0, b=0)
    graph.add_hyperedge(q2)
    for v in [2,3,12,13]:
        graph.connect(q2.uid, v)

    q3 = Hyperedge("Q3", "Q", r=0, b=0)
    graph.add_hyperedge(q3)
    for v in [3,4,11,12]:
        graph.connect(q3.uid, v)
        
    visualize_graph(
        graph,
        "Custom Graph: Hexagon + Heptagon Connected",
        f"eductions/eduction8/step0.png"
    )

    p12 = ProductionP12()
    p12.apply(graph)
    
    visualize_graph(
        graph,
        "P12 Applied",
        f"eductions/eduction8/step1.png"
    )

    p0 = ProductionP0()
    p0.apply(graph, target_id="Q1")
    
    visualize_graph(
        graph,
        "P0 Applied",
        f"eductions/eduction8/step3.png"
    )

    p13 = ProductionP13()
    p13.apply(graph)
    
    visualize_graph(
        graph,
        "P13 Applied",
        f"eductions/eduction8/step4.png"
    )

    p4 = ProductionP4()
    p4.apply(graph)
    
    visualize_graph(
        graph,
        "P4 Applied Three Times",
        f"eductions/eduction8/step5.png"
    )

    p3 = ProductionP3()
    p3.apply(graph)
    
    visualize_graph(
        graph,
        "P3 Applied Three Times",
        f"eductions/eduction8/step6.png"
    )

    p14 = ProductionP14()
    p14.apply(graph)
    
    visualize_graph(
        graph,
        "P14 Applied",
        f"eductions/eduction8/step7.png"
    )

    p1 = ProductionP1()
    p1.apply(graph)
    
    visualize_graph(
        graph,
        "P1 Applied",
        f"eductions/eduction8/step8.png"
    )
    
    p4 = ProductionP4()
    p4.apply(graph)
    
    visualize_graph(
        graph,
        "P4 Applied",
        f"eductions/eduction8/step9.png"
    )
    
    p2 = ProductionP2()
    p2.apply(graph)
    
    visualize_graph(
        graph,
        "P2 Applied",
        f"eductions/eduction8/step10.png"
    )
    
    p3.apply(graph)
    
    visualize_graph(
        graph,
        "P3 Applied",
        f"eductions/eduction8/step11.png"
    )
    
    p5 = ProductionP5()
    p5.apply(graph)
    
    visualize_graph(
        graph,
        "P5 Applied",
        f"eductions/eduction8/step12.png"
    )
    
    p2.apply(graph)
    
    visualize_graph(
        graph,
        "P2 Applied Again",
        f"eductions/eduction8/step13.png"
    )
    
    p0.apply(graph, target_id="Q9")
    visualize_graph(
        graph,
        "P0 Applied Again",
        f"eductions/eduction8/step14.png"
    )
    
    p1.apply(graph)
    visualize_graph(
        graph,
        "P1 Applied Again",
        f"eductions/eduction8/step15.png"
    )
    
    p4.apply(graph)
    visualize_graph(
        graph,
        "P4 Applied Again",
        f"eductions/eduction8/step16.png"
    )
    p3.apply(graph)
    visualize_graph(
        graph,
        "P3 Applied Again",
        f"eductions/eduction8/step17.png"
    )
    p5.apply(graph)
    visualize_graph(
        graph,
        "P5 Applied Again",
        f"eductions/eduction8/step18.png"
    )
    
    p0.apply(graph, target_id="Q13")
    visualize_graph(
        graph,
        "P0 Applied on Q13",
        f"eductions/eduction8/step19.png"
    )
    p1.apply(graph)
    visualize_graph(
        graph,
        "P1 Applied on Q13",
        f"eductions/eduction8/step20.png"
    )
    p4.apply(graph)
    visualize_graph(
        graph,
        "P4 Applied on Q13",
        f"eductions/eduction8/step21.png"
    )
    p2.apply(graph)
    visualize_graph(
        graph,
        "P2 Applied on Q13",
        f"eductions/eduction8/step22.png"
    )
    p3.apply(graph)
    visualize_graph(
        graph,
        "P3 Applied on Q13",
        f"eductions/eduction8/step23.png"
    )
    p5.apply(graph)
    visualize_graph(
        graph,
        "P5 Applied on Q13",
        f"eductions/eduction8/step24.png"
    )
    

if __name__ == "__main__":
    create_custom_graph()
import pytest
from src.productions.p14 import ProductionP14
from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.utils.visualization import visualize_graph
import matplotlib
matplotlib.use("Agg")

# --- KONFIGURACJA ---
VIS_DIR = "tests/test_p14"

def create_base_graph():
    """
    Tworzy bazowy graf wejściowy dla P14.
    """
    graph = Graph()

    import math

    R = 3.0
    corners = []
    for i in range(7):
        angle = 2 * math.pi * i / 7
        x = R * math.cos(angle)
        y = R * math.sin(angle)
        v = Vertex(uid=i + 1, x=x, y=y)
        graph.add_vertex(v)
        corners.append(v)

    midpoints = []
    for i in range(7):
        v1 = corners[i]
        v2 = corners[(i + 1) % 7]
        mx = (v1.x + v2.x) / 2
        my = (v1.y + v2.y) / 2
        mv = Vertex(uid=100 + i, x=mx, y=my)
        graph.add_vertex(mv)
        midpoints.append(mv)

    q = Hyperedge("Q1", "Q", r=1, b=0)
    graph.add_hyperedge(q)
    for v in corners:
        graph.connect("Q1", v.uid)
    
    for i in range(7):
        v1 = corners[i]
        v2 = corners[(i + 1) % 7]
        m = midpoints[i]

        e1 = Hyperedge(f"E1_{i}", "E", r=0, b=1)
        e2 = Hyperedge(f"E2_{i}", "E", r=0, b=1)

        graph.add_hyperedge(e1)
        graph.add_hyperedge(e2)

        graph.connect(e1.uid, v1.uid)
        graph.connect(e1.uid, m.uid)
        graph.connect(e2.uid, v2.uid)
        graph.connect(e2.uid, m.uid)
    
    return graph

def test_vis_standard_execution():
    graph = create_base_graph()

    visualize_graph(
        graph,
        "P14: LHS (Standard)",
        f"{VIS_DIR}/p14_lhs_standard_przed.png"
    )

    p14 = ProductionP14()
    p14.apply(graph)

    visualize_graph(
        graph,
        "P14: RHS (Standard)",
        f"{VIS_DIR}/p14_lhs_standard_po.png"
    )

def test_vis_subgraph_execution():
    graph = create_base_graph()

    graph.add_vertex(Vertex(999, 10, 10))
    graph.add_hyperedge(Hyperedge("E_extra", "E", 0, 1))
    graph.connect("E_extra", 999)

    visualize_graph(
        graph,
        "P14: LHS (Podgraf)",
        f"{VIS_DIR}/p14_lhs_subgraph_przed.png"
    )

    p14 = ProductionP14()
    p14.apply(graph)

    visualize_graph(
        graph,
        "P14: RHS (Podgraf)",
        f"{VIS_DIR}/p14_lhs_subgraph_po.png"
    )

def test_error_missing_midpoint():
    graph = create_base_graph()

    graph.remove_node(100)

    visualize_graph(
        graph,
        "P14: Missing Midpoint",
        f"{VIS_DIR}/p14_lhs_missing_midpoint.png"
    )

    p14 = ProductionP14()
    matches = p14.find_lhs(graph)

    assert len(matches) == 0

def test_error_wrong_R():
    graph = create_base_graph()

    graph.update_hyperedge("Q1", r=0)

    visualize_graph(
        graph,
        "P14: R=0",
        f"{VIS_DIR}/p14_lhs_wrong_R.png"
    )

    p14 = ProductionP14()
    assert len(p14.find_lhs(graph)) == 0

def test_error_unbroken_edge():
    graph = create_base_graph()

    graph.remove_node(100)
    graph.remove_node("E1_0")
    graph.remove_node("E2_0")

    graph.add_hyperedge(Hyperedge("E_whole", "E", 0, 1))
    graph.connect("E_whole", 1)
    graph.connect("E_whole", 2)

    visualize_graph(
        graph,
        "P14: Unbroken Edge",
        f"{VIS_DIR}/p14_lhs_unbroken_edge.png"
    )

    p14 = ProductionP14()
    assert len(p14.find_lhs(graph)) == 0

def test_multiple_matches():
    graph = Graph()

    import math

    def add_septagon(graph, prefix: str, offset_x: float):
        R = 3
        corners = []
        for i in range(7):
            angle = 2 * math.pi * i / 7
            x = R * math.cos(angle) + offset_x
            y = R * math.sin(angle)
            v = Vertex(uid=f"{prefix}_v{i}", x=x, y=y)
            graph.add_vertex(v)
            corners.append(v)

        midpoints = []
        for i in range(7):
            v1 = corners[i]
            v2 = corners[(i + 1) % 7]
            mx = (v1.x + v2.x) / 2
            my = (v1.y + v2.y) / 2
            mv = Vertex(uid=f"{prefix}_m{i}", x=mx, y=my, hanging=True)
            graph.add_vertex(mv)
            midpoints.append(mv)

        q = Hyperedge(f"{prefix}_Q", "Q", r=1, b=0)
        graph.add_hyperedge(q)
        for v in corners:
            graph.connect(q.uid, v.uid)

        for i in range(7):
            e1 = Hyperedge(f"{prefix}_E1_{i}", "E", r=0, b=1)
            e2 = Hyperedge(f"{prefix}_E2_{i}", "E", r=0, b=1)
            graph.add_hyperedge(e1)
            graph.add_hyperedge(e2)

            graph.connect(e1.uid, corners[i].uid)
            graph.connect(e1.uid, midpoints[i].uid)
            graph.connect(e2.uid, corners[(i + 1) % 7].uid)
            graph.connect(e2.uid, midpoints[i].uid)

    add_septagon(graph, "A", offset_x=0)
    add_septagon(graph, "B", offset_x=10)

    visualize_graph(
        graph,
        "P14: Multiple Matches",
        f"{VIS_DIR}/p14_lhs_multiple_matches_przed.png"
    )

    p14 = ProductionP14()
    matches = p14.find_lhs(graph)
    assert len(matches) == 2

    p14.apply(graph)

    visualize_graph(
        graph,
        "P14: Multiple Matches",
        f"{VIS_DIR}/p14_lhs_multiple_matches_po.png"
    )

def test_error_wrong_label():
    graph = create_base_graph()

    graph.update_hyperedge("Q1", label="S")

    visualize_graph(
        graph,
        "P14: Wrong Label",
        f"{VIS_DIR}/p14_lhs_wrong_label.png"
    )

    p14 = ProductionP14()
    assert len(p14.find_lhs(graph)) == 0
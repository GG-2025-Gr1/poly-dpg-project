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
        mv = Vertex(uid=100 + i, x=mx, y=my, hanging=True)
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
    matches = p14.find_lhs(graph)
    assert len(matches) == 1
    p14.apply(graph)

    visualize_graph(
        graph,
        "P14: RHS (Standard)",
        f"{VIS_DIR}/p14_lhs_standard_po.png"
    )

def test_vis_subgraph_execution():
    graph = create_base_graph()

    extra_vertices = [
        Vertex(2000, -8,  0),
        Vertex(2001, -6,  4),
        Vertex(2002,  0,  6),
        Vertex(2003,  6,  4),
        Vertex(2004,  8,  0),
        Vertex(2005,  6, -4),
        Vertex(2006,  0, -6),
        Vertex(2007, -6, -4),
    ]
    for v in extra_vertices:
        graph.add_vertex(v)

    corner_links = [
        (5, 2000),
        (4, 2001),
        (3, 2002),
        (2, 2003),
        (1, 2004),
        (7, 2005),
        (6, 2006),
    ]

    for i, (u, v) in enumerate(corner_links):
        e = Hyperedge(f"E_ext_corner_{i}", "E", 0, 1)
        graph.add_hyperedge(e)
        graph.connect(e.uid, u)
        graph.connect(e.uid, v)

    midpoint_links = [
        (104, 2007),
        (103, 2000),
        (102, 2001),
        (101, 2002),
    ]

    for i, (u, v) in enumerate(midpoint_links):
        e = Hyperedge(f"E_ext_mid_{i}", "E", 0, 1)
        graph.add_hyperedge(e)
        graph.connect(e.uid, u)
        graph.connect(e.uid, v)

    cycle = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
    for i in range(len(cycle)):
        e = Hyperedge(f"E_ext_cycle_{i}", "E", 0, 1)
        graph.add_hyperedge(e)
        graph.connect(e.uid, cycle[i])
        graph.connect(e.uid, cycle[(i + 1) % len(cycle)])
    
    visualize_graph(
        graph,
        "P14: Subgraph",
        f"{VIS_DIR}/p14_lhs_subgraph_przed.png"
    )

    p14 = ProductionP14()
    matches = p14.find_lhs(graph)
    assert len(matches) == 1

    p14.apply(graph)

    visualize_graph(
        graph,
        "P14: Subgraph",
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

    R = 3

    corners_A = []
    for i in range(7):
        angle = 2 * math.pi * i / 7
        v = Vertex(
            uid=f"A_v{i}",
            x=R * math.cos(angle),
            y=R * math.sin(angle)
        )
        graph.add_vertex(v)
        corners_A.append(v)

    mids_A = []
    for i in range(7):
        v1, v2 = corners_A[i], corners_A[(i + 1) % 7]
        mv = Vertex(
            uid=f"A_m{i}",
            x=(v1.x + v2.x) / 2,
            y=(v1.y + v2.y) / 2,
            hanging=True
        )
        graph.add_vertex(mv)
        mids_A.append(mv)

    qA = Hyperedge("Q_A", "Q", r=1, b=0)
    graph.add_hyperedge(qA)
    for v in corners_A:
        graph.connect(qA.uid, v.uid)

    for i in range(7):
        e1 = Hyperedge(f"A_E1_{i}", "E", 0, 1)
        e2 = Hyperedge(f"A_E2_{i}", "E", 0, 1)
        graph.add_hyperedge(e1)
        graph.add_hyperedge(e2)
        graph.connect(e1.uid, corners_A[i].uid)
        graph.connect(e1.uid, mids_A[i].uid)
        graph.connect(e2.uid, corners_A[(i + 1) % 7].uid)
        graph.connect(e2.uid, mids_A[i].uid)

    corners_B = []
    offset_x = 10
    for i in range(7):
        angle = math.pi + 2 * math.pi * i / 7
        v = Vertex(
            uid=f"B_v{i}",
            x=R * math.cos(angle) + offset_x,
            y=R * math.sin(angle)
        )
        graph.add_vertex(v)
        corners_B.append(v)

    mids_B = []
    for i in range(7):
        v1, v2 = corners_B[i], corners_B[(i + 1) % 7]
        mv = Vertex(
            uid=f"B_m{i}",
            x=(v1.x + v2.x) / 2,
            y=(v1.y + v2.y) / 2,
            hanging=True
        )
        graph.add_vertex(mv)
        mids_B.append(mv)

    qB = Hyperedge("Q_B", "Q", r=1, b=0)
    graph.add_hyperedge(qB)
    for v in corners_B:
        graph.connect(qB.uid, v.uid)

    for i in range(7):
        e1 = Hyperedge(f"B_E1_{i}", "E", 0, 1)
        e2 = Hyperedge(f"B_E2_{i}", "E", 0, 1)
        graph.add_hyperedge(e1)
        graph.add_hyperedge(e2)
        graph.connect(e1.uid, corners_B[i].uid)
        graph.connect(e1.uid, mids_B[i].uid)
        graph.connect(e2.uid, corners_B[(i + 1) % 7].uid)
        graph.connect(e2.uid, mids_B[i].uid)

    e_link = Hyperedge("E_link", "E", 0, 1)
    graph.add_hyperedge(e_link)
    graph.connect(e_link.uid, corners_A[0].uid)
    graph.connect(e_link.uid, corners_B[0].uid)

    visualize_graph(
        graph,
        "P14: Multiple matches",
        f"{VIS_DIR}/p14_lhs_multiple_matches_przed.png"
    )

    p14 = ProductionP14()
    matches = p14.find_lhs(graph)
    assert len(matches) == 2

    p14.apply(graph)

    visualize_graph(
        graph,
        "P14: Multiple matches",
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
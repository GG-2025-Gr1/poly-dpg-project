from numpy import shares_memory
from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p0 import ProductionP0
from src.productions.p1 import ProductionP1
from src.productions.p2 import ProductionP2
from src.productions.p3 import ProductionP3
from src.productions.p4 import ProductionP4
from src.productions.p5 import ProductionP5
from src.productions.p12 import ProductionP12
from src.productions.p13 import ProductionP13
from src.productions.p14 import ProductionP14
from src.utils.visualization import visualize_graph


def get_main_graph():
    g = Graph()
    vertices = [
        Vertex(uid=1, x=1.0, y=0.0),
        Vertex(uid=2, x=0.0, y=2.0),
        Vertex(uid=3, x=0.0, y=4.0),
        Vertex(uid=4, x=1.0, y=6.0),
        Vertex(uid=5, x=2.0, y=4.0),
        Vertex(uid=6, x=2.0, y=2.0),
        Vertex(uid=7, x=8.0, y=0.0),
        Vertex(uid=8, x=5.0, y=2.0),
        Vertex(uid=9, x=5.0, y=4.0),
        Vertex(uid=10, x=8.0, y=6.0),
        Vertex(uid=11, x=10.0, y=5.0),
        Vertex(uid=12, x=11.0, y=3.0),
        Vertex(uid=13, x=10.0, y=1.0),
    ]

    for v in vertices:
        g.add_vertex(v)

    boundary_edges = [Hyperedge(uid=f"E{i}", label="E", r=0, b=1) for i in range(1, 10)]

    boundary_edges_vertices = [
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 10),
        (10, 11),
        (11, 12),
        (12, 13),
        (13, 7),
        (7, 1),
    ]

    for e, (v1, v2) in zip(boundary_edges, boundary_edges_vertices):
        g.add_hyperedge(e)
        g.connect(e.uid, v1)
        g.connect(e.uid, v2)

    shared_edges = [Hyperedge(uid=f"ES{i}", label="E", r=0, b=0) for i in range(1, 9)]

    shared_edges_vertices = [
        (1, 6),
        (4, 5),
        (9, 10),
        (7, 8),
        (6, 8),
        (5, 6),
        (5, 9),
        (8, 9),
    ]

    for e, (v1, v2) in zip(shared_edges, shared_edges_vertices):
        g.add_hyperedge(e)
        g.connect(e.uid, v1)
        g.connect(e.uid, v2)

    inside_edges_vertices = [
        (1, 6, 7, 8),
        (1, 2, 3, 4, 5, 6),
        (4, 5, 9, 10),
        (7, 8, 9, 10, 11, 12, 13),
        (5, 6, 8, 9),
    ]

    for i, vs in enumerate(inside_edges_vertices):
        label = "    QPST"[len(vs)]
        e = Hyperedge(uid=f"EI{i+1}", label=label, r=0, b=0)

        g.add_hyperedge(e)
        for v in vs:
            g.connect(e.uid, v)

    return g


def break_element(g, element, refine_prod, mark_prod, break_prod):
    refine_prod.apply_rhs(g, g.get_hyperedge(element))

    for e in mark_prod.find_lhs(g):
        mark_prod.apply_rhs(g, e)

    # break outer edges
    p4 = ProductionP4()
    for e in p4.find_lhs(g):
        p4.apply_rhs(g, e)

    # break broken inner edges
    p2 = ProductionP2()
    for e in p2.find_lhs(g):
        p2.apply_rhs(g, e)

    # break unbroken inner edges
    p3 = ProductionP3()
    for e in p3.find_lhs(g):
        p3.apply_rhs(g, e)

    for e in break_prod.find_lhs(g):
        break_prod.apply_rhs(g, e)


if __name__ == "__main__":
    g = get_main_graph()

    p0 = ProductionP0()
    p1 = ProductionP1()
    p5 = ProductionP5()
    p12 = ProductionP12()
    p13 = ProductionP13()
    p14 = ProductionP14()
    # mark EI4 for refinement

    break_element(g, "EI4", p12, p13, p14)
    break_element(g, "EI3", p0, p1, p5)
    break_element(g, "EI5", p0, p1, p5)
    break_element(g, "EI5_sub_Q2", p0, p1, p5)
    visualize_graph(g, "Graph")

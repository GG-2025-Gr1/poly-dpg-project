import sys
import os

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)
src_path = os.path.join(parent_dir, 'src')

from src.graph import Graph

from src.graph import Graph
from src.elements import Vertex, Hyperedge
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


OUTPUT_DIR = "wywod5"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_starting_graph():
    g = Graph()

    v1 = Vertex(uid=1, x=0.0, y=0.0)
    v2 = Vertex(uid=2, x=12.5, y=0.0)
    v3 = Vertex(uid=3, x=-2.0, y=5.0)
    v4 = Vertex(uid=4, x=2.0, y=5.0)
    v5 = Vertex(uid=5, x=10.0, y=5.0)
    v6 = Vertex(uid=6, x=20.0, y=7.5)
    v7 = Vertex(uid=7, x=-2.0, y=10.0)
    v8 = Vertex(uid=8, x=2.0, y=10.0)
    v9 = Vertex(uid=9, x=10.0, y=10.0)
    v10 = Vertex(uid=10, x=0.0, y=15.0)
    v11 = Vertex(uid=11, x=12.5, y=15.0)

    for v in [v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11]:
        g.add_vertex(v)
    
    e1 = Hyperedge(uid="E1", label="E", r=0, b=1)
    g.add_hyperedge(e1)
    g.connect("E1", 1)
    g.connect("E1", 2)

    e2 = Hyperedge(uid="E2", label="E", r=0, b=1)
    g.add_hyperedge(e2)
    g.connect("E2", 1)
    g.connect("E2", 3)

    e3 = Hyperedge(uid="E3", label="E", r=0, b=0)
    g.add_hyperedge(e3)
    g.connect("E3", 1)
    g.connect("E3", 4)

    e4 = Hyperedge(uid="E4", label="E", r=0, b=0)
    g.add_hyperedge(e4)
    g.connect("E4", 4)
    g.connect("E4", 5)
    
    e5 = Hyperedge(uid="E5", label="E", r=0, b=0)
    g.add_hyperedge(e5)
    g.connect("E5", 2)
    g.connect("E5", 5)

    e6 = Hyperedge(uid="E6", label="E", r=0, b=1)
    g.add_hyperedge(e6)
    g.connect("E6", 2)
    g.connect("E6", 6)

    e7 = Hyperedge(uid="E7", label="E", r=0, b=1)
    g.add_hyperedge(e7)
    g.connect("E7", 3)
    g.connect("E7", 7)

    e8 = Hyperedge(uid="E8", label="E", r=0, b=0)
    g.add_hyperedge(e8)
    g.connect("E8", 4)
    g.connect("E8", 8)

    e9 = Hyperedge(uid="E9", label="E", r=0, b=0)
    g.add_hyperedge(e9)
    g.connect("E9", 8)
    g.connect("E9", 9)

    e10 = Hyperedge(uid="E10", label="E", r=0, b=0)
    g.add_hyperedge(e10)
    g.connect("E10", 5)
    g.connect("E10", 9)

    e11 = Hyperedge(uid="E11", label="E", r=0, b=0)
    g.add_hyperedge(e11)
    g.connect("E11", 8)
    g.connect("E11", 10)

    e12 = Hyperedge(uid="E12", label="E", r=0, b=1)
    g.add_hyperedge(e12)
    g.connect("E12", 7)
    g.connect("E12", 10)

    e13 = Hyperedge(uid="E13", label="E", r=0, b=0)
    g.add_hyperedge(e13)
    g.connect("E13", 9)
    g.connect("E13", 11)

    e14 = Hyperedge(uid="E14", label="E", r=0, b=1)
    g.add_hyperedge(e14)
    g.connect("E14", 10)
    g.connect("E14", 11)

    e15 = Hyperedge(uid="E15", label="E", r=0, b=1)
    g.add_hyperedge(e15)
    g.connect("E15", 6)
    g.connect("E15", 11)

    visualize_graph(g, "Graf", filepath="before.png")

    return g


if __name__ == "__main__":
    
    g = create_starting_graph()

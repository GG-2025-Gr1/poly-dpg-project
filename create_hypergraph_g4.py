from src.graph import Graph
from src.elements import Vertex, Hyperedge


def create_initial_graph_g4():
    g = Graph()

    v_coords = {
        1: (-1.0, 0.5), 2: (1.0, 0.5), 3: (1.0, -0.5), 4: (-1.0, -0.5),
        5: (-2.0, 1.5), 6: (2.0, 1.5), 7: (2.0, -1.5), 8: (-2.0, -1.5),
        9: (-3.0, 0.5), 10: (-3.0, -0.5),
        11: (3.0, 1.5), 12: (3.0, -1.5)
    }
    for uid, (x, y) in v_coords.items():
        g.add_vertex(Vertex(uid=uid, x=x, y=y))

    edges = {
        "E1": ([1, 2], 0), "E2": ([2, 3], 0), "E3": ([3, 4], 0), "E4": ([4, 1], 0),
        "E5": ([1, 5], 0), "E6": ([2, 6], 0), "E7": ([3, 7], 0), "E8": ([4, 8], 0),
        "E9": ([5, 6], 1), "E10": ([6, 11], 1), "E11": ([11, 12], 1), "E12": ([12, 7], 1),
        "E13": ([7, 8], 1), "E14": ([8, 10], 1), "E15": ([10, 9], 1), "E16": ([9, 5], 1)
    }
    for uid, (v_ids, b) in edges.items():
        g.add_hyperedge(Hyperedge(uid=uid, label="E", r=0, b=b))
        for vid in v_ids:
            g.connect(uid, vid)

    regions = {
        "Q_center": ("Q", [1, 2, 3, 4]),
        "Q_top": ("Q", [1, 5, 6, 2]),
        "Q_bottom": ("Q", [4, 8, 7, 3]),
        "S_left": ("S", [1, 4, 8, 10, 9, 5]),
        "S_right": ("S", [2, 3, 7, 12, 11, 6])
    }
    for uid, (label, v_ids) in regions.items():
        g.add_hyperedge(Hyperedge(uid=uid, label=label, r=0, b=0))
        for vid in v_ids:
            g.connect(uid, vid)

    return g

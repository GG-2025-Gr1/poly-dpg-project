import os
import networkx as nx
import matplotlib.pyplot as plt

from ..graph import Graph
from ..elements import Vertex, Hyperedge


def visualize_graph(graph: Graph, title: str, filepath: str = None, show_attributes: bool = True, highlight_ids: list = None):
    nx_graph = graph.nx_graph
    pos = {}

    for node_id, data in nx_graph.nodes(data=True):
        obj = data.get("data")
        if isinstance(obj, Vertex):
            pos[node_id] = (obj.x, obj.y)

    for node_id, data in nx_graph.nodes(data=True):
        obj = data.get("data")
        if isinstance(obj, Hyperedge):
            neighbors = list(nx_graph.neighbors(node_id))
            if neighbors:
                sum_x = sum(pos[n][0] for n in neighbors if n in pos)
                sum_y = sum(pos[n][1] for n in neighbors if n in pos)
                pos[node_id] = (sum_x / len(neighbors), sum_y / len(neighbors))
            else:
                pos[node_id] = (0, 0)

    plt.figure(figsize=(12, 10))

    v_nodes = [n for n, d in nx_graph.nodes(data=True) if isinstance(d.get("data"), Vertex)]
    h_nodes = [n for n, d in nx_graph.nodes(data=True) if isinstance(d.get("data"), Hyperedge)]

    solid_edges = []
    dashed_edges = []
    for u, v in nx_graph.edges():
        data_u = nx_graph.nodes[u].get("data")
        data_v = nx_graph.nodes[v].get("data")
        if (isinstance(data_u, Hyperedge) and data_u.label == 'E') or \
           (isinstance(data_v, Hyperedge) and data_v.label == 'E'):
            solid_edges.append((u, v))
        else:
            dashed_edges.append((u, v))

    nx.draw_networkx_edges(nx_graph, pos, edgelist=dashed_edges, edge_color="lightgray", style="dashed", alpha=0.5)
    nx.draw_networkx_edges(nx_graph, pos, edgelist=solid_edges, edge_color="black", width=2)

    for node_id in h_nodes:
        obj = nx_graph.nodes[node_id]["data"]
        is_lit = highlight_ids is None or node_id in highlight_ids or obj.uid in highlight_ids

        color = "white"
        if is_lit:
            if obj.label == "Q":
                color = "#ff9999"
            elif obj.label == "S":
                color = "#ffcc99"
            elif obj.label == "E":
                color = "#99ff99"

        label = obj.label
        if show_attributes and is_lit:
            if obj.label in ["Q", "S", "P"]:
                label += f"\nR={obj.r}"
            elif obj.label == "E":
                label += f"\nB={obj.b}\nR={obj.r}"

        nx.draw_networkx_nodes(nx_graph, pos, nodelist=[node_id], node_color=color,
                               node_size=800 if obj.label != "E" else 400, edgecolors="gray")
        nx.draw_networkx_labels(nx_graph, pos, labels={node_id: label}, font_size=8, font_weight="bold")

    nx.draw_networkx_nodes(nx_graph, pos, nodelist=v_nodes, node_color="#66b2ff", node_size=150)

    plt.title(title)
    plt.axis("off")

    if filepath:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
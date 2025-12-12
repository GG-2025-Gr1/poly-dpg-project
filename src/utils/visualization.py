import os
import networkx as nx
import matplotlib.pyplot as plt

from ..graph import Graph
from ..elements import Vertex, Hyperedge


def visualize_graph(graph: Graph, title: str, filepath: str = None):
    """
    Visualizes an object of the model.graph.Graph class.
    Calculates the positions of logical nodes (Q, E) based on their neighboring vertices.
    """
    nx_graph = graph.nx_graph
    pos = {}
    labels = {}
    colors = []
    sizes = []

    # 1. Najpierw ustal pozycje dla Wierzchołków (Vertex) - one mają stałe X, Y
    for node_id, data in nx_graph.nodes(data=True):
        obj = data.get("data")
        if isinstance(obj, Vertex):
            pos[node_id] = (obj.x, obj.y)

    # 2. Następnie oblicz pozycje dla Hiperkrawędzi (Hyperedge) - centroidy
    for node_id, data in nx_graph.nodes(data=True):
        obj = data.get("data")
        if isinstance(obj, Hyperedge):
            neighbors = list(nx_graph.neighbors(node_id))
            if not neighbors:
                pos[node_id] = (0, 0)
                continue

            # Średnia z pozycji sąsiadów, którzy mają już ustaloną pozycję (czyli Vertexów)
            sum_x, sum_y, count = 0, 0, 0
            for n in neighbors:
                if n in pos:
                    sum_x += pos[n][0]
                    sum_y += pos[n][1]
                    count += 1

            if count > 0:
                pos[node_id] = (sum_x / count, sum_y / count)
            else:
                pos[node_id] = (0, 0)  # Fallback

    # 3. Stylizacja węzłów
    for node_id, data in nx_graph.nodes(data=True):
        obj = data.get("data")

        if isinstance(obj, Vertex):
            colors.append("#66b2ff")  # Niebieski dla wierzchołków
            sizes.append(200)
            labels[node_id] = f"{node_id}"

        elif isinstance(obj, Hyperedge):
            if obj.label == "Q":
                colors.append("#ff9999")  # Czerwony dla wnętrza
                sizes.append(600)
                # Wyświetlamy ID oraz flagę R
                labels[node_id] = f"Q\nR={obj.r}"
            elif obj.label == "E":
                colors.append("#99ff99")  # Zielony dla krawędzi
                sizes.append(300)
                labels[node_id] = f"E\nB={obj.b}"
            else:
                colors.append("#cccccc")
                sizes.append(300)
                labels[node_id] = str(obj.label)

    # 4. Rysowanie
    plt.figure(figsize=(8, 8))
    nx.draw(
        nx_graph,
        pos,
        with_labels=True,
        labels=labels,
        node_color=colors,
        node_size=sizes,
        font_size=9,
        font_weight="bold",
        edge_color="gray",
    )

    plt.title(title)

    if filepath:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

        output_dir = os.path.join(project_root, "visualizations")
        os.makedirs(output_dir, exist_ok=True)

        dir_only, filename_only = os.path.split(filepath)
        if dir_only:
            output_dir = os.path.join(output_dir, dir_only)
            os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename_only)

        plt.savefig(filepath)
        print(f"Zapisano wizualizację do pliku: {filepath}")
        plt.close()
    else:
        plt.show()

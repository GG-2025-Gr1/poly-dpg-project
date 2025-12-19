import os
import networkx as nx
import matplotlib.pyplot as plt

from ..graph import Graph
from ..elements import Vertex, Hyperedge


def visualize_graph(graph: Graph, title: str, filepath: str = None):
    """
    Visualizes an object of the model.graph.Graph class.
    Calculates the positions of logical nodes (Q, E) based on their neighboring vertices.
    Ensures vertices are drawn ON TOP of hyperedges and their labels for visibility.
    """
    nx_graph = graph.nx_graph
    pos = {}
    
    # Lists to separate drawing layers
    vertex_nodes = []
    hyperedge_nodes = []
    
    # Properties for each node
    labels_v = {}
    colors_v = []
    sizes_v = []
    
    labels_h = {}
    colors_h = []
    sizes_h = []

    # 1. Calculate Positions
    
    # 1a. Vertex positions (fixed)
    for node_id, data in nx_graph.nodes(data=True):
        obj = data.get("data")
        if isinstance(obj, Vertex):
            pos[node_id] = (obj.x, obj.y)
            vertex_nodes.append(node_id)

    # 1b. Hyperedge positions (centroids of neighbors)
    for node_id, data in nx_graph.nodes(data=True):
        obj = data.get("data")
        if isinstance(obj, Hyperedge):
            neighbors = list(nx_graph.neighbors(node_id))
            hyperedge_nodes.append(node_id)
            
            if not neighbors:
                pos[node_id] = (0, 0)
                continue

            sum_x, sum_y, count = 0, 0, 0
            for n in neighbors:
                if n in pos:
                    sum_x += pos[n][0]
                    sum_y += pos[n][1]
                    count += 1

            if count > 0:
                pos[node_id] = (sum_x / count, sum_y / count)
            else:
                pos[node_id] = (0, 0)

    # 2. Prepare visual properties
    
    # Vertices
    for node_id in vertex_nodes:
        colors_v.append("#66b2ff") # Blue
        sizes_v.append(200)
        labels_v[node_id] = f"{node_id}"
        
    # Hyperedges
    for node_id in hyperedge_nodes:
        obj = nx_graph.nodes[node_id]["data"]
        
        if obj.label == "Q":
            colors_h.append("#ff9999") # Red
            sizes_h.append(600)
            labels_h[node_id] = f"Q\nR={obj.r}"
        elif obj.label == "E":
            colors_h.append("#99ff99") # Green
            sizes_h.append(300)
            labels_h[node_id] = f"E\nB={obj.b}\nR={obj.r}"
        else:
            colors_h.append("#cccccc") # Grey
            sizes_h.append(300)
            labels_h[node_id] = f"{obj.label}\nR={obj.r}"

    # 3. Drawing - Layered Approach
    plt.figure(figsize=(8, 8))
    
    # Layer 1: Hyperedges (Background)
    if hyperedge_nodes:
        nx.draw_networkx_nodes(
            nx_graph,
            pos,
            nodelist=hyperedge_nodes,
            node_color=colors_h,
            node_size=sizes_h,
            label="Hyperedges"
        )
        # Layer 1b: Hyperedge Labels (Still background relative to vertices)
        nx.draw_networkx_labels(
            nx_graph,
            pos,
            labels_h,
            font_size=9,
            font_weight="bold"
        )
    
    # Layer 2: Edges (Middle)
    nx.draw_networkx_edges(
        nx_graph,
        pos,
        edge_color="gray"
    )
        
    # Layer 3: Vertices (Foreground)
    if vertex_nodes:
        nx.draw_networkx_nodes(
            nx_graph,
            pos,
            nodelist=vertex_nodes,
            node_color=colors_v,
            node_size=sizes_v,
            label="Vertices"
        )
        # Layer 3b: Vertex Labels (Topmost)
        # Offset labels slightly above the node
        pos_labels = {k: (v[0], v[1] + 0.1) for k, v in pos.items() if k in vertex_nodes}
        
        # Add coordinates to vertex labels for clarity
        enhanced_labels_v = {}
        for node_id in vertex_nodes:
            obj = nx_graph.nodes[node_id]["data"]
            enhanced_labels_v[node_id] = f"{node_id}\n({obj.x},{obj.y})"

        nx.draw_networkx_labels(
            nx_graph,
            pos_labels,
            enhanced_labels_v,
            font_size=8,
            font_weight="bold",
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1) # Add background to labels
        )

    plt.title(title)
    plt.axis('equal') # Keep aspect ratio for geometry

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

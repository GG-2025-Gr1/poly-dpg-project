# import os
# import networkx as nx
# import matplotlib.pyplot as plt
# from PIL import Image, ImageDraw

# from ..graph import Graph
# from ..elements import Vertex, Hyperedge


# def visualize_graph(graph: Graph, title: str, filepath: str = None):
#     """
#     Visualizes an object of the model.graph.Graph class.
#     Calculates the positions of logical nodes (Q, E) based on their neighboring vertices.
#     Ensures vertices are drawn ON TOP of hyperedges and their labels for visibility.
#     """
#     nx_graph = graph.nx_graph
#     pos = {}
    
#     # Lists to separate drawing layers
#     vertex_nodes = []
#     hyperedge_nodes = []
    
#     # Properties for each node
#     labels_v = {}
#     colors_v = []
#     sizes_v = []
    
#     labels_h = {}
#     colors_h = []
#     sizes_h = []

#     # 1. Calculate Positions
    
#     # 1a. Vertex positions (fixed)
#     for node_id, data in nx_graph.nodes(data=True):
#         obj = data.get("data")
#         if isinstance(obj, Vertex):
#             x, y = obj.x, obj.y
#             # Offset dla hanging nodes - aby nie nakładały się z krawędziami
#             if obj.hanging:
#                 y += 0.2
#             pos[node_id] = (x, y)

#     # 1b. Hyperedge positions (centroids of neighbors)
#     for node_id, data in nx_graph.nodes(data=True):
#         obj = data.get("data")
#         if isinstance(obj, Hyperedge):
#             neighbors = list(nx_graph.neighbors(node_id))
#             hyperedge_nodes.append(node_id)
            
#             if not neighbors:
#                 pos[node_id] = (0, 0)
#                 continue

#             sum_x, sum_y, count = 0, 0, 0
#             for n in neighbors:
#                 if n in pos:
#                     sum_x += pos[n][0]
#                     sum_y += pos[n][1]
#                     count += 1

#             if count > 0:
#                 pos[node_id] = (sum_x / count, sum_y / count)
#             else:
#                 pos[node_id] = (0, 0)

#     # 2. Prepare visual properties
    
#     # Vertices
#     for node_id in vertex_nodes:
#         colors_v.append("#66b2ff") # Blue
#         sizes_v.append(200)
#         labels_v[node_id] = f"{node_id}"
        
#     # Hyperedges
#     for node_id in hyperedge_nodes:
#         obj = nx_graph.nodes[node_id]["data"]
        
#         if obj.label == "Q":
#             colors_h.append("#ff9999") # Red
#             sizes_h.append(600)
#             labels_h[node_id] = f"Q\nR={obj.r}"
#         elif obj.label == "E":
#             colors_h.append("#99ff99") # Green
#             sizes_h.append(300)
#             labels_h[node_id] = f"E\nB={obj.b}\nR={obj.r}"
#         else:
#             colors_h.append("#cccccc") # Grey
#             sizes_h.append(300)
#             labels_h[node_id] = f"{obj.label}\nR={obj.r}"

#     # 3. Drawing - Layered Approach
#     plt.figure(figsize=(8, 8))
    
#     # Layer 1: Hyperedges (Background)
#     if hyperedge_nodes:
#         nx.draw_networkx_nodes(
#             nx_graph,
#             pos,
#             nodelist=hyperedge_nodes,
#             node_color=colors_h,
#             node_size=sizes_h,
#             label="Hyperedges"
#         )
#         # Layer 1b: Hyperedge Labels (Still background relative to vertices)
#         nx.draw_networkx_labels(
#             nx_graph,
#             pos,
#             labels_h,
#             font_size=9,
#             font_weight="bold"
#         )
    
#     # Layer 2: Edges (Middle)
#     nx.draw_networkx_edges(
#         nx_graph,
#         pos,
#         edge_color="gray"
#     )
        
#     # Layer 3: Vertices (Foreground)
#     if vertex_nodes:
#         nx.draw_networkx_nodes(
#             nx_graph,
#             pos,
#             nodelist=vertex_nodes,
#             node_color=colors_v,
#             node_size=sizes_v,
#             label="Vertices"
#         )
#         # Layer 3b: Vertex Labels (Topmost)
#         # Offset labels slightly above the node
#         pos_labels = {k: (v[0], v[1] + 0.1) for k, v in pos.items() if k in vertex_nodes}
        
#         # Add coordinates to vertex labels for clarity
#         enhanced_labels_v = {}
#         for node_id in vertex_nodes:
#             obj = nx_graph.nodes[node_id]["data"]
#             enhanced_labels_v[node_id] = f"{node_id}\n({obj.x},{obj.y})"

#         nx.draw_networkx_labels(
#             nx_graph,
#             pos_labels,
#             enhanced_labels_v,
#             font_size=8,
#             font_weight="bold",
#             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1) # Add background to labels
#         )

#     plt.title(title)
#     plt.axis('equal') # Keep aspect ratio for geometry

#     if filepath:
#         current_dir = os.path.dirname(os.path.abspath(__file__))
#         project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

#         output_dir = os.path.join(project_root, "visualizations")
#         os.makedirs(output_dir, exist_ok=True)

#         dir_only, filename_only = os.path.split(filepath)
#         if dir_only:
#             output_dir = os.path.join(output_dir, dir_only)
#             os.makedirs(output_dir, exist_ok=True)
#         filepath = os.path.join(output_dir, filename_only)

#         plt.savefig(filepath)
#         print(f"Zapisano wizualizację do pliku: {filepath}")
#         plt.close()
#     else:
#         plt.show()


# def merge_images_with_arrow(
#     before_path: str, after_path: str, output_path: str, arrow_width: int = 100
# ):
#     """
#     Merges two images side by side with an arrow pointing from the first to the second.

#     Args:
#         before_path: Path to the first image (before state)
#         after_path: Path to the second image (after state)
#         output_path: Path where the merged image should be saved
#         arrow_width: Width of the arrow area between images (default: 100 pixels)
#     """
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
#     output_dir = os.path.join(project_root, "visualizations")

#     dir_only, filename_only = os.path.split(output_path)
#     if dir_only:
#         output_dir = os.path.join(output_dir, dir_only)
#         os.makedirs(output_dir, exist_ok=True)

#     # Load images
#     img1 = Image.open(os.path.join(output_dir, before_path))
#     img2 = Image.open(os.path.join(output_dir, after_path))

#     # Resize images to same height if needed
#     max_height = max(img1.height, img2.height)
#     if img1.height != max_height:
#         aspect_ratio = img1.width / img1.height
#         img1 = img1.resize((int(max_height * aspect_ratio), max_height), Image.LANCZOS)
#     if img2.height != max_height:
#         aspect_ratio = img2.width / img2.height
#         img2 = img2.resize((int(max_height * aspect_ratio), max_height), Image.LANCZOS)

#     # Create new image with space for arrow
#     total_width = img1.width + arrow_width + img2.width
#     merged_img = Image.new("RGB", (total_width, max_height), "white")

#     # Paste images
#     merged_img.paste(img1, (0, 0))
#     merged_img.paste(img2, (img1.width + arrow_width, 0))

#     # Draw arrow
#     draw = ImageDraw.Draw(merged_img)
#     arrow_start_x = img1.width + 10
#     arrow_end_x = img1.width + arrow_width - 10
#     arrow_y = max_height // 2

#     # Arrow line
#     draw.line([(arrow_start_x, arrow_y), (arrow_end_x, arrow_y)], fill="black", width=3)

#     # Arrow head
#     arrow_head_size = 15
#     draw.polygon(
#         [
#             (arrow_end_x, arrow_y),
#             (arrow_end_x - arrow_head_size, arrow_y - arrow_head_size),
#             (arrow_end_x - arrow_head_size, arrow_y + arrow_head_size),
#         ],
#         fill="black",
#     )

#     # Save merged image
#     full_output_path = os.path.join(output_dir, filename_only)
#     merged_img.save(full_output_path)
#     print(f"Zapisano połączoną wizualizację do pliku: {full_output_path}")


###

import os
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

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
            vertex_nodes.append(node_id)
            x, y = obj.x, obj.y
            # Offset dla hanging nodes - aby nie nakładały się z krawędziami
            if obj.hanging:
                y += 0.2
            pos[node_id] = (x, y)

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
        
    # Hyperedges (draw only E-type, hide Q/S nodes and labels)
    hyperedge_nodes_e = []
    for node_id in hyperedge_nodes:
        obj = nx_graph.nodes[node_id]["data"]
        if obj.label != "E":
            continue
        hyperedge_nodes_e.append(node_id)
        colors_h.append("#99ff99") # Green
        sizes_h.append(300)
        labels_h[node_id] = f"E\nB={obj.b}\nR={obj.r}"

    # 3. Drawing - Layered Approach
    plt.figure(figsize=(32, 32))
    
    # Layer 1: Hyperedges (Background) - only E-type
    if hyperedge_nodes_e:
        nx.draw_networkx_nodes(
            nx_graph,
            pos,
            nodelist=hyperedge_nodes_e,
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

    # Layer 2: Edges (Middle) - only edges incident to E-type hyperedges
    edges_to_draw = []
    for u, v in nx_graph.edges():
        obj_u = nx_graph.nodes[u].get("data")
        obj_v = nx_graph.nodes[v].get("data")
        if isinstance(obj_u, Hyperedge) and getattr(obj_u, "label", None) == "E" and isinstance(obj_v, Vertex):
            edges_to_draw.append((u, v))
        elif isinstance(obj_v, Hyperedge) and getattr(obj_v, "label", None) == "E" and isinstance(obj_u, Vertex):
            edges_to_draw.append((u, v))

    if edges_to_draw:
        nx.draw_networkx_edges(
            nx_graph,
            pos,
            edgelist=edges_to_draw,
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
        nx.draw_networkx_labels(
            nx_graph,
            pos,
            labels_v,
            font_size=10,
            font_weight="bold",
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='black', linewidth=0.5, pad=2)
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


def merge_images_with_arrow(
    before_path: str, after_path: str, output_path: str, arrow_width: int = 100
):
    """
    Merges two images side by side with an arrow pointing from the first to the second.

    Args:
        before_path: Path to the first image (before state)
        after_path: Path to the second image (after state)
        output_path: Path where the merged image should be saved
        arrow_width: Width of the arrow area between images (default: 100 pixels)
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    output_dir = os.path.join(project_root, "visualizations")

    dir_only, filename_only = os.path.split(output_path)
    if dir_only:
        output_dir = os.path.join(output_dir, dir_only)
        os.makedirs(output_dir, exist_ok=True)

    # Load images
    img1 = Image.open(os.path.join(output_dir, before_path))
    img2 = Image.open(os.path.join(output_dir, after_path))

    # Resize images to same height if needed
    max_height = max(img1.height, img2.height)
    if img1.height != max_height:
        aspect_ratio = img1.width / img1.height
        img1 = img1.resize((int(max_height * aspect_ratio), max_height), Image.LANCZOS)
    if img2.height != max_height:
        aspect_ratio = img2.width / img2.height
        img2 = img2.resize((int(max_height * aspect_ratio), max_height), Image.LANCZOS)

    # Create new image with space for arrow
    total_width = img1.width + arrow_width + img2.width
    merged_img = Image.new("RGB", (total_width, max_height), "white")

    # Paste images
    merged_img.paste(img1, (0, 0))
    merged_img.paste(img2, (img1.width + arrow_width, 0))

    # Draw arrow
    draw = ImageDraw.Draw(merged_img)
    arrow_start_x = img1.width + 10
    arrow_end_x = img1.width + arrow_width - 10
    arrow_y = max_height // 2

    # Arrow line
    draw.line([(arrow_start_x, arrow_y), (arrow_end_x, arrow_y)], fill="black", width=3)

    # Arrow head
    arrow_head_size = 15
    draw.polygon(
        [
            (arrow_end_x, arrow_y),
            (arrow_end_x - arrow_head_size, arrow_y - arrow_head_size),
            (arrow_end_x - arrow_head_size, arrow_y + arrow_head_size),
        ],
        fill="black",
    )

    # Save merged image
    full_output_path = os.path.join(output_dir, filename_only)
    merged_img.save(full_output_path)
    print(f"Zapisano połączoną wizualizację do pliku: {full_output_path}")
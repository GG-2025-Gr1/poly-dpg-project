import os
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

from ..graph import Graph
from ..elements import Vertex, Hyperedge


def visualize_graph(graph: Graph, title: str, filepath: str = None, show_attributes: bool = False, highlight_nodes: list = None):
    """
    Visualizes an object of the model.graph.Graph class.
    Args:
        highlight_nodes: List of uids (str/int) to highlight. If provided, other hyperedges are grayed out/unlabeled.
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
            x, y = obj.x, obj.y
            if obj.hanging:
                y += 0.2
            pos[node_id] = (x, y)
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
        sizes_v.append(120)       
        labels_v[node_id] = str(node_id) # Just ID
        
    # Hyperedges
    for node_id in hyperedge_nodes:
        obj = nx_graph.nodes[node_id]["data"]
        
        # Logic: Is this node highlighted?
        # If highlight_nodes is None, everything is "highlighted" (normal behavior)
        # If highlight_nodes is Set, only those are.
        is_highlighted = (highlight_nodes is None) or (node_id in highlight_nodes)
        
        if obj.label in ["Q", "S", "P"]:
            if is_highlighted:
                colors_h.append("#ff9999") # Red (Active)
                sizes_h.append(400)
                
                if show_attributes:
                    labels_h[node_id] = f"{obj.label}\nR={obj.r}"
                else:
                    # Minimal label for highlighted ones (just Type)
                    # User asked to remove unnecessary text. 
                    # Maybe just "Q"?
                    labels_h[node_id] = obj.label
            else:
                colors_h.append("#eeeeee") # Very light grey (Inactive)
                sizes_h.append(400)
                labels_h[node_id] = ""     # No label for inactive
                
        elif obj.label == "E":
            colors_h.append("#99ff99") 
            sizes_h.append(80)         
            
            if show_attributes and is_highlighted:
                parts = []
                if obj.b == 1: parts.append("B=1")
                if obj.r == 1: parts.append("R=1")
                labels_h[node_id] = "\n".join(parts) if parts else ""
            else:
                labels_h[node_id] = ""
        else:
            colors_h.append("#cccccc")
            sizes_h.append(100)
            labels_h[node_id] = obj.label if is_highlighted else ""

    # 3. Drawing - Layered Approach
    plt.figure(figsize=(12, 12)) if show_attributes else plt.figure(figsize=(10, 10))
    
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
        labels_h_filtered = {k: v for k, v in labels_h.items() if v}
        
        bbox_style = dict(facecolor='white', alpha=0.8, edgecolor='#cccccc', boxstyle='round,pad=0.2') if show_attributes else None
        
        nx.draw_networkx_labels(
            nx_graph,
            pos,
            labels_h_filtered,
            font_size=9 if show_attributes else 10,
            font_weight="normal" if show_attributes else "bold",
            bbox=bbox_style
        )
    
    # Layer 2: Edges (Middle)
    solid_edges = []
    dashed_edges = []

    for u, v in nx_graph.edges():
        node_u = nx_graph.nodes[u].get("data")
        node_v = nx_graph.nodes[v].get("data")
        
        h_obj = None
        if isinstance(node_u, Hyperedge):
            h_obj = node_u
        elif isinstance(node_v, Hyperedge):
            h_obj = node_v
            
        if h_obj:
            if h_obj.label == 'E':
                solid_edges.append((u, v))
            else:
                dashed_edges.append((u, v))
    
    if solid_edges:
        nx.draw_networkx_edges(
            nx_graph,
            pos,
            edgelist=solid_edges,
            edge_color="black",
            width=2.5
        )
        
    if dashed_edges:
        nx.draw_networkx_edges(
            nx_graph,
            pos,
            edgelist=dashed_edges,
            edge_color="gray",
            style="dashed",
            width=1.0,
            alpha=0.7
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
        # pos_labels = {k: (v[0], v[1] + 0.08) for k, v in pos.items() if k in vertex_nodes}
        #
        # nx.draw_networkx_labels(
        #     nx_graph,
        #     pos_labels,
        #     labels_v,
        #     font_size=8,
        #     font_color="#333333"
        # )

    plt.title(title)
    plt.axis('equal')

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

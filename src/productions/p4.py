from typing import List, Union
import uuid
from .production import Production
from ..graph import Graph
from ..elements import Vertex, Hyperedge


class ProductionP4(Production):
    """
    P4: Podział krawędzi brzegowej.
    Znajduje krawędź E z R=1 i B=1, wstawia nowy wierzchołek w jej środku
    i tworzy dwie nowe krawędzie z B=1 i R=0.
    """

    DEBUG = True

    def find_lhs(
        self, graph: Graph, target_id: Union[int, str] = None
    ) -> List[Hyperedge]:
        candidates: List[Hyperedge] = []

        for _, data in graph._nx_graph.nodes(data=True):
            if self.DEBUG:
                print(f"[P4] Sprawdzam węzeł: {data}")

            hyperedge_obj = data.get("data")

            # 1. Must be a Hyperedge
            if not isinstance(hyperedge_obj, Hyperedge):
                if self.DEBUG:
                    print("[P4] - pomijam, nie jest Hyperedge.")
                continue

            # 2. If target_id is given, only consider that specific node
            if target_id is not None and hyperedge_obj.uid != target_id:
                if self.DEBUG:
                    print(f"[P4] - pomijam, nie jest celem (target_id={target_id}).")
                continue

            # 3. Must have label E
            if hyperedge_obj.label != "E":
                if self.DEBUG:
                    print("[P4] - pomijam, nie jest E.")
                continue

            # 4. Must have R=1
            if hyperedge_obj.r != 1:
                if self.DEBUG:
                    print("[P4] - pomijam, R != 1.")
                continue

            # 5. Must have B=1 (boundary edge)
            if hyperedge_obj.b != 1:
                if self.DEBUG:
                    print("[P4] - pomijam, B != 1.")
                continue

            # 6. Must be connected to exactly 2 vertices
            hyperedge_vertices = graph.get_hyperedge_vertices(hyperedge_obj.uid)
            if self.DEBUG:
                print(f"[P4] - znalezione wierzchołki hiperkrawędzi: {hyperedge_vertices}")

            if len(hyperedge_vertices) != 2:
                if self.DEBUG:
                    print("[P4] - pomijam, nie ma dokładnie 2 wierzchołków.")
                continue

            if self.DEBUG:
                print(f"[P4] - znaleziono kandydata: {hyperedge_obj}")
            candidates.append(hyperedge_obj)

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        vertices = graph.get_hyperedge_vertices(match_node.uid)
        v1, v2 = vertices[0], vertices[1]

        if self.DEBUG:
            print(f"[P4] Dzielę krawędź {match_node.uid} między wierzchołkami {v1.uid} i {v2.uid}")

        mid_x = (v1.x + v2.x) / 2.0
        mid_y = (v1.y + v2.y) / 2.0

        new_vertex_id = str(uuid.uuid4())

        new_vertex = Vertex(uid=new_vertex_id, x=mid_x, y=mid_y, hanging=False)
        graph.add_vertex(new_vertex)

        if self.DEBUG:
            print(f"[P4] Utworzono nowy wierzchołek {new_vertex_id} w ({mid_x}, {mid_y})")

        edge1_id = str(uuid.uuid4())
        edge2_id = str(uuid.uuid4())

        edge1 = Hyperedge(uid=edge1_id, label="E", r=0, b=1)
        edge2 = Hyperedge(uid=edge2_id, label="E", r=0, b=1)

        graph.add_hyperedge(edge1)
        graph.connect(edge1_id, v1.uid)
        graph.connect(edge1_id, new_vertex_id)

        graph.add_hyperedge(edge2)
        graph.connect(edge2_id, new_vertex_id)
        graph.connect(edge2_id, v2.uid)

        if self.DEBUG:
            print(f"[P4] Utworzono krawędź {edge1_id}: {v1.uid} -> {new_vertex_id}")
            print(f"[P4] Utworzono krawędź {edge2_id}: {new_vertex_id} -> {v2.uid}")

        graph.remove_node(match_node.uid)

        if self.DEBUG:
            print(f"[P4] Usunięto starą krawędź {match_node.uid}")

        print(f"-> P4: Podzielono krawędź brzegową {match_node.uid}, utworzono wierzchołek {new_vertex_id} i krawędzie {edge1_id}, {edge2_id}.")

    # def apply_rhs(self, graph: Graph, match_node: Hyperedge):
    #     # Get the two vertices of the edge
    #     vertices = graph.get_hyperedge_vertices(match_node.uid)
    #     v1, v2 = vertices[0], vertices[1]

    #     if self.DEBUG:
    #         print(f"[P4] Dzielę krawędź {match_node.uid} między wierzchołkami {v1.uid} i {v2.uid}")

    #     # Calculate midpoint
    #     mid_x = (v1.x + v2.x) / 2.0
    #     mid_y = (v1.y + v2.y) / 2.0

    #     # --- ZMIANA TUTAJ ---
    #     new_vertex_id = str(uuid.uuid4())

    #     # Create new vertex (not hanging, as it's on a boundary edge)
    #     new_vertex = Vertex(uid=new_vertex_id, x=mid_x, y=mid_y, hanging=False)
    #     graph.add_vertex(new_vertex)

    #     if self.DEBUG:
    #         print(f"[P4] Utworzono nowy wierzchołek {new_vertex_id} w ({mid_x}, {mid_y})")

    #     # --- I ZMIANA TUTAJ ---
    #     edge1_id = str(uuid.uuid4())
    #     edge2_id = str(uuid.uuid4())

    #     # Create two new edges with B=1, R=0
    #     edge1 = Hyperedge(uid=edge1_id, label="E", r=0, b=1)
    #     edge2 = Hyperedge(uid=edge2_id, label="E", r=0, b=1)

    #     graph.add_hyperedge(edge1)
    #     graph.connect(edge1_id, v1.uid)
    #     graph.connect(edge1_id, new_vertex_id)

    #     graph.add_hyperedge(edge2)
    #     graph.connect(edge2_id, new_vertex_id)
    #     graph.connect(edge2_id, v2.uid)

    #     if self.DEBUG:
    #         print(f"[P4] Utworzono krawędź {edge1_id}: {v1.uid} -> {new_vertex_id}")
    #         print(f"[P4] Utworzono krawędź {edge2_id}: {new_vertex_id} -> {v2.uid}")

    #     # Remove the old edge
    #     graph.remove_node(match_node.uid)

    #     if self.DEBUG:
    #         print(f"[P4] Usunięto starą krawędź {match_node.uid}")

    #     print(f"-> P4: Podzielono krawędź brzegową {match_node.uid}, utworzono wierzchołek {new_vertex_id} i krawędzie {edge1_id}, {edge2_id}.")

    # def apply_rhs(self, graph: Graph, match_node: Hyperedge):
    #     # Get the two vertices of the edge
    #     vertices = graph.get_hyperedge_vertices(match_node.uid)
    #     v1, v2 = vertices[0], vertices[1]

    #     if self.DEBUG:
    #         print(f"[P4] Dzielę krawędź {match_node.uid} między wierzchołkami {v1.uid} i {v2.uid}")

    #     # Calculate midpoint
    #     mid_x = (v1.x + v2.x) / 2.0
    #     mid_y = (v1.y + v2.y) / 2.0

    #     # Generate new vertex ID
    #     # Simple approach: use max existing vertex ID + 1
    #     max_vertex_id = max(
    #         [node_id for node_id, data in graph._nx_graph.nodes(data=True)
    #          if isinstance(data.get("data"), Vertex)],
    #         default=0
    #     )
    #     new_vertex_id = max_vertex_id + 1

    #     # Create new vertex (not hanging, as it's on a boundary edge)
    #     new_vertex = Vertex(uid=new_vertex_id, x=mid_x, y=mid_y, hanging=False)
    #     graph.add_vertex(new_vertex)

    #     if self.DEBUG:
    #         print(f"[P4] Utworzono nowy wierzchołek {new_vertex_id} w ({mid_x}, {mid_y})")

    #     # Generate new edge IDs
    #     max_edge_id = max(
    #         [int(str(node_id).replace("E", ""))
    #          for node_id, data in graph._nx_graph.nodes(data=True)
    #          if isinstance(data.get("data"), Hyperedge) and str(node_id).startswith("E")],
    #         default=0
    #     )
    #     edge1_id = f"E{max_edge_id + 1}"
    #     edge2_id = f"E{max_edge_id + 2}"

    #     # Create two new edges with B=1, R=0
    #     edge1 = Hyperedge(uid=edge1_id, label="E", r=0, b=1)
    #     edge2 = Hyperedge(uid=edge2_id, label="E", r=0, b=1)

    #     graph.add_hyperedge(edge1)
    #     graph.connect(edge1_id, v1.uid)
    #     graph.connect(edge1_id, new_vertex_id)

    #     graph.add_hyperedge(edge2)
    #     graph.connect(edge2_id, new_vertex_id)
    #     graph.connect(edge2_id, v2.uid)

    #     if self.DEBUG:
    #         print(f"[P4] Utworzono krawędź {edge1_id}: {v1.uid} -> {new_vertex_id}")
    #         print(f"[P4] Utworzono krawędź {edge2_id}: {new_vertex_id} -> {v2.uid}")

    #     # Remove the old edge
    #     graph.remove_node(match_node.uid)

    #     if self.DEBUG:
    #         print(f"[P4] Usunięto starą krawędź {match_node.uid}")

    #     print(f"-> P4: Podzielono krawędź brzegową {match_node.uid}, utworzono wierzchołek {new_vertex_id} i krawędzie {edge1_id}, {edge2_id}.")

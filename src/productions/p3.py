from typing import List, Union
from ..graph import Graph
from ..elements import Hyperedge, Vertex
from .production import Production


class ProductionP3(Production):
    """
    P3: Podział krawędzi współdzielonej (B=0), która jest oznaczona do podziału (R=1).
    Aktualizuje R starej krawędzi (R: 1->0), dodaje wierzchołek V w środku
    i tworzy 2 nowe krawędzie łączące V z końcami (R=0, B=0).
    Stara krawędź POZOSTAJE (zgodnie z diagramem - 3 krawędzie E po RHS).
    """

    def find_lhs(self, graph: Graph, target_id: Union[int, str] = None) -> List[Hyperedge]:
        candidates = []
        for node_id, data in graph.nx_graph.nodes(data=True):
            he = data.get("data")

            # 1. Musi to być Hyperedge
            if not isinstance(he, Hyperedge):
                continue

            # 2. Opcjonalne filtrowanie po ID
            if target_id is not None and he.uid != target_id:
                continue

            # 3. Musi mieć etykietę 'E'
            if he.label != "E":
                continue

            # 4. Musi mieć R=1 (oznaczona do podziału)
            if he.r != 1:
                continue

            # 5. Musi mieć B=0 (krawędź wewnętrzna/współdzielona)
            if he.b != 0:
                continue

            # 6. Musi łączyć dokładnie 2 wierzchołki
            vertices = graph.get_hyperedge_vertices(he.uid)
            if len(vertices) != 2:
                continue

            candidates.append(he)

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        # Pobieramy wierzchołki starej krawędzi
        vertices = graph.get_hyperedge_vertices(match_node.uid)
        v1, v2 = vertices[0], vertices[1]

        # 1. Obliczamy współrzędne nowego wierzchołka (środek)
        new_x = (v1.x + v2.x) / 2.0
        new_y = (v1.y + v2.y) / 2.0
        max_vertex_id = max(
            [node_id for node_id, data in graph._nx_graph.nodes(data=True) 
             if isinstance(data.get("data"), Vertex)],
            default=0
        )
        # Tworzymy unikalne ID dla nowych elementów
        new_v_uid = max_vertex_id + 1
        max_edge_id = max(
            [int(str(node_id).replace("E", "")) 
             for node_id, data in graph._nx_graph.nodes(data=True) 
             if isinstance(data.get("data"), Hyperedge) and str(node_id).startswith("E")],
            default=0
        )
        new_e1_uid = f"E{max_edge_id + 1}"
        new_e2_uid = f"E{max_edge_id + 2}"

        # 2. Dodajemy nowy wierzchołek (wiszący)
        # Zgodnie z P3, ten wierzchołek powstaje na krawędzi.
        # W kontekście PolyDPG często staje się on hanging node dla sąsiada.
        new_vertex = Vertex(uid=new_v_uid, x=new_x, y=new_y, hanging=True)
        graph.add_vertex(new_vertex)

        # 3. Aktualizujemy starą krawędź - ZOSTAJE, tylko zmienia R: 1->0
        # Zgodnie z diagramem stara krawędź (1-2) pozostaje z zaktualizowanym R
        graph.update_hyperedge(match_node.uid, r=0)

        # 4. Tworzymy dwie nowe krawędzie (R=0, B=0) łączące V z końcami
        # Te są dodatkowymi połączeniami do nowego wierzchołka V
        e1 = Hyperedge(uid=new_e1_uid, label="E", r=0, b=0)
        e2 = Hyperedge(uid=new_e2_uid, label="E", r=0, b=0)

        graph.add_hyperedge(e1)
        graph.add_hyperedge(e2)

        # 5. Łączymy nowe krawędzie
        # E1 łączy v1 i nowy wierzchołek
        graph.connect(new_e1_uid, v1.uid)
        graph.connect(new_e1_uid, new_v_uid)

        # E2 łączy nowy wierzchołek i v2
        graph.connect(new_e2_uid, new_v_uid)
        graph.connect(new_e2_uid, v2.uid)

        print(f"-> P3: Zaktualizowano {match_node.uid} (R->0) i dodano V z krawędziami {new_e1_uid}, {new_e2_uid}.")

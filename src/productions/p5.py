import math
import uuid
from typing import List, Union, Optional, Tuple
from ..graph import Graph
from ..elements import Hyperedge, Vertex
from .production import Production


class ProductionP5(Production):
    """
    P5: Podział elementu czworokątnego (Q, R=1), jeśli wszystkie jego krawędzie
    zostały wcześniej podzielone (istnieją węzły wiszące na każdym boku).
    """

    DEBUG = True

    def find_lhs(self, graph: Graph, target_id: Union[int, str] = None) -> List[Hyperedge]:
        candidates = []
        for node_id, data in graph.nx_graph.nodes(data=True):
            he = data.get("data")

            if self.DEBUG:
                print(f"[P5] Sprawdzam węzeł: {he}")

            # 1. Musi to być Hyperedge typu 'Q' z R=1
            if not isinstance(he, Hyperedge) or he.label != 'Q' or he.r != 1:
                if self.DEBUG and isinstance(he, Hyperedge):
                    print(f"[P5] - pomijam, nie jest Q z R=1 (label={he.label}, R={he.r}).")
                continue

            # 2. Opcjonalne filtrowanie po ID
            if target_id is not None and he.uid != target_id:
                if self.DEBUG:
                    print(f"[P5] - pomijam, nie jest celem (target_id={target_id}).")
                continue

            # 3. Musi mieć dokładnie 4 narożniki (wierzchołki)
            corners = graph.get_hyperedge_vertices(he.uid)
            if self.DEBUG:
                print(f"[P5] - znalezione wierzchołki: {len(corners)}")
            if len(corners) != 4:
                if self.DEBUG:
                    print(f"[P5] - pomijam, nie ma 4 wierzchołków (ma {len(corners)}).")
                continue

            # 4. Sortujemy narożniki geometrycznie (przeciwnie do wskazówek zegara),
            # Jest to niezbędne, aby sprawdzić sąsiedztwo na bokach
            sorted_corners = self._sort_vertices_counter_clockwise(corners)
            if self.DEBUG:
                print(f"[P5] - posortowane wierzchołki: {[v.uid for v in sorted_corners]}")

            # 5. Sprawdzamy warunek "all edges are broken"
            # Pomiędzy każdą parą sąsiednich narożników musi istnieć "midpoint" (węzeł wiszący)
            # połączony krawędziami E.
            is_broken = True
            for i in range(4):
                v_curr = sorted_corners[i]
                v_next = sorted_corners[(i + 1) % 4]

                midpoint = self._find_midpoint_between(graph, v_curr, v_next)
                if self.DEBUG:
                    print(f"[P5] - szukam midpoint między {v_curr.uid} a {v_next.uid}: {midpoint.uid if midpoint else 'BRAK'}")
                if midpoint is None:
                    is_broken = False
                    if self.DEBUG:
                        print(f"[P5] - brak midpoint między {v_curr.uid} a {v_next.uid}, krawędź nie jest złamana.")
                    break

            if is_broken:
                if self.DEBUG:
                    print(f"[P5] - znaleziono kandydata: {he}")
                candidates.append(he)
            elif self.DEBUG:
                print("[P5] - pomijam, nie wszystkie krawędzie są złamane.")

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        if self.DEBUG:
            print(f"[P5] Zaczynamy apply_rhs dla {match_node.uid}")
        # 1. Pobieramy i sortujemy narożniki starego Q
        corners = graph.get_hyperedge_vertices(match_node.uid)
        corners = self._sort_vertices_counter_clockwise(corners)
        if self.DEBUG:
            print(f"[P5] - posortowane narożniki: {[v.uid for v in corners]}")

        # c1..c4 to narożniki 1, 2, 3, 4 z diagramu
        c1, c2, c3, c4 = corners[0], corners[1], corners[2], corners[3]

        # 2. Znajdujemy istniejące węzły środkowe (5, 6, 7, 8 z diagramu).
        # Zakładamy, że find_lhs już zweryfikował ich istnienie
        m1 = self._find_midpoint_between(graph, c1, c2)  # między 1 a 2
        m2 = self._find_midpoint_between(graph, c2, c3)  # między 2 a 3
        m3 = self._find_midpoint_between(graph, c3, c4)  # między 3 a 4
        m4 = self._find_midpoint_between(graph, c4, c1)  # między 4 a 1
        if self.DEBUG:
            print(f"[P5] - midpoints: {[m.uid if m else 'BRAK' for m in [m1, m2, m3, m4]]}")

        # 3. Obliczamy współrzędne nowego centrum (węzeł 9 - nieoznaczony, środek krzyża)
        center_x = (c1.x + c2.x + c3.x + c4.x) / 4.0
        center_y = (c1.y + c2.y + c3.y + c4.y) / 4.0

        numeric_vertex_ids = []
        for node_id, data in graph.nx_graph.nodes(data=True):
            if isinstance(data.get("data"), Vertex) and isinstance(node_id, int):
                numeric_vertex_ids.append(node_id)
        
        max_vertex_id = max(numeric_vertex_ids, default=0)
        print(f"Max vertex ID: {max_vertex_id}")
        center_uid = max_vertex_id + 1
        center_vertex = Vertex(uid=center_uid, x=center_x, y=center_y, hanging=False)
        graph.add_vertex(center_vertex)
        if self.DEBUG:
            print(f"[P5] - dodano centrum: {center_uid} ({center_x}, {center_y})")

        # 4. Usuwamy stary element Q (tylko hyperedge, wierzchołki zostają)
        graph.remove_node(match_node.uid)
        if self.DEBUG:
            print(f"[P5] - usunięto stary element: {match_node.uid}")

        # 5. Tworzymy 4 nowe elementy Q (ćwiartki) z R=0
        # Find max numeric Q ID
        numeric_q_ids = []
        for node_id, data in graph._nx_graph.nodes(data=True):
            if isinstance(data.get("data"), Hyperedge):
                # Try to extract numeric part from Q IDs like "Q12"
                node_str = str(node_id)
                if node_str.startswith("Q"):
                    try:
                        numeric_part = int(node_str[1:])
                        numeric_q_ids.append(numeric_part)
                    except ValueError:
                        pass  # Skip non-numeric Q IDs
        
        max_q_id = max(numeric_q_ids, default=0)
        new_q_ids = [f"Q{max_q_id + i}" for i in range(1, 5)]

        # Definiujemy grupy wierzchołków dla nowych Q (zgodnie z ruchem wskazówek zegara lub CCW)
        # Ważne, aby zachować spójność topologiczną.
        # Q1: c1 - m1 - center - m4
        q1_nodes = [c1, m1, center_vertex, m4]
        # Q2: m1 - c2 - m2 - center
        q2_nodes = [m1, c2, m2, center_vertex]
        # Q3: center - m2 - c3 - m3
        q3_nodes = [center_vertex, m2, c3, m3]
        # Q4: m4 - center - m3 - c4
        q4_nodes = [m4, center_vertex, m3, c4]

        quads_nodes = [q1_nodes, q2_nodes, q3_nodes, q4_nodes]

        for q_id, nodes in zip(new_q_ids, quads_nodes):
            new_q = Hyperedge(uid=q_id, label='Q', r=0, b=0)  # R=0 po podziale
            graph.add_hyperedge(new_q)
            for node in nodes:
                graph.connect(q_id, node.uid)
            if self.DEBUG:
                print(f"[P5] - dodano nowy element Q: {q_id} z wierzchołkami {[n.uid for n in nodes]}")

        # 6. Tworzymy 4 nowe krawędzie wewnętrzne E (R=0, B=0)
        # Łączą one węzły środkowe (m1..m4) z nowym centrum
        midpoints = [m1, m2, m3, m4]
        for i, mid_node in enumerate(midpoints):
            # Find max numeric E ID
            numeric_e_ids = []
            for node_id, data in graph._nx_graph.nodes(data=True):
                if isinstance(data.get("data"), Hyperedge):
                    # Try to extract numeric part from E IDs like "E12"
                    node_str = str(node_id)
                    if node_str.startswith("E"):
                        try:
                            numeric_part = int(node_str[1:])
                            numeric_e_ids.append(numeric_part)
                        except ValueError:
                            pass  # Skip non-numeric E IDs
            
            max_e_id = max(numeric_e_ids, default=0)
            e_id = f"E{max_e_id + 1}"
            new_e = Hyperedge(uid=e_id, label='E', r=0, b=0)  # B=0 bo wewnętrzne
            graph.add_hyperedge(new_e)
            graph.connect(e_id, mid_node.uid)
            graph.connect(e_id, center_vertex.uid)
            if self.DEBUG:
                print(f"[P5] - dodano krawędź wewnętrzną: {e_id} ({mid_node.uid} - {center_vertex.uid})")

        print(f"-> P5: Podzielono Q {match_node.uid} na 4 mniejsze i dodano centrum {center_uid}.")

    # --- Metody pomocnicze ---

    def _sort_vertices_counter_clockwise(self, vertices: List[Vertex]) -> List[Vertex]:
        """Sortuje wierzchołki geometrycznie wokół ich środka ciężkości."""
        if not vertices:
            return []

        # Środek ciężkości
        cx = sum(v.x for v in vertices) / len(vertices)
        cy = sum(v.y for v in vertices) / len(vertices)

        def angle_from_center(v):
            return math.atan2(v.y - cy, v.x - cx)

        return sorted(vertices, key=angle_from_center)

    def _find_midpoint_between(self, graph: Graph, v1: Vertex, v2: Vertex) -> Optional[Vertex]:
        """
        Znajduje wierzchołek leżący "pomiędzy" v1 i v2.
        Definicja "pomiędzy": Istnieje ścieżka v1 --(E)-- v_mid --(E)-- v2.
        """
        # Pobieramy krawędzie (Hyperedges typu E) podłączone do v1
        v1_edges = [he for he in graph.get_vertex_hyperedges(v1.uid) if he.label == 'E']

        # Pobieramy krawędzie podłączone do v2
        v2_edges = [he for he in graph.get_vertex_hyperedges(v2.uid) if he.label == 'E']

        # Szukamy wspólnego sąsiada (wierzchołka) dla tych krawędzi
        for e1 in v1_edges:
            neighbors_e1 = graph.get_hyperedge_vertices(e1.uid)
            for potential_mid in neighbors_e1:
                # POPRAWKA: Punkt środkowy nie może być żadnym z narożników!
                if potential_mid == v1 or potential_mid == v2:
                    continue

                # Dodatkowo możemy sprawdzić, czy jest wiszący (opcjonalne, ale zgodne z teorią)
                # CO TO KURWA JEST? PSUJE PRODUKCJE!
                # if not potential_mid.hanging:
                #     continue

                # Sprawdzamy, czy ten potential_mid łączy się z v2 przez inną krawędź
                for e2 in v2_edges:
                    if potential_mid in graph.get_hyperedge_vertices(e2.uid):
                        # Znaleziono strukturę V1-E-Mid-E-V2
                        return potential_mid

        return None
import math
from typing import List, Union, Optional, Tuple
from ..graph import Graph
from ..elements import Hyperedge, Vertex
from .production import Production


class ProductionP11(Production):
    """
    P11: Podział elementu sześciokątnego (S, R=1), jeśli wszystkie jego krawędzie
    zostały wcześniej podzielone (istnieją węzły wiszące na każdym boku).
    """
    
    DEBUG = True

    def find_lhs(
        self, graph: Graph, target_id: Union[int, str] = None
    ) -> List[Hyperedge]:
        candidates = []
        for node_id, data in graph.nx_graph.nodes(data=True):
            he = data.get("data")
            
            if self.DEBUG:
                print(f"[P11] Sprawdzam węzeł: {he}")

            # 1. Musi to być Hyperedge typu 'S' z R=1
            if not isinstance(he, Hyperedge) or he.label != "S" or he.r != 1:
                if self.DEBUG and isinstance(he, Hyperedge):
                    print(f"[P11] - pomijam, nie jest S z R=1 (label={he.label}, R={he.r}).")
                continue

            # 2. Opcjonalne filtrowanie po ID
            if target_id is not None and he.uid != target_id:
                if self.DEBUG:
                    print(f"[P11] - pomijam, nie jest celem (target_id={target_id}).")
                continue

            # 3. Musi mieć dokładnie 6 wierzchołków
            corners = graph.get_hyperedge_vertices(he.uid)
            if self.DEBUG:
                print(f"[P11] - znalezione wierzchołki: {len(corners)}")
            if len(corners) != 6:
                if self.DEBUG:
                    print(f"[P11] - pomijam, nie ma 6 wierzchołków (ma {len(corners)}).")
                continue

            # 4. Sortujemy narożniki geometrycznie (przeciwnie do wskazówek zegara),
            # Jest to niezbędne, aby sprawdzić sąsiedztwo na bokach
            sorted_corners = self._sort_vertices_counter_clockwise(corners)
            if self.DEBUG:
                print(f"[P11] - posortowane wierzchołki: {[v.uid for v in sorted_corners]}")

            # 5. Sprawdzamy warunek "all edges are broken"
            # Pomiędzy każdą parą sąsiednich narożników musi istnieć "midpoint" (węzeł wiszący)
            # połączony krawędziami E.
            is_broken = True
            for i in range(6):
                v_curr = sorted_corners[i]
                v_next = sorted_corners[(i + 1) % 6]

                midpoint = self._find_midpoint_between(graph, v_curr, v_next)
                if self.DEBUG:
                    print(f"[P11] - szukam midpoint między {v_curr.uid} a {v_next.uid}: {midpoint.uid if midpoint else 'BRAK'}")
                if midpoint is None:
                    is_broken = False
                    if self.DEBUG:
                        print(f"[P11] - brak midpoint między {v_curr.uid} a {v_next.uid}, S nie jest 'wszystko złamane'")
                    break

            if is_broken:
                if self.DEBUG:
                    print(f"[P11] - znaleziono kandydata: {he}")
                candidates.append(he)
            elif self.DEBUG:
                print(f"[P11] - pomijam, nie wszystkie krawędzie są złamane.")

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        if self.DEBUG:
            print(f"[P11] Zaczynamy apply_rhs dla {match_node.uid}")
        
        # 1. Pobieramy i sortujemy narożniki starego Q
        corners = graph.get_hyperedge_vertices(match_node.uid)
        corners = self._sort_vertices_counter_clockwise(corners)
        if self.DEBUG:
            print(f"[P11] - posortowane narożniki: {[v.uid for v in corners]}")

        # c1..c6 to narożniki 1, 2, 3, 4, 5, 6 z diagramu

        # 2. Znajdujemy istniejące węzły środkowe (7, 8, 9, 10, 11, 12 z diagramu).
        # Zakładamy, że find_lhs już zweryfikował ich istnienie
        m = [
            self._find_midpoint_between(graph, corners[i], corners[(i + 1) % 6])
            for i in range(6)
        ]
        if self.DEBUG:
            print(f"[P11] - znalezione midpoints: {[mp.uid if mp else 'BRAK' for mp in m]}")

        # 3. Obliczamy współrzędne nowego centrum (węzeł 13 - nieoznaczony, środek krzyża)
        center_x = sum(c.x for c in corners) / 6.0
        center_y = sum(c.y for c in corners) / 6.0

        max_vertex_id = max(
            [node_id for node_id, data in graph._nx_graph.nodes(data=True) 
             if isinstance(data.get("data"), Vertex)],
            default=0
        )
        center_uid = max_vertex_id + 1
        center_vertex = Vertex(uid=center_uid, x=center_x, y=center_y, hanging=False)
        graph.add_vertex(center_vertex)
        if self.DEBUG:
            print(f"[P11] - dodano wierzchołek centrum: {center_uid} ({center_x}, {center_y})")

        # 4. Usuwamy stary element Q (tylko hyperedge, wierzchołki zostają)
        graph.remove_node(match_node.uid)
        if self.DEBUG:
            print(f"[P11] - usunięto stary element: {match_node.uid}")

        # 5. Tworzymy 6 nowych elementów Q z R=0
        # Nazewnictwo ID: Q_old_0, Q_old_1...
        max_edge_id = max(
            [int(str(node_id).replace("Q", "")) 
             for node_id, data in graph._nx_graph.nodes(data=True) 
             if isinstance(data.get("data"), Hyperedge) and str(node_id).startswith("Q")],
            default=0
        )
        new_q_ids = [f"Q{max_edge_id + i}" for i in range(1,7)]

        # Definiujemy grupy wierzchołków dla nowych Q (zgodnie z ruchem wskazówek zegara lub CCW)
        # Ważne, aby zachować spójność topologiczną.

        quads_nodes = [[corners[i], m[i], center_vertex, m[i - 1]] for i in range(6)]

        for q_id, nodes in zip(new_q_ids, quads_nodes):
            new_q = Hyperedge(uid=q_id, label="Q", r=0, b=0)  # R=0 po podziale
            graph.add_hyperedge(new_q)
            for node in nodes:
                graph.connect(q_id, node.uid)
            if self.DEBUG:
                print(f"[P11] - dodano nowy element Q: {q_id} z wierzchołkami {[n.uid for n in nodes]}")

        # 6. Tworzymy 6 nowych krawędzi wewnętrznych E (R=0, B=0)
        # Łączą one węzły środkowe (m1..m6) z nowym centrum
        midpoints = m
        for i, mid_node in enumerate(midpoints):
            max_edge_id = max(
                [int(str(node_id).replace("E", "")) 
                for node_id, data in graph._nx_graph.nodes(data=True) 
                if isinstance(data.get("data"), Hyperedge) and str(node_id).startswith("E")],
                default=0
            )
            e_id = f"E{max_edge_id + 1}"
            new_e = Hyperedge(uid=e_id, label="E", r=0, b=0)  # B=0 bo wewnętrzne
            graph.add_hyperedge(new_e)
            graph.connect(e_id, mid_node.uid)
            graph.connect(e_id, center_vertex.uid)
            if self.DEBUG:
                print(f"[P11] - dodano nową krawędź wewnętrzną: {e_id} ({mid_node.uid} - {center_vertex.uid})")

        print(
            f"-> P11: Podzielono Q {match_node.uid} na 6 mniejszych i dodano centrum {center_uid}."
        )

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

    def _find_midpoint_between(
        self, graph: Graph, v1: Vertex, v2: Vertex
    ) -> Optional[Vertex]:
        """
        Znajduje wierzchołek leżący "pomiędzy" v1 i v2.
        Definicja "pomiędzy": Istnieje ścieżka v1 --(E)-- v_mid --(E)-- v2.
        """
        # Pobieramy krawędzie (Hyperedges typu E) podłączone do v1
        v1_edges = [he for he in graph.get_vertex_hyperedges(v1.uid) if he.label == "E"]
        print(f"v1_edges: {[he.uid for he in v1_edges]}")
        # Pobieramy krawędzie podłączone do v2
        v2_edges = [he for he in graph.get_vertex_hyperedges(v2.uid) if he.label == "E"]
        print(f"v2_edges: {[he.uid for he in v2_edges]}")

        # Szukamy wspólnego sąsiada (wierzchołka) dla tych krawędzi
        for e1 in v1_edges:
            neighbors_e1 = graph.get_hyperedge_vertices(e1.uid)
            print(f"neighbors_e1 for edge {e1.uid}: {[v.uid for v in neighbors_e1]}")
            for potential_mid in neighbors_e1:
                # POPRAWKA: Punkt środkowy nie może być żadnym z narożników!
                if potential_mid == v1 or potential_mid == v2:
                    continue

                # Dodatkowo możemy sprawdzić, czy jest wiszący (opcjonalne, ale zgodne z teorią)
                # Co to kurwa jest? Psuje produkcje!
                # if not potential_mid.hanging:
                #     print(f"potential_mid {potential_mid.uid} nie jest hanging, pomijam.")
                #     continue

                # Sprawdzamy, czy ten potential_mid łączy się z v2 przez inną krawędź
                for e2 in v2_edges:
                    if potential_mid in graph.get_hyperedge_vertices(e2.uid):
                        # Znaleziono strukturę V1-E-Mid-E-V2
                        return potential_mid

        return None

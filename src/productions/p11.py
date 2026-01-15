import math
from typing import List, Union, Optional, Tuple
from ..graph import Graph
from ..elements import Hyperedge, Vertex
from .production import Production


class ProductionP11(Production):
    """
    P11: Podział elementu sześciokątnego (Q, R=1), jeśli wszystkie jego krawędzie
    zostały wcześniej podzielone (istnieją węzły wiszące na każdym boku).
    """

    def find_lhs(
        self, graph: Graph, target_id: Union[int, str] = None
    ) -> List[Hyperedge]:
        candidates = []
        for node_id, data in graph.nx_graph.nodes(data=True):
            he = data.get("data")

            # 1. Musi to być Hyperedge typu 'Q' z R=1
            if not isinstance(he, Hyperedge) or he.label != "Q" or he.r != 1:
                continue

            # 2. Opcjonalne filtrowanie po ID
            if target_id is not None and he.uid != target_id:
                continue

            # 3. Musi mieć dokładnie 6 narożników (wierzchołków)
            corners = graph.get_hyperedge_vertices(he.uid)
            if len(corners) != 6:
                continue

            # 4. Sortujemy narożniki geometrycznie (przeciwnie do wskazówek zegara),
            # Jest to niezbędne, aby sprawdzić sąsiedztwo na bokach
            sorted_corners = self._sort_vertices_counter_clockwise(corners)

            # 5. Sprawdzamy warunek "all edges are broken"
            # Pomiędzy każdą parą sąsiednich narożników musi istnieć "midpoint" (węzeł wiszący)
            # połączony krawędziami E.
            is_broken = True
            for i in range(6):
                v_curr = sorted_corners[i]
                v_next = sorted_corners[(i + 1) % 6]

                midpoint = self._find_midpoint_between(graph, v_curr, v_next)
                if midpoint is None:
                    is_broken = False
                    break

            if is_broken:
                candidates.append(he)

        return candidates

    def apply_rhs(self, graph: Graph, match_node: Hyperedge):
        # 1. Pobieramy i sortujemy narożniki starego Q
        corners = graph.get_hyperedge_vertices(match_node.uid)
        corners = self._sort_vertices_counter_clockwise(corners)

        # c1..c6 to narożniki 1, 2, 3, 4, 5, 6 z diagramu

        # 2. Znajdujemy istniejące węzły środkowe (7, 8, 9, 10, 11, 12 z diagramu).
        # Zakładamy, że find_lhs już zweryfikował ich istnienie
        m = [
            self._find_midpoint_between(graph, corners[i], corners[(i + 1) % 6])
            for i in range(6)
        ]

        # 3. Obliczamy współrzędne nowego centrum (węzeł 13 - nieoznaczony, środek krzyża)
        center_x = sum(c.x for c in corners) / 6.0
        center_y = sum(c.y for c in corners) / 6.0

        center_uid = f"{match_node.uid}_center"
        center_vertex = Vertex(uid=center_uid, x=center_x, y=center_y, hanging=False)
        graph.add_vertex(center_vertex)

        # 4. Usuwamy stary element Q (tylko hyperedge, wierzchołki zostają)
        graph.remove_node(match_node.uid)

        # 5. Tworzymy 6 nowych elementów Q z R=0
        # Nazewnictwo ID: Q_old_0, Q_old_1...
        new_q_ids = [f"{match_node.uid}_sub_Q{i}" for i in range(6)]

        # Definiujemy grupy wierzchołków dla nowych Q (zgodnie z ruchem wskazówek zegara lub CCW)
        # Ważne, aby zachować spójność topologiczną.

        quads_nodes = [[corners[i], m[i], center_vertex, m[i - 1]] for i in range(6)]

        for q_id, nodes in zip(new_q_ids, quads_nodes):
            new_q = Hyperedge(uid=q_id, label="Q", r=0, b=0)  # R=0 po podziale
            graph.add_hyperedge(new_q)
            for node in nodes:
                graph.connect(q_id, node.uid)

        # 6. Tworzymy 6 nowych krawędzi wewnętrznych E (R=0, B=0)
        # Łączą one węzły środkowe (m1..m6) z nowym centrum
        midpoints = m
        for i, mid_node in enumerate(midpoints):
            e_id = f"{match_node.uid}_inner_E{i}"
            new_e = Hyperedge(uid=e_id, label="E", r=0, b=0)  # B=0 bo wewnętrzne
            graph.add_hyperedge(new_e)
            graph.connect(e_id, mid_node.uid)
            graph.connect(e_id, center_vertex.uid)

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

        # Pobieramy krawędzie podłączone do v2
        v2_edges = [he for he in graph.get_vertex_hyperedges(v2.uid) if he.label == "E"]

        # Szukamy wspólnego sąsiada (wierzchołka) dla tych krawędzi
        for e1 in v1_edges:
            neighbors_e1 = graph.get_hyperedge_vertices(e1.uid)
            for potential_mid in neighbors_e1:
                # POPRAWKA: Punkt środkowy nie może być żadnym z narożników!
                if potential_mid == v1 or potential_mid == v2:
                    continue

                # Dodatkowo możemy sprawdzić, czy jest wiszący (opcjonalne, ale zgodne z teorią)
                if not potential_mid.hanging:
                    continue

                # Sprawdzamy, czy ten potential_mid łączy się z v2 przez inną krawędź
                for e2 in v2_edges:
                    if potential_mid in graph.get_hyperedge_vertices(e2.uid):
                        # Znaleziono strukturę V1-E-Mid-E-V2
                        return potential_mid

        return None

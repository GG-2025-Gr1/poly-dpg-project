import math
from typing import List, Union, Optional

from ..graph import Graph
from ..elements import Vertex, Hyperedge
from .production import Production

class ProductionP11(Production):
    """
    P11: Podział elementu sześciokątnego (Hexagon) na 6 czworokątów (Quad).
    Warunek: Element S ma R=1 oraz wszystkie jego krawędzie są już podzielone
    (istnieją wierzchołki pośrednie między narożnikami).
    """

    def find_lhs(self, graph: Graph, target_id: Union[int, str] = None) -> List[dict]:
        matches = []

        # Iterujemy po wszystkich węzłach w grafie
        for node_id, node_data in graph.nx_graph.nodes(data=True):
            hyperedge = node_data.get('data')

            # 1. Musi to być hiperkrawędź typu S
            if not isinstance(hyperedge, Hyperedge) or hyperedge.label != 'S':
                continue

            # 2. Jeśli podano target_id, sprawdzamy tylko ten ID
            if target_id is not None and hyperedge.uid != target_id:
                continue

            # 3. Musi mieć flagę R=1 (oznaczenie do refinacji)
            if hyperedge.r != 1:
                continue

            # 4. Pobieramy sąsiadujące wierzchołki (powinno być ich 6 - narożniki)
            corners = graph.get_hyperedge_vertices(hyperedge.uid)
            if len(corners) != 6:
                continue

            centroid_x = sum(v.x for v in corners) / 6
            centroid_y = sum(v.y for v in corners) / 6
            
            corners_sorted = sorted(
                corners, 
                key=lambda v: math.atan2(v.y - centroid_y, v.x - centroid_x)
            )

            # 5. Sprawdzamy czy WSZYSTKIE krawędzie są "połamane"
            midpoints = []
            is_valid_hex = True

            for i in range(6):
                v_curr = corners_sorted[i]
                v_next = corners_sorted[(i + 1) % 6]

                found_midpoint = self._find_midpoint(graph, v_curr, v_next)
                
                if found_midpoint is None:
                    is_valid_hex = False
                    break
                
                midpoints.append(found_midpoint)

            if is_valid_hex:
                matches.append({
                    's_hyperedge': hyperedge,
                    'corners': corners_sorted,
                    'midpoints': midpoints
                })

        return matches

    def _find_midpoint(self, graph: Graph, v1: Vertex, v2: Vertex) -> Optional[Vertex]:
        """Znajduje wierzchołek leżący 'pomiędzy' v1 i v2 w sensie grafowym (v1-E-mid-E-v2)."""
        neighbors_v1 = graph.get_neighbors(v1.uid)
        
        for mid in neighbors_v1:
            if mid.uid == v2.uid: 
                continue

            neighbors_v2 = graph.get_neighbors(v2.uid)
            # Check by UID to avoid object identity issues if reloaded
            if any(n.uid == mid.uid for n in neighbors_v2):
                edges_1 = graph.get_hyperedges_between_vertices(v1.uid, mid.uid)
                edges_2 = graph.get_hyperedges_between_vertices(v2.uid, mid.uid)
                
                has_e1 = any(e.label == 'E' for e in edges_1)
                has_e2 = any(e.label == 'E' for e in edges_2)

                if has_e1 and has_e2:
                    return mid
        return None

    def apply_rhs(self, graph: Graph, match: dict):
        s_edge = match['s_hyperedge']
        corners = match['corners']
        midpoints = match['midpoints']

        graph.remove_node(s_edge.uid)

        # 2. Obliczamy nowy wierzchołek centralny
        center_x = sum(v.x for v in corners) / 6
        center_y = sum(v.y for v in corners) / 6

        new_id_v = f"v_center_from_{s_edge.uid}" 
        center_vertex = Vertex(uid=new_id_v, x=center_x, y=center_y, hanging=False)
        graph.add_vertex(center_vertex)

        # 3. Tworzymy nowe elementy (6 czworokątów i 6 krawędzi wewnętrznych)
        for i in range(6):
            idx_curr = i
            idx_next = (i + 1) % 6
            
            # Wierzchołki dla nowego Q:
            # Prawidłowa kolejność (CCW): corner[next], mid[next], center, mid[curr] ?!
            # Sprawdźmy P8: corner[idx_next], mid[idx_curr], center, mid[idx_next]
            # Moment.
            # corner[idx_next] to wierzchołek "docelowy" krawędzi i.
            # mid[idx_curr] to środek krawędzi i.
            # mid[idx_next] to środek krawędzi i+1.
            # Więc Quad w rogu corner[i+1] (czyli corner[idx_next]) składa się z:
            # corner[i+1], mid[i], center, mid[i+1].
            # Odpowiada to liście: [v_corner, v_mid_prev, v_center, v_mid_next]
            
            v_corner = corners[idx_next]
            v_mid_prev = midpoints[idx_curr]
            v_center = center_vertex
            v_mid_next = midpoints[idx_next]
            
            q_uid = f"Q_{s_edge.uid}_{i}"
            new_q = Hyperedge(uid=q_uid, label='Q', r=0, b=0)
            graph.add_hyperedge(new_q)
            
            for v in [v_corner, v_mid_prev, v_center, v_mid_next]:
                graph.connect(q_uid, v.uid)
                
            e_uid = f"E_inner_{s_edge.uid}_{i}"
            new_e = Hyperedge(uid=e_uid, label='E', r=0, b=0)
            graph.add_hyperedge(new_e)
            graph.connect(e_uid, v_center.uid)
            graph.connect(e_uid, v_mid_next.uid)

        print(f"-> P11: Podział elementu S {s_edge.uid} na 6 czworokątów.")

import matplotlib
matplotlib.use('Agg')

import unittest
import matplotlib.pyplot as plt
import networkx as nx
import os

from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p8 import ProductionP8

class TestProductionP8(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()
        self.viz_dir = "visualizations/tests/test_p8"
        os.makedirs(self.viz_dir, exist_ok=True)

    def draw_graph(self, filename, title):
        """Pomocnicza funkcja do wizualizacji grafu."""
        plt.figure(figsize=(10, 10))
        G = self.graph.nx_graph
        pos = {}
        labels = {}
        colors = []
        
        for node_id, data in G.nodes(data=True):
            obj = data.get('data')
            if isinstance(obj, Vertex):
                pos[node_id] = (obj.x, obj.y)
                labels[node_id] = f"{obj.uid}"
                colors.append('skyblue')
            elif isinstance(obj, Hyperedge):
                neighbors = self.graph.get_hyperedge_vertices(obj.uid)
                if neighbors:
                    avg_x = sum(n.x for n in neighbors) / len(neighbors)
                    avg_y = sum(n.y for n in neighbors) / len(neighbors)
                    pos[node_id] = (avg_x, avg_y)
                else:
                    pos[node_id] = (0, 0)
                
                label_text = f"{obj.label}\nR={obj.r}\nB={obj.b}"
                labels[node_id] = label_text
                
                if obj.label == 'P': colors.append('orange')
                elif obj.label == 'Q': colors.append('lightgreen')
                elif obj.label == 'E': colors.append('yellow')
                else: colors.append('grey')

        nx.draw_networkx_nodes(G, pos, node_size=800, node_color=colors)
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title(title)
        plt.axis('equal')
        plt.savefig(os.path.join(self.viz_dir, filename))
        plt.close()

    def _create_valid_p8_unit(self, offset_x=0, offset_y=0, suffix=""):
        """
        Helper tworzący poprawną strukturę pod P8 (pięciokąt z R=1 i midpointami).
        Zwraca ID głównej hiperkrawędzi P.
        """
        corners = [
            Vertex(uid=f'v1{suffix}', x=0+offset_x, y=0+offset_y),
            Vertex(uid=f'v2{suffix}', x=2+offset_x, y=0+offset_y),
            Vertex(uid=f'v3{suffix}', x=2.5+offset_x, y=1.5+offset_y),
            Vertex(uid=f'v4{suffix}', x=1+offset_x, y=3+offset_y),
            Vertex(uid=f'v5{suffix}', x=-0.5+offset_x, y=1.5+offset_y)
        ]
        for v in corners:
            self.graph.add_vertex(v)

        midpoints = []
        for i in range(5):
            c1 = corners[i]
            c2 = corners[(i+1)%5]
            mid = Vertex(uid=f'm{i}{suffix}', x=(c1.x+c2.x)/2, y=(c1.y+c2.y)/2)
            midpoints.append(mid)
            self.graph.add_vertex(mid)

        for i in range(5):
            e1 = Hyperedge(uid=f'e_{i}_a{suffix}', label='E', r=0, b=1)
            e2 = Hyperedge(uid=f'e_{i}_b{suffix}', label='E', r=0, b=1)
            self.graph.add_hyperedge(e1)
            self.graph.add_hyperedge(e2)
            self.graph.connect(e1.uid, corners[i].uid)
            self.graph.connect(e1.uid, midpoints[i].uid)
            self.graph.connect(e2.uid, midpoints[i].uid)
            self.graph.connect(e2.uid, corners[(i+1)%5].uid)

        p_uid = f'P_main{suffix}'
        p_node = Hyperedge(uid=p_uid, label='P', r=1, b=0)
        self.graph.add_hyperedge(p_node)
        for v in corners:
            self.graph.connect(p_node.uid, v.uid)
            
        return p_uid

    def test_p8_isomorphic_happy_path(self):
        """Test podstawowy: Poprawny graf izomorficzny z LHS -> Oczekiwana transformacja."""
        self._create_valid_p8_unit()
        self.draw_graph("test_p8_scenariusz1_happy_path_przed.png", "Scenariusz 1: Poprawny graf (Przed)")

        prod = ProductionP8()
        matches = prod.find_lhs(self.graph)
        self.assertEqual(len(matches), 1)
        prod.apply(self.graph)

        self.draw_graph("test_p8_scenariusz1_happy_path_po.png", "Scenariusz 1: Poprawny graf (Po)")
        
        with self.assertRaises(ValueError):
            self.graph.get_hyperedge('P_main')
        quads = [n for n, d in self.graph.nx_graph.nodes(data=True) 
                 if isinstance(d.get('data'), Hyperedge) and d.get('data').label == 'Q']
        self.assertEqual(len(quads), 5)

    def test_p8_subgraph_embedding(self):
        """Test osadzenia: Dwa pięciokąty w jednym grafie."""
        self._create_valid_p8_unit(offset_x=0, suffix="_A")
        self._create_valid_p8_unit(offset_x=10, suffix="_B")
        
        self.draw_graph("test_p8_scenariusz2_subgraph_przed.png", "Scenariusz 2: Dwa podgrafy (Przed)")

        prod = ProductionP8()
        matches = prod.find_lhs(self.graph)
        self.assertEqual(len(matches), 2, "Powinno znaleźć 2 dopasowania")
        
        prod.apply(self.graph)
        
        self.draw_graph("test_p8_scenariusz2_subgraph_po.png", "Scenariusz 2: Dwa podgrafy (Po)")
        
        quads = [n for n, d in self.graph.nx_graph.nodes(data=True) 
                 if isinstance(d.get('data'), Hyperedge) and d.get('data').label == 'Q']
        self.assertEqual(len(quads), 10)

    def test_p8_wrong_label(self):
        """Test negatywny: Etykieta inna niż P (np. Q)."""
        p_uid = self._create_valid_p8_unit()
        self.graph.update_hyperedge(p_uid, label='Q') # Zmieniamy P na Q
        
        self.draw_graph("test_p8_scenariusz3_zla_etykieta.png", "Scenariusz 3: Zła etykieta (Q zamiast P)")

        prod = ProductionP8()
        matches = prod.find_lhs(self.graph)
        self.assertEqual(len(matches), 0, "Nie powinno znaleźć dopasowania dla etykiety Q")

    def test_p8_wrong_r_flag(self):
        """Test negatywny: Flaga R=0 zamiast R=1."""
        p_uid = self._create_valid_p8_unit()
        self.graph.update_hyperedge(p_uid, r=0) # Zmieniamy na R=0
        
        self.draw_graph("test_p8_scenariusz4_zle_R.png", "Scenariusz 4: Zła flaga (R=0)")
        
        prod = ProductionP8()
        matches = prod.find_lhs(self.graph)
        self.assertEqual(len(matches), 0, "Nie powinno znaleźć dopasowania dla R=0")

    def test_p8_missing_midpoint_edge(self):
        """
        Test specyficzny dla P8: Jeden bok NIE jest połamany.
        (Brak midpointa i podziału na dwie krawędzie E).
        """
        self._create_valid_p8_unit()
        
        # Psujemy strukturę: usuwamy midpoint m0 i jego krawędzie
        self.graph.remove_node('m0') 
        self.graph.remove_node('e_0_a')
        self.graph.remove_node('e_0_b')
        
        # Dodajemy "niepołamaną" krawędź bezpośrednią
        e_broken = Hyperedge(uid='e_bad', label='E', r=1, b=1)
        self.graph.add_hyperedge(e_broken)
        self.graph.connect(e_broken.uid, 'v1')
        self.graph.connect(e_broken.uid, 'v2')
        
        self.draw_graph("test_p8_scenariusz5_niepolamana_krawedz.png", "Scenariusz 5: Jeden bok nie jest podzielony")

        prod = ProductionP8()
        matches = prod.find_lhs(self.graph)
        self.assertEqual(len(matches), 0, "Nie powinno znaleźć dopasowania, gdy bok nie jest podzielony")

    def test_p8_missing_vertex(self):
        """Test negatywny: Brak jednego z narożników połączonych z P."""
        p_uid = self._create_valid_p8_unit()
        # Odłączamy jeden narożnik od P
        self.graph.remove_edge(p_uid, 'v5')
        
        self.draw_graph("test_p8_scenariusz6_brak_wierzcholka.png", "Scenariusz 6: Hiperkrawędź P nie jest połączona z v5")
        
        prod = ProductionP8()
        matches = prod.find_lhs(self.graph)
        self.assertEqual(len(matches), 0, "P musi mieć 5 narożników")

    def test_p8_target_id(self):
        """
        Test parametru target_id: W grafie są dwa elementy P gotowe do podziału,
        ale chcemy podzielić tylko jeden z nich.
        """
        # Tworzymy dwa niezależne elementy P8
        uid_a = self._create_valid_p8_unit(offset_x=0, suffix="_A")
        uid_b = self._create_valid_p8_unit(offset_x=10, suffix="_B")
        
        self.draw_graph("test_p8_scenariusz7_target_id_przed.png", "Scenariusz 7: Przed (celujemy tylko w A)")

        prod = ProductionP8()
        # Wyszukujemy tylko dla konkretnego ID (uid_a)
        matches = prod.find_lhs(self.graph, target_id=uid_a)
        
        self.assertEqual(len(matches), 1, "Powinno znaleźć tylko jedno dopasowanie dla podanego target_id")
        self.assertEqual(matches[0]['p_hyperedge'].uid, uid_a, "Znalezione dopasowanie powinno dotyczyć elementu A")
        
        prod.apply(self.graph, target_id=uid_a)
        
        self.draw_graph("test_p8_scenariusz7_target_id_po.png", "Scenariusz 7: Po (tylko A podzielone)")
        
        # Sprawdzenie: A powinno zniknąć (zostać podzielone), B powinno zostać bez zmian
        with self.assertRaises(ValueError):
            self.graph.get_hyperedge(uid_a) # A nie istnieje
            
        p_b = self.graph.get_hyperedge(uid_b) # B istnieje
        self.assertEqual(p_b.r, 1, "Element B powinien pozostać nienaruszony (R=1)")

    def test_p8_preserves_original_vertices(self):
        """
        Test weryfikujący, czy oryginalne wierzchołki (narożniki i midpointy)
        nie zostały usunięte ani przesunięte podczas produkcji.
        """
        self._create_valid_p8_unit()
        
        # Zapamiętujemy stan wierzchołków przed produkcją
        original_vertices = {}
        for n, d in self.graph.nx_graph.nodes(data=True):
            if isinstance(d.get('data'), Vertex):
                v = d.get('data')
                original_vertices[v.uid] = (v.x, v.y)
        
        prod = ProductionP8()
        prod.apply(self.graph)
        
        # Sprawdzamy stan po produkcji
        for uid, (old_x, old_y) in original_vertices.items():
            # Wierzchołek musi nadal istnieć
            try:
                v_new = self.graph.get_vertex(uid)
            except ValueError:
                self.fail(f"Wierzchołek {uid} został usunięty, a powinien zostać zachowany!")
            
            # Współrzędne muszą być identyczne
            self.assertEqual(v_new.x, old_x, f"Współrzędna X wierzchołka {uid} uległa zmianie")
            self.assertEqual(v_new.y, old_y, f"Współrzędna Y wierzchołka {uid} uległa zmianie")

    def test_p8_multiple_applications(self):
        """
        Test masowy: Sprawdza, czy w grafie zawierającym wiele (np. 4) elementów P8,
        wszystkie zostaną poprawnie przetworzone w jednym przebiegu.
        """
        # Tworzymy siatkę 4 elementów
        self._create_valid_p8_unit(offset_x=0, offset_y=0, suffix="_1")
        self._create_valid_p8_unit(offset_x=5, offset_y=0, suffix="_2")
        self._create_valid_p8_unit(offset_x=0, offset_y=5, suffix="_3")
        self._create_valid_p8_unit(offset_x=5, offset_y=5, suffix="_4")
        
        self.draw_graph("test_p8_scenariusz8_multi_przed.png", "Scenariusz 8: 4 elementy (Przed)")
        
        prod = ProductionP8()
        matches = prod.find_lhs(self.graph)
        self.assertEqual(len(matches), 4, "Powinno znaleźć 4 elementy do podziału")
        
        prod.apply(self.graph)
        
        self.draw_graph("test_p8_scenariusz8_multi_po.png", "Scenariusz 8: 4 elementy (Po)")
        
        # Weryfikacja: nie powinno być już żadnego P, powinno być 4 * 5 = 20 Q
        p_nodes = [n for n, d in self.graph.nx_graph.nodes(data=True) 
                   if isinstance(d.get('data'), Hyperedge) and d.get('data').label == 'P']
        self.assertEqual(len(p_nodes), 0, "Wszystkie elementy P powinny zostać przetworzone")
        
        q_nodes = [n for n, d in self.graph.nx_graph.nodes(data=True) 
                   if isinstance(d.get('data'), Hyperedge) and d.get('data').label == 'Q']
        self.assertEqual(len(q_nodes), 20, "Powinno powstać 20 elementów Q (4 elementy * 5)")

if __name__ == '__main__':
    unittest.main()
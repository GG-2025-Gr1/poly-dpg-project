import math

from src.graph import Graph
from src.elements import Vertex, Hyperedge


def get_2x2_grid_graph():
    """
    Tworzy siatkę 2x2 elementy (4 czworokąty).

    Układ wierzchołków (ID):
    7 -- 8 -- 9  (y=2.0)
    | Q3 | Q4 |
    4 -- 5 -- 6  (y=1.0)
    | Q1 | Q2 |
    1 -- 2 -- 3  (y=0.0)
    """
    g = Graph()

    # --- 1. Wierzchołki (Vertex) ---
    # Generujemy 9 wierzchołków w siatce 3x3 punkty
    vertices_data = [
        (1, 0.0, 0.0),
        (2, 1.0, 0.0),
        (3, 2.0, 0.0),  # Rząd dolny
        (4, 0.0, 1.0),
        (5, 1.0, 1.0),
        (6, 2.0, 1.0),  # Rząd środkowy
        (7, 0.0, 2.0),
        (8, 1.0, 2.0),
        (9, 2.0, 2.0),  # Rząd górny
    ]

    for uid, x, y in vertices_data:
        g.add_vertex(Vertex(uid=uid, x=x, y=y))

    # --- 2. Elementy Wnętrza (Q) ---
    # Definiujemy 4 elementy. Lewy-górny to Q3.
    # Atrybut R=0 na starcie.
    quads = [
        Hyperedge(uid="Q1", label="Q", r=0, b=0),  # Lewy-dół
        Hyperedge(uid="Q2", label="Q", r=0, b=0),  # Prawy-dół
        Hyperedge(uid="Q3", label="Q", r=0, b=0),  # Lewy-góra (TARGET)
        Hyperedge(uid="Q4", label="Q", r=0, b=0),  # Prawy-góra
    ]
    for q in quads:
        g.add_hyperedge(q)

    # Definicja połączeń Q z wierzchołkami (kolejność zazwyczaj przeciwna do ruchu wskazówek zegara lub zgodna)
    q_conns = {
        "Q1": [1, 2, 5, 4],
        "Q2": [2, 3, 6, 5],
        "Q3": [4, 5, 8, 7],
        "Q4": [5, 6, 9, 8],
    }
    for q_uid, v_ids in q_conns.items():
        for v_id in v_ids:
            g.connect(q_uid, v_id)

    # --- 3. Krawędzie (E) ---
    # Dodajemy krawędzie, aby graf był kompletny (ważne: krawędzie wewnętrzne są współdzielone!)
    # Format: (ID, v1, v2, Boundary_Flag)
    edges_data = [
        # Zewnętrzne (Boundary B=1)
        ("E1", 1, 2, 1),
        ("E2", 2, 3, 1),  # Dół
        ("E3", 3, 6, 1),
        ("E4", 6, 9, 1),  # Prawa
        ("E5", 9, 8, 1),
        ("E6", 8, 7, 1),  # Góra
        ("E7", 7, 4, 1),
        ("E8", 4, 1, 1),  # Lewa
        # Wewnętrzne (Internal B=0) - to są krawędzie współdzielone między Q
        (
            "E9",
            4,
            5,
            0,
        ),  # Pozioma środek (między Q1/Q3 a Q2/Q4 - nie, to między Q1 a Q3)
        ("E10", 5, 6, 0),  # Pozioma środek
        ("E11", 2, 5, 0),  # Pionowa środek
        ("E12", 5, 8, 0),  # Pionowa środek
    ]

    for eid, v1, v2, b_flag in edges_data:
        e = Hyperedge(uid=eid, label="E", r=0, b=b_flag)
        g.add_hyperedge(e)
        g.connect(eid, v1)
        g.connect(eid, v2)

    return g


def get_hexagonal_test_graph():
    """
    Tworzy geometrię sześciokąta, ale środek nazywa 'Q'.
    Służy do testowania wizualizacji i mechanizmu P0.
    """
    g = Graph()

    # --- 1. Geometria (6 wierzchołków na okręgu) ---
    radius = 2.0
    center_x, center_y = 3.0, 3.0  # Przesunięcie środka

    vertices_ids = [1, 2, 3, 4, 5, 6]

    for i, vid in enumerate(vertices_ids):
        # Kąt co 60 stopni
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)

        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)

        # Tworzymy wierzchołki geometryczne
        g.add_vertex(Vertex(uid=vid, x=round(x, 2), y=round(y, 2)))

    # --- 2. Krawędzie (E) ---
    # Łączymy w pętlę 1-2-3-4-5-6-1
    for i in range(len(vertices_ids)):
        curr_v = vertices_ids[i]
        next_v = vertices_ids[(i + 1) % len(vertices_ids)]

        eid = f"E{i + 1}"
        # Tworzymy krawędzie (zielone kwadraty w wizualizacji)
        g.add_hyperedge(Hyperedge(uid=eid, label="E", r=0, b=1))
        g.connect(eid, curr_v)
        g.connect(eid, next_v)

    # --- 3. Wnętrze (Q) - TEST ---
    # Tutaj robimy "oszustwo" dla testu.
    # Geometrycznie to sześciokąt, ale logicznie dajemy label='Q'.
    # Dzięki temu wizualizacja pokaże czerwony kwadrat, a P0 zadziała.
    q_id = "Q1"
    g.add_hyperedge(Hyperedge(uid=q_id, label="Q", r=0, b=0))

    # Podłączamy Q do wszystkich 6 wierzchołków
    for vid in vertices_ids:
        g.connect(q_id, vid)

    return g


def get_graph_with_shared_edge_marked_simple():
    """
    Graf do testowania P3 - wersja prosta.
    Dwa trójkąty/czworokąty współdzielące krawędź E_shared.
    E_shared ma R=1, B=0.
    Wszystkie krawędzie zewnętrzne są brzegowe (B=1).
    """
    g = Graph()

    # Wierzchołki
    v1 = Vertex(uid=1, x=0, y=0)
    v2 = Vertex(uid=2, x=2, y=0)
    v3 = Vertex(uid=3, x=1, y=2)
    v4 = Vertex(uid=4, x=1, y=-2)

    for v in [v1, v2, v3, v4]:
        g.add_vertex(v)

    # Krawędź współdzielona (do podziału)
    e_shared = Hyperedge(uid="E_shared", label="E", r=1, b=0)
    g.add_hyperedge(e_shared)
    g.connect("E_shared", 1)
    g.connect("E_shared", 2)

    # Krawędzie zewnętrzne (żeby graf wyglądał sensownie)
    edges = [
        ("E1", 1, 3), ("E2", 3, 2),  # Górny trójkąt
        ("E3", 1, 4), ("E4", 4, 2)  # Dolny trójkąt
    ]
    for eid, vid1, vid2 in edges:
        e = Hyperedge(uid=eid, label="E", r=0, b=1)
        g.add_hyperedge(e)
        g.connect(eid, vid1)
        g.connect(eid, vid2)

    # Elementy wnętrza (opcjonalne dla P3, ale poprawne topologicznie)
    q1 = Hyperedge(uid="Q1", label="Q", r=0, b=0)  # Góra
    g.add_hyperedge(q1)
    for vid in [1, 2, 3]:
        g.connect("Q1", vid)

    q2 = Hyperedge(uid="Q2", label="Q", r=0, b=0)  # Dół
    g.add_hyperedge(q2)
    for vid in [1, 2, 4]:
        g.connect("Q2", vid)

    return g


def get_graph_with_shared_edge_marked_extended():
    r"""
    Graf do testowania P3 - wersja rozszerzona.
    Dwa elementy Q współdzielące krawędź E_shared (R=1, B=0).
    
    E_shared (1-2) jest współdzielona (B=0) i oznaczona do podziału (R=1).
    E1, E3 są brzegowe (B=1).
    E2, E4 są współdzielone (B=0) między Q1/Q2.
    """
    g = Graph()

    # Wierzchołki
    v1 = Vertex(uid=1, x=0, y=0)
    v2 = Vertex(uid=2, x=2, y=0)
    v3 = Vertex(uid=3, x=1, y=2)
    v4 = Vertex(uid=4, x=1, y=-2)

    for v in [v1, v2, v3, v4]:
        g.add_vertex(v)

    # Krawędź współdzielona (do podziału) - między Q1 i Q2
    e_shared = Hyperedge(uid="E_shared", label="E", r=1, b=0)
    g.add_hyperedge(e_shared)
    g.connect("E_shared", 1)
    g.connect("E_shared", 2)

    # Krawędzie - mix brzegowych i współdzielonych
    edges = [
        ("E1", 1, 3, 1),  # Brzegowa (zewnętrzna lewa)
        ("E2", 3, 2, 0),  # Współdzielona (między Q1 a potencjalnym Q3)
        ("E3", 2, 4, 1),  # Brzegowa (zewnętrzna prawa)
        ("E4", 4, 1, 0),  # Współdzielona (między Q2 a potencjalnym Q4)
    ]
    for eid, vid1, vid2, b_flag in edges:
        e = Hyperedge(uid=eid, label="E", r=0, b=b_flag)
        g.add_hyperedge(e)
        g.connect(eid, vid1)
        g.connect(eid, vid2)

    # Elementy wnętrza (Q1 góra, Q2 dół)
    q1 = Hyperedge(uid="Q1", label="Q", r=0, b=0)  # Górny trójkąt
    g.add_hyperedge(q1)
    for vid in [1, 2, 3]:
        g.connect("Q1", vid)

    q2 = Hyperedge(uid="Q2", label="Q", r=0, b=0)  # Dolny trójkąt
    g.add_hyperedge(q2)
    for vid in [1, 2, 4]:
        g.connect("Q2", vid)

    return g


def get_pentagonal_graph_marked_simple():
    """
    Graf do testowania P7 - wersja prosta.
    Jeden element P (pięciokąt) z R=1.
    Otoczony 5 krawędziami E z R=0.
    """
    g = Graph()

    # 5 wierzchołków na okręgu
    import math
    radius = 2.0
    for i in range(5):
        angle = math.radians(72 * i - 90)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        g.add_vertex(Vertex(uid=i+1, x=x, y=y))

    # Wnętrze P (R=1 - trigger dla P7)
    p = Hyperedge(uid="P1", label="P", r=1, b=0)
    g.add_hyperedge(p)
    for i in range(1, 6):
        g.connect("P1", i)

    # 5 krawędzi (R=0 - mają zostać zmienione na R=1)
    for i in range(5):
        curr = i + 1
        next_v = ((i + 1) % 5) + 1
        eid = f"E{curr}"
        e = Hyperedge(uid=eid, label="E", r=0, b=1)
        g.add_hyperedge(e)
        g.connect(eid, curr)
        g.connect(eid, next_v)

    return g


def get_pentagonal_graph_marked_extended():
    """
    Graf do testowania P7 - wersja rozszerzona.
    Element P (pięciokąt) z R=1 w centrum, otoczony elementami Q.
    
    Struktura:
    - 1 element P (pięciokąt centralny, R=1)
    - 5 elementów Q (trójkąty na zewnątrz)
    - 5 krawędzi P-Q (współdzielone, B=0)
    - 5 krawędzi zewnętrznych Q (brzegowe, B=1)
    
    P7 oznacza wszystkie 5 krawędzi P (zarówno B=0 jak i potencjalnie B=1).
    """
    g = Graph()

    # 5 wierzchołków pięciokąta (wewnętrzne)
    import math
    radius_inner = 2.0
    pentagon_vertices = []
    for i in range(5):
        angle = math.radians(72 * i - 90)  # -90 żeby pierwszy był u góry
        x = radius_inner * math.cos(angle)
        y = radius_inner * math.sin(angle)
        vid = i + 1
        g.add_vertex(Vertex(uid=vid, x=x, y=y))
        pentagon_vertices.append(vid)

    # 5 wierzchołków zewnętrznych (dla trójkątów Q)
    radius_outer = 3.5
    outer_vertices = []
    for i in range(5):
        angle = math.radians(72 * i - 90)
        x = radius_outer * math.cos(angle)
        y = radius_outer * math.sin(angle)
        vid = i + 6  # 6-10
        g.add_vertex(Vertex(uid=vid, x=x, y=y))
        outer_vertices.append(vid)

    # Element P (pięciokąt centralny, R=1 - trigger dla P7)
    p = Hyperedge(uid="P1", label="P", r=1, b=0)
    g.add_hyperedge(p)
    for vid in pentagon_vertices:
        g.connect("P1", vid)

    # 5 krawędzi pięciokąta (wewnętrzne krawędzie P)
    # Te są współdzielone z trójkątami Q (B=0)
    for i in range(5):
        curr = pentagon_vertices[i]
        next_v = pentagon_vertices[(i + 1) % 5]
        eid = f"E{i+1}"
        e = Hyperedge(uid=eid, label="E", r=0, b=0)  # B=0 - współdzielone z Q
        g.add_hyperedge(e)
        g.connect(eid, curr)
        g.connect(eid, next_v)

    # 5 trójkątów Q na zewnątrz + ich krawędzie
    for i in range(5):
        # Trójkąt składa się z:
        # - 2 wierzchołki z pięciokąta
        # - 1 wierzchołek zewnętrzny
        v_inner1 = pentagon_vertices[i]
        v_inner2 = pentagon_vertices[(i + 1) % 5]
        v_outer = outer_vertices[i]

        # Element Q (trójkąt)
        q_id = f"Q{i+1}"
        q = Hyperedge(uid=q_id, label="Q", r=0, b=0)
        g.add_hyperedge(q)
        g.connect(q_id, v_inner1)
        g.connect(q_id, v_inner2)
        g.connect(q_id, v_outer)

        # Krawędź od v_inner1 do v_outer (brzegowa)
        e1_id = f"E_outer_{i+1}a"
        e1 = Hyperedge(uid=e1_id, label="E", r=0, b=1)
        g.add_hyperedge(e1)
        g.connect(e1_id, v_inner1)
        g.connect(e1_id, v_outer)

        # Krawędź od v_outer do v_inner2 (brzegowa)
        e2_id = f"E_outer_{i+1}b"
        e2 = Hyperedge(uid=e2_id, label="E", r=0, b=1)
        g.add_hyperedge(e2)
        g.connect(e2_id, v_outer)
        g.connect(e2_id, v_inner2)

    return g


def get_hexagonal_graph_marked():
    """
    Graf do testowania P10.
    Jeden element S (szcześciokąt) z R=1.
    Otoczony 6 krawędziami E z R=0.
    """
    g = Graph()

    # 6 wierzchołków na okręgu
    import math
    radius = 2.0
    for i in range(6):
        angle = math.radians(60 * i)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        g.add_vertex(Vertex(uid=i+1, x=x, y=y))

    # Wnętrze P (R=1 - trigger dla P10)
    p = Hyperedge(uid="P1", label="S", r=1, b=0)
    g.add_hyperedge(p)
    for i in range(1, 7):
        g.connect("P1", i)

    # 6 krawędzi (R=0 - mają zostać zmienione na R=1)
    for i in range(6):
        curr = i + 1
        next_v = ((i + 1) % 6) + 1
        eid = f"E{curr}"
        e = Hyperedge(uid=eid, label="E", r=0, b=1)
        g.add_hyperedge(e)
        g.connect(eid, curr)
        g.connect(eid, next_v)

    return g


def get_heptagonal_graph_marked():
    """
    Graf do testowania P13.
    Jeden element T (siedmiokąt) z R=1.
    Otoczony 5 krawędziami E z R=0.
    """
    g = Graph()

    # Wierzchołki
    vertices = [Vertex(uid=i, x=math.cos(2 * math.pi / 7 * i), y=math.sin(2 * math.pi / 7 * i)) for i in range(1, 8)]
    for v in vertices:
        g.add_vertex(v)

    # Element T (siedmiokąt)
    t = Hyperedge(uid="T", label="T", r=1, b=0)
    g.add_hyperedge(t)
    for v in vertices:
        g.connect("T", v.uid)

    # Krawędzie E (R=0)
    for i in range(7):
        e = Hyperedge(uid=f"E{i+1}", label="E", r=0, b=1)
        g.add_hyperedge(e)
        g.connect(e.uid, vertices[i].uid)
        g.connect(e.uid, vertices[(i + 1) % 7].uid)

    return g


def get_2x2_grid_graph_marked(marked_quad_ids=[]):
    """
    Tworzy siatkę 2x2 elementy (4 czworokąty).

    Układ wierzchołków (ID):
    7 -- 8 -- 9  (y=2.0)
    | Q3 | Q4 |
    4 -- 5 -- 6  (y=1.0)
    | Q1 | Q2 |
    1 -- 2 -- 3  (y=0.0)

    marked_quad_ids: lista ID czworokątów (Q), które mają mieć R=1.
    """
    if not marked_quad_ids:
        return get_2x2_grid_graph()

    g = Graph()

    # --- 1. Wierzchołki (Vertex) ---
    # Generujemy 9 wierzchołków w siatce 3x3 punkty
    vertices_data = [
        (1, 0.0, 0.0),
        (2, 1.0, 0.0),
        (3, 2.0, 0.0),  # Rząd dolny
        (4, 0.0, 1.0),
        (5, 1.0, 1.0),
        (6, 2.0, 1.0),  # Rząd środkowy
        (7, 0.0, 2.0),
        (8, 1.0, 2.0),
        (9, 2.0, 2.0),  # Rząd górny
    ]

    for uid, x, y in vertices_data:
        g.add_vertex(Vertex(uid=uid, x=x, y=y))

    # --- 2. Elementy Wnętrza (Q) ---
    # Definiujemy 4 elementy. Lewy-górny to Q3.
    # Atrybut R=0 na starcie.
    quads = [
        Hyperedge(uid="Q1", label="Q", r=0, b=0),  # Lewy-dół
        Hyperedge(uid="Q2", label="Q", r=0, b=0),  # Prawy-dół
        Hyperedge(uid="Q3", label="Q", r=0, b=0),  # Lewy-góra (TARGET)
        Hyperedge(uid="Q4", label="Q", r=0, b=0),  # Prawy-góra
    ]
    for q in quads:
        if q.uid in marked_quad_ids:
            q.r = 1  # Oznaczamy R=1 dla wskazanych czworokątów
        g.add_hyperedge(q)

    # Definicja połączeń Q z wierzchołkami (kolejność zazwyczaj przeciwna do ruchu wskazówek zegara lub zgodna)
    q_conns = {
        "Q1": [1, 2, 5, 4],
        "Q2": [2, 3, 6, 5],
        "Q3": [4, 5, 8, 7],
        "Q4": [5, 6, 9, 8],
    }
    for q_uid, v_ids in q_conns.items():
        for v_id in v_ids:
            g.connect(q_uid, v_id)

    # --- 3. Krawędzie (E) ---
    # Dodajemy krawędzie, aby graf był kompletny (ważne: krawędzie wewnętrzne są współdzielone!)
    # Format: (ID, v1, v2, Boundary_Flag)
    edges_data = [
        # Zewnętrzne (Boundary B=1)
        ("E1", 1, 2, 1),
        ("E2", 2, 3, 1),  # Dół
        ("E3", 3, 6, 1),
        ("E4", 6, 9, 1),  # Prawa
        ("E5", 9, 8, 1),
        ("E6", 8, 7, 1),  # Góra
        ("E7", 7, 4, 1),
        ("E8", 4, 1, 1),  # Lewa
        # Wewnętrzne (Internal B=0) - to są krawędzie współdzielone między Q
        (
            "E9",
            4,
            5,
            0,
        ),  # Pozioma środek (między Q1/Q3 a Q2/Q4 - nie, to między Q1 a Q3)
        ("E10", 5, 6, 0),  # Pozioma środek
        ("E11", 2, 5, 0),  # Pionowa środek
        ("E12", 5, 8, 0),  # Pionowa środek
    ]

    for eid, v1, v2, b_flag in edges_data:
        e = Hyperedge(uid=eid, label="E", r=0, b=b_flag)
        g.add_hyperedge(e)
        g.connect(eid, v1)
        g.connect(eid, v2)

    return g

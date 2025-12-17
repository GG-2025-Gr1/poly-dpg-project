import pytest
from src.productions.p5 import ProductionP5
from src.graph import Graph
from src.elements import Vertex, Hyperedge
# Używamy Twojej funkcji z projektu:
from src.utils.visualization import visualize_graph
import matplotlib
matplotlib.use('Agg')

# --- KONFIGURACJA ---
VIS_DIR = "tests/test_p5"


def create_base_graph():
    """Tworzy poprawny graf wejściowy dla P5 (LHS)."""
    graph = Graph()

    # Narożniki
    v1 = Vertex(1, 0.0, 0.0)
    v2 = Vertex(2, 2.0, 0.0)
    v3 = Vertex(3, 2.0, 2.0)
    v4 = Vertex(4, 0.0, 2.0)

    # Midpoints (wiszące)
    m1 = Vertex(5, 1.0, 0.0, hanging=True)
    m2 = Vertex(6, 2.0, 1.0, hanging=True)
    m3 = Vertex(7, 1.0, 2.0, hanging=True)
    m4 = Vertex(8, 0.0, 1.0, hanging=True)

    for v in [v1, v2, v3, v4, m1, m2, m3, m4]:
        graph.add_vertex(v)

    # Element Q (R=1)
    q = Hyperedge("Q1", "Q", r=1, b=0)
    graph.add_hyperedge(q)
    for i in [1, 2, 3, 4]:
        graph.connect("Q1", i)

    # Krawędzie obwodu (niezbędne dla P5)
    edges = [("E1a", 1, 5), ("E1b", 5, 2), ("E2a", 2, 6), ("E2b", 6, 3),
             ("E3a", 3, 7), ("E3b", 7, 4), ("E4a", 4, 8), ("E4b", 8, 1)]
    for e, u, v in edges:
        graph.add_hyperedge(Hyperedge(e, "E", 0, 1))
        graph.connect(e, u)
        graph.connect(e, v)

    return graph


# === SCENARIUSZ 1: STANDARDOWE WYKONANIE ===
def test_vis_standard_execution():
    """Generuje obrazki dla poprawnego wykonania produkcji."""
    graph = create_base_graph()

    # 1. Przed
    visualize_graph(graph, "P5: LHS (Standard)", f"{VIS_DIR}/scenariusz1_przed.png")

    # 2. Wykonanie
    p5 = ProductionP5()
    p5.apply(graph)

    # 3. Po
    visualize_graph(graph, "P5: RHS (Standard)", f"{VIS_DIR}/scenariusz1_po.png")


# === SCENARIUSZ 2: GRAF JAKO PODGRAF (Izomorfizm) ===
def test_vis_subgraph_execution():
    """Generuje obrazki, gdy element jest częścią większego grafu."""
    graph = create_base_graph()

    # Dodajemy "niezwiązane" elementy (sztuczny tłum)
    graph.add_vertex(Vertex(99, 4.0, 4.0))  # Daleko
    graph.add_hyperedge(Hyperedge("E_extra", "E", 0, 1))
    graph.connect("E_extra", 99)

    # 1. Przed
    visualize_graph(graph, "P5: LHS (Podgraf)", f"{VIS_DIR}/scenariusz2_podgraf_przed.png")

    p5 = ProductionP5()
    p5.apply(graph)

    # 2. Po (Sprawdzamy czy węzeł 99 nadal tam jest)
    visualize_graph(graph, "P5: RHS (Podgraf)", f"{VIS_DIR}/scenariusz2_podgraf_po.png")


# === SCENARIUSZ 3: BŁĄD - BRAK WIERZCHOŁKA ===
def test_vis_error_missing_vertex():
    """Generuje obrazek niepoprawnego grafu (brak jednego mid-pointa)."""
    graph = create_base_graph()

    # Usuwamy wierzchołek nr 5 (ten na dole pośrodku)
    # Uwaga: remove_node w NetworkX usuwa też przyległe krawędzie
    graph.remove_node(5)

    visualize_graph(graph, "P5 Error: Brak wierzcholka 5", f"{VIS_DIR}/scenariusz3_error_brak_v.png")

    # Próba wykonania (nie powinna nic zmienić)
    p5 = ProductionP5()
    matches = p5.find_lhs(graph)
    assert len(matches) == 0  # Upewniamy się w teście, że nie działa


# === SCENARIUSZ 4: BŁĄD - ZŁA WARTOŚĆ R ===
def test_vis_error_wrong_attribute():
    """Generuje obrazek grafu z błędnym atrybutem (R=0 zamiast R=1)."""
    graph = create_base_graph()

    # Psujemy atrybut R
    graph.update_hyperedge("Q1", r=0)

    visualize_graph(graph, "P5 Error: Q ma R=0", f"{VIS_DIR}/scenariusz4_error_zle_R.png")

    p5 = ProductionP5()
    matches = p5.find_lhs(graph)
    assert len(matches) == 0


# === SCENARIUSZ 5: BŁĄD - BRAK KRAWĘDZI (Broken Edge) ===
def test_vis_error_missing_edge():
    """Generuje obrazek, gdzie krawędź nie jest 'połamana' (brak węzła w środku)."""
    graph = create_base_graph()

    # Usuwamy całą dolną strukturę (E-M-E) i wstawiamy jedną krawędź bezpośrednią
    # To symuluje sytuację, gdzie bok NIE został wcześniej podzielony przez P3
    graph.remove_node(5)  # Usuwamy midpoint
    graph.remove_node("E1a")  # Usuwamy małe krawędzie
    graph.remove_node("E1b")

    # Dodajemy "całą" krawędź między 1 a 2
    graph.add_hyperedge(Hyperedge("E_whole", "E", 0, 1))
    graph.connect("E_whole", 1)
    graph.connect("E_whole", 2)

    visualize_graph(graph, "P5 Error: Bok niepodzielony", f"{VIS_DIR}/scenariusz5_error_caly_bok.png")

    p5 = ProductionP5()
    matches = p5.find_lhs(graph)
    assert len(matches) == 0


# === SCENARIUSZ 6: WIELE DOPASOWAŃ (Double Match) ===
def test_vis_multiple_matches():
    """
    Tworzy graf z DWOMA niezależnymi elementami gotowymi do podziału.
    Sprawdza, czy produkcja wykona się dla obu miejsc.
    """
    graph = Graph()

    # --- Pierwszy kwadrat (po lewej, ID 1-8) ---
    # Narożniki
    graph.add_vertex(Vertex(1, 0, 0))
    graph.add_vertex(Vertex(2, 2, 0))
    graph.add_vertex(Vertex(3, 2, 2))
    graph.add_vertex(Vertex(4, 0, 2))
    # Midpoints
    graph.add_vertex(Vertex(5, 1, 0, hanging=True))
    graph.add_vertex(Vertex(6, 2, 1, hanging=True))
    graph.add_vertex(Vertex(7, 1, 2, hanging=True))
    graph.add_vertex(Vertex(8, 0, 1, hanging=True))
    # Elementy
    graph.add_hyperedge(Hyperedge("Q1", "Q", r=1, b=0))
    for i in [1, 2, 3, 4]:
        graph.connect("Q1", i)
    # Krawędzie
    edges1 = [("E1a", 1, 5), ("E1b", 5, 2), ("E2a", 2, 6), ("E2b", 6, 3),
              ("E3a", 3, 7), ("E3b", 7, 4), ("E4a", 4, 8), ("E4b", 8, 1)]
    for e, u, v in edges1:
        graph.add_hyperedge(Hyperedge(e, "E", 0, 1))
        graph.connect(e, u)
        graph.connect(e, v)

    # --- Drugi kwadrat (po prawej, ID 11-18) ---
    offset_x = 4.0
    graph.add_vertex(Vertex(11, 0 + offset_x, 0))
    graph.add_vertex(Vertex(12, 2 + offset_x, 0))
    graph.add_vertex(Vertex(13, 2 + offset_x, 2))
    graph.add_vertex(Vertex(14, 0 + offset_x, 2))
    # Midpoints
    graph.add_vertex(Vertex(15, 1 + offset_x, 0, hanging=True))
    graph.add_vertex(Vertex(16, 2 + offset_x, 1, hanging=True))
    graph.add_vertex(Vertex(17, 1 + offset_x, 2, hanging=True))
    graph.add_vertex(Vertex(18, 0 + offset_x, 1, hanging=True))
    # Elementy
    graph.add_hyperedge(Hyperedge("Q2", "Q", r=1, b=0))
    for i in [11, 12, 13, 14]:
        graph.connect("Q2", i)
    # Krawędzie
    edges2 = [("E11a", 11, 15), ("E11b", 15, 12), ("E12a", 12, 16), ("E12b", 16, 13),
              ("E13a", 13, 17), ("E13b", 17, 14), ("E14a", 14, 18), ("E14b", 18, 11)]
    for e, u, v in edges2:
        graph.add_hyperedge(Hyperedge(e, "E", 0, 1))
        graph.connect(e, u)
        graph.connect(e, v)

    visualize_graph(graph, "P5: LHS (Dwa kwadraty)", f"{VIS_DIR}/scenariusz6_multi_przed.png")

    p5 = ProductionP5()
    # Sprawdźmy ile znalazł dopasowań
    matches = p5.find_lhs(graph)
    assert len(matches) == 2, f"Powinien znaleźć 2 dopasowania, znalazł {len(matches)}"

    p5.apply(graph)

    visualize_graph(graph, "P5: RHS (Dwa kwadraty)", f"{VIS_DIR}/scenariusz6_multi_po.png")


# === SCENARIUSZ 7: GEOMETRIA - SKRZYŻOWANE WIERZCHOŁKI (Twisted) ===
def test_vis_geometric_distortion():
    """
    Testuje punkt rubryki: 'niepoprawny (z błędnymi współrzędnymi)'.
    Tworzymy tzw. 'bowtie quad' (skrzyżowany).
    Topologicznie jest poprawny (spełnia warunki grafowe), ale geometrycznie jest błędny.
    Produkcja się wykona (bo sprawdza topologię), ale wynik wizualny pokaże problem.
    """
    graph = Graph()

    # Skrzyżowanie: V2 zamienione miejscami z V4 geometrycznie
    # (0,0) -- (0,2)  <-- V2 jest teraz u góry po lewej
    #           \ /
    #           / \
    # (2,0) -- (2,2)

    v1 = Vertex(1, 0.0, 0.0)
    v2 = Vertex(2, 0.0, 2.0)  # ZAMIANA: V2 poszło tam gdzie V4
    v3 = Vertex(3, 2.0, 2.0)
    v4 = Vertex(4, 2.0, 0.0)  # ZAMIANA: V4 poszło tam gdzie V2

    # Midpoints (współrzędne 'na oko' pośrodku boków skrzyżowanych)
    # Bok 1-2 (teraz pionowy lewy): (0,1)
    m1 = Vertex(5, 0.0, 1.0, hanging=True)
    # Bok 2-3 (teraz poziomy górny): (1,2)
    m2 = Vertex(6, 1.0, 2.0, hanging=True)
    # Bok 3-4 (teraz pionowy prawy): (2,1)
    m3 = Vertex(7, 2.0, 1.0, hanging=True)
    # Bok 4-1 (teraz poziomy dolny): (1,0)
    m4 = Vertex(8, 1.0, 0.0, hanging=True)

    for v in [v1, v2, v3, v4, m1, m2, m3, m4]:
        graph.add_vertex(v)

    # Q łączy 1-2-3-4 (kolejność topologiczna standardowa, ale w przestrzeni skręcona)
    q = Hyperedge("Q1", "Q", r=1, b=0)
    graph.add_hyperedge(q)
    for i in [1, 2, 3, 4]:
        graph.connect("Q1", i)

    # Krawędzie
    edges = [("E1a", 1, 5), ("E1b", 5, 2), ("E2a", 2, 6), ("E2b", 6, 3),
             ("E3a", 3, 7), ("E3b", 7, 4), ("E4a", 4, 8), ("E4b", 8, 1)]
    for e, u, v in edges:
        graph.add_hyperedge(Hyperedge(e, "E", 0, 1))
        graph.connect(e, u)
        graph.connect(e, v)

    visualize_graph(graph, "P5: Twisted Geometry (LHS)", f"{VIS_DIR}/scenariusz7_twisted_przed.png")

    p5 = ProductionP5()
    p5.apply(graph)

    visualize_graph(graph, "P5: Twisted Geometry (RHS)", f"{VIS_DIR}/scenariusz7_twisted_po.png")


# === SCENARIUSZ 8: BŁĄD - ZŁA ETYKIETA (Label) ===
def test_vis_error_wrong_label():
    """
    Testuje punkt: 'niepoprawny (z niepoprawną etykietą)'.
    Wszystko jest idealnie (R=1, boki podzielone), ale element nazywa się 'S' zamiast 'Q'.
    Produkcja NIE powinna się wykonać.
    """
    graph = create_base_graph()

    # Zmieniamy etykietę głównego elementu na "S" (np. element Sierpińskiego ;) )
    graph.update_hyperedge("Q1", label="S")

    visualize_graph(graph, "P5 Error: Label='S' zamiast 'Q'", f"{VIS_DIR}/scenariusz8_error_zla_etykieta.png")

    p5 = ProductionP5()
    matches = p5.find_lhs(graph)
    assert len(matches) == 0, "Produkcja nie powinna zadziałać dla label='S'"


# === SCENARIUSZ 9: GEOMETRIA - FIGURA WKLĘSŁA (Boomerang) ===
def test_vis_concave_geometry():
    """
    Testuje punkt: 'czy współrzędne nowych wierzchołków są poprawne'.
    Używamy czworokąta wklęsłego (jak grot strzały lub bumerang).

    Matematyka (średnia arytmetyczna) spowoduje, że nowy środek wypadnie
    POZA obszarem figury (pomiędzy ramionami bumerangu).
    Jest to zachowanie poprawne i oczekiwane w tym algorytmie.
    """
    graph = Graph()

    # Kształt "V" lub grota strzały skierowanego w górę
    # (0,2)       (2,2)
    #   \           /
    #    \         /
    #     \ (1,1) /  <-- V_wklęsły (Corner 4)
    #      \     /
    #       (1,0)    <-- V_dół (Corner 2) - chociaż tutaj układ musi być cykliczny

    # Zróbmy prostszy "Bumerang":
    v1 = Vertex(1, 0.0, 0.0)  # Lewy dół
    v2 = Vertex(2, 2.0, 0.0)  # Prawy dół
    v3 = Vertex(3, 2.0, 2.0)  # Prawy góra
    v4 = Vertex(4, 1.0, 1.0)  # WKLĘŚNIĘCIE (zamiast być w (0,2))

    # Midpoints (współrzędne uśrednione ręcznie)
    m1 = Vertex(5, 1.0, 0.0, hanging=True)  # Dół (między 1 a 2)
    m2 = Vertex(6, 2.0, 1.0, hanging=True)  # Prawo (między 2 a 3)
    m3 = Vertex(7, 1.5, 1.5, hanging=True)  # Wklęsły bok (między 3 a 4)
    m4 = Vertex(8, 0.5, 0.5, hanging=True)  # Lewy bok (między 4 a 1)

    for v in [v1, v2, v3, v4, m1, m2, m3, m4]:
        graph.add_vertex(v)

    # Q
    q = Hyperedge("Q1", "Q", r=1, b=0)
    graph.add_hyperedge(q)
    for i in [1, 2, 3, 4]: graph.connect("Q1", i)

    # Krawędzie
    edges = [("E1a", 1, 5), ("E1b", 5, 2), ("E2a", 2, 6), ("E2b", 6, 3),
             ("E3a", 3, 7), ("E3b", 7, 4), ("E4a", 4, 8), ("E4b", 8, 1)]
    for e, u, v in edges:
        graph.add_hyperedge(Hyperedge(e, "E", 0, 1))
        graph.connect(e, u)
        graph.connect(e, v)

    visualize_graph(graph, "P5: Concave (LHS)", f"{VIS_DIR}/scenariusz9_concave_przed.png")

    p5 = ProductionP5()
    p5.apply(graph)

    visualize_graph(graph, "P5: Concave (RHS)", f"{VIS_DIR}/scenariusz9_concave_po.png")


# === SCENARIUSZ 10: SĄSIEDZI ZE WSPÓLNĄ KRAWĘDZIĄ (Connected Mesh) ===
def test_vis_connected_neighbors():
    """
    Testuje dwa elementy Q, które dzielą jedną krawędź (i jej midpoint).
    Jest to kluczowy test dla zachowania ciągłości siatki (mesh continuity).

    Struktura:
    [ Q1 ]-[ Q2 ]

    Wspólna krawędź pionowa: (2,0) -- (2,1) -- (2,2)
    """
    graph = Graph()

    # --- Wierzchołki (Geometryczna siatka 2x1) ---
    # Narożniki
    # Lewy (x=0)
    v1 = Vertex(1, 0.0, 0.0)  # Lewy-Dół
    v4 = Vertex(4, 0.0, 2.0)  # Lewy-Góra
    # Środek (x=2) - WSPÓLNE
    v2 = Vertex(2, 2.0, 0.0)  # Środek-Dół (Wspólny)
    v3 = Vertex(3, 2.0, 2.0)  # Środek-Góra (Wspólny)
    # Prawy (x=4)
    v5 = Vertex(5, 4.0, 0.0)  # Prawy-Dół
    v6 = Vertex(6, 4.0, 2.0)  # Prawy-Góra

    # Midpoints (Wiszące)
    # Lewy kwadrat (zewnętrzne)
    m_left = Vertex(10, 0.0, 1.0, hanging=True)
    m_top1 = Vertex(11, 1.0, 2.0, hanging=True)
    m_btm1 = Vertex(12, 1.0, 0.0, hanging=True)

    # WSPÓLNY MIDPOINT (Pionowy środek)
    m_shared = Vertex(13, 2.0, 1.0, hanging=True)

    # Prawy kwadrat (zewnętrzne)
    m_right = Vertex(14, 4.0, 1.0, hanging=True)
    m_top2 = Vertex(15, 3.0, 2.0, hanging=True)
    m_btm2 = Vertex(16, 3.0, 0.0, hanging=True)

    all_nodes = [v1, v2, v3, v4, v5, v6, m_left, m_top1, m_btm1, m_shared, m_right, m_top2, m_btm2]
    for v in all_nodes:
        graph.add_vertex(v)

    # --- Elementy Q ---
    # Q1 (Lewy): 1-2-3-4
    graph.add_hyperedge(Hyperedge("Q1", "Q", r=1, b=0))
    for i in [1, 2, 3, 4]:
        graph.connect("Q1", i)

    # Q2 (Prawy): 2-5-6-3 (Uwaga na kolejność, żeby szło po obwodzie)
    graph.add_hyperedge(Hyperedge("Q2", "Q", r=1, b=0))
    for i in [2, 5, 6, 3]:
        graph.connect("Q2", i)

    # --- Krawędzie E ---
    # Definicja krawędzi: (ID, Start, End)
    edges_data = [
        # Lewy kwadrat (unikalne)
        ("E_L_left1", 1, 10), ("E_L_left2", 10, 4),
        ("E_L_top1", 4, 11), ("E_L_top2", 11, 3),
        ("E_L_btm1", 1, 12), ("E_L_btm2", 12, 2),

        # WSPÓLNA KRAWĘDŹ (Pionowa) - Dodajemy ją tylko raz!
        # Łączy V2 -> M_shared -> V3
        ("E_Shared1", 2, 13), ("E_Shared2", 13, 3),

        # Prawy kwadrat (unikalne)
        ("E_R_btm1", 2, 16), ("E_R_btm2", 16, 5),
        ("E_R_right1", 5, 14), ("E_R_right2", 14, 6),
        ("E_R_top1", 6, 15), ("E_R_top2", 15, 3)
    ]

    for eid, u, v in edges_data:
        graph.add_hyperedge(Hyperedge(eid, "E", 0, 1))
        graph.connect(eid, u)
        graph.connect(eid, v)

    # 1. Wizualizacja PRZED
    visualize_graph(graph, "P5: Connected Neighbors (LHS)", f"{VIS_DIR}/scenariusz10_connected_przed.png")

    # 2. Aplikacja
    p5 = ProductionP5()
    # Powinno znaleźć 2 dopasowania (Q1 i Q2)
    matches = p5.find_lhs(graph)
    assert len(matches) == 2, f"Powinno byc 2 sąsiadów do podziału, jest {len(matches)}"

    p5.apply(graph)

    # 3. Wizualizacja PO
    visualize_graph(graph, "P5: Connected Neighbors (RHS)", f"{VIS_DIR}/scenariusz10_connected_po.png")

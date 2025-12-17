from itertools import combinations
import pytest

from src.productions.p1 import ProductionP1
from tests.graphs import get_2x2_grid_graph_marked

from src.utils.visualization import visualize_graph

POSSIBLE_Q_IDS = ["Q1", "Q2", "Q3", "Q4"]

VIS_DIR = "tests/test_p1"

def test_2x2_grid_initial_state_with_Q1_marked():
    """Test that all Q elements in the 2x2 grid have R=0 initially. except Q1 which has R=1."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])

    for q_id in POSSIBLE_Q_IDS:
        hyperedge = graph.get_hyperedge(q_id)
        assert hyperedge.label == "Q"
        if q_id == "Q1":
            assert hyperedge.r == 1, f"{q_id} should have R=1 initially"
        else:
            assert hyperedge.r == 0, f"{q_id} should have R=0 initially"
            
    visualize_graph(graph, title="Initial State with Q1 marked", filepath=f"{VIS_DIR}/initial_state_Q1_marked.png")
            
@pytest.mark.parametrize("target_q_id", POSSIBLE_Q_IDS)
def test_2x2_grid_p1_on_specific_q(target_q_id):
    """Test that P1 correctly marks E elements connected to a specific Q element as R=1."""
    graph = get_2x2_grid_graph_marked(marked_quad_ids=[target_q_id])
    
    visualize_graph(graph, title=f"Before P1 on {target_q_id}", filepath=f"{VIS_DIR}/before_P1_on_{target_q_id}.png")
    p1 = ProductionP1()

    # Apply P1 to specific Q
    result_graph = p1.apply(graph, target_id=target_q_id)

    # Check that the E edges connected to the target Q have R=1
    target_hyperedge = result_graph.get_hyperedge(target_q_id)
    hyperedge_vertices = result_graph.get_hyperedge_vertices(target_hyperedge.uid)
    for vertex1, vertex2 in combinations(hyperedge_vertices, 2):
        hyperedges = result_graph.get_hyperedges_between_vertices(
            vertex_uid1=vertex1.uid, vertex_uid2=vertex2.uid
        )
        for he in hyperedges:
            if he.label == "E":
                assert he.r == 1, f"E edge {he.uid} connected to {target_q_id} should have R=1 after P1"
                
    visualize_graph(result_graph, title=f"After P1 on {target_q_id}", filepath=f"{VIS_DIR}/after_P1_on_{target_q_id}.png")
    
def test_p1_should_not_apply_if_R_is_0():
    """
    Test sprawdza, czy produkcja NIE wykonuje się, gdy hiperkrawędź Q ma R=0.
    Pokrywa punkt: Sprawdzenie warunku atrybutów (graf izomorficzny, ale złe atrybuty).
    """
    # Przygotuj graf, w którym Q1 ma R=0 (domyślnie w get_2x2_grid_graph_marked tylko wybrany ma R=1)
    # Tutaj nie oznaczamy żadnego jako R=1, więc wszystkie mają R=0.
    graph = get_2x2_grid_graph_marked(marked_quad_ids=[]) 
    p1 = ProductionP1()

    # Próbujemy zaaplikować produkcję do Q1, które ma R=0
    candidates = p1.find_lhs(graph, target_id="Q1")
    
    assert len(candidates) == 0, "Produkcja nie powinna znaleźć kandydata, gdy R=0"

    # Upewniamy się, że graf się nie zmienił (krawędzie E nadal mają R=0)
    target_hyperedge = graph.get_hyperedge("Q1")
    hyperedge_vertices = graph.get_hyperedge_vertices(target_hyperedge.uid)
    for vertex1, vertex2 in combinations(hyperedge_vertices, 2):
        hyperedges = graph.get_hyperedges_between_vertices(vertex1.uid, vertex2.uid)
        for he in hyperedges:
            if he.label == "E":
                assert he.r == 0, "Krawędź E nie powinna zmienić R na 1"
    
    visualize_graph(graph, title="After P1 attempt on Q1 with R=0", filepath=f"{VIS_DIR}/after_P1_attempt_on_Q1_R0.png")


def test_p1_should_not_apply_if_node_is_missing():
    """
    Test sprawdza zachowanie dla niekompletnego grafu (usunięty wierzchołek).
    Pokrywa punkt: 1.3 - graf niepoprawny (bez jakiegoś wierzchołka).
    """
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    p1 = ProductionP1()

    # Pobieramy wierzchołki Q1 i usuwamy jeden z nich z grafu
    q1 = graph.get_hyperedge("Q1")
    vertices = graph.get_hyperedge_vertices(q1.uid)
    vertex_to_remove = vertices[0]
    
    # Symulacja usunięcia wierzchołka (zależnie od implementacji Graph, 
    # tutaj zakładamy usunięcie go ze struktury logicznej, co sprawia, że Q1 ma tylko 3 sąsiadów)
    graph.remove_node(vertex_to_remove.uid) 

    candidates = p1.find_lhs(graph, target_id="Q1")
    assert len(candidates) == 0, "Produkcja nie powinna dopasować Q, który ma mniej niż 4 wierzchołki"
    
    visualize_graph(graph, title="After P1 attempt on Q1 with a missing vertex", filepath=f"{VIS_DIR}/after_P1_attempt_on_Q1_missing_vertex.png")


def test_p1_should_not_apply_if_boundary_edge_is_missing():
    """
    Test sprawdza zachowanie, gdy brakuje krawędzi 'E' między wierzchołkami Q.
    Pokrywa punkt: 1.4 - graf niepoprawny (bez jakiejś krawędzi).
    """
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    p1 = ProductionP1()

    # Znajdź krawędź E należącą do Q1 i usuń ją
    q1 = graph.get_hyperedge("Q1")
    vertices = graph.get_hyperedge_vertices(q1.uid)
    
    # Znajdźmy jakąś krawędź E między wierzchołkami Q1
    edge_removed = False
    for v1, v2 in combinations(vertices, 2):
        edges = graph.get_hyperedges_between_vertices(v1.uid, v2.uid)
        e_edges = [e for e in edges if e.label == "E"]
        if e_edges:          
            # Usuwamy pierwszą znalezioną krawędź E
            graph.remove_edge(v1.uid, e_edges[0].uid)
            edge_removed = True
            break
        
    assert edge_removed, "Nie udało się przygotować testu - brak krawędzi E do usunięcia"

    # Weryfikacja logiki find_lhs (która sprawdza spójność otoczenia)
    candidates = p1.find_lhs(graph, target_id="Q1")
    # Zgodnie z logiką w `find_lhs`, jeśli brakuje krawędzi E, pętla może przerwać działanie
    # lub uznać to za brak pełnego dopasowania (zależy od dokładnej implementacji `should_continue`).
    # Zakładając rygorystyczne sprawdzanie topologii:
    
    print(candidates)
    assert len(candidates) == 0, "Produkcja nie powinna się wykonać, jeśli brakuje krawędzi brzegowej E"
    
    visualize_graph(graph, title="After P1 attempt on Q1 with a missing boundary edge", filepath=f"{VIS_DIR}/after_P1_attempt_on_Q1_missing_boundary_edge.png")


def test_p1_isolation_does_not_affect_neighbors():
    """
    Test sprawdza, czy wykonanie produkcji na Q1 nie psuje sąsiada Q2 (który ma R=0).
    Pokrywa punkty: 
    2.1 - czy nie uszkadza większego grafu.
    2.2 - czy transformuje tylko wskazane osadzenie.
    """
    # Q1 ma R=1, Q2 ma R=0. Sąsiadują ze sobą.
    graph = get_2x2_grid_graph_marked(marked_quad_ids=["Q1"])
    p1 = ProductionP1()

    # Wykonaj na Q1
    p1.apply(graph, target_id="Q1")

    # Sprawdź Q2 (nie powinno być zmienione, poza krawędzią wspólną)
    q2 = graph.get_hyperedge("Q2")
    assert q2.r == 0, "Atrybut R dla Q2 nie powinien się zmienić"

    # Sprawdź krawędzie Q2
    q2_vertices = graph.get_hyperedge_vertices(q2.uid)
    q1_vertices = graph.get_hyperedge_vertices("Q1")
    
    for v1, v2 in combinations(q2_vertices, 2):
        edges = graph.get_hyperedges_between_vertices(v1.uid, v2.uid)
        for e in edges:
            if e.label == "E":
                # Jeśli krawędź jest wspólna z Q1 (czyli oba wierzchołki należą też do Q1)
                is_shared = (v1 in q1_vertices) and (v2 in q1_vertices)
                
                if is_shared:
                    assert e.r == 1, "Wspólna krawędź powinna mieć R=1 (zmieniona przez Q1)"
                else:
                    assert e.r == 0, "Krawędź należąca tylko do Q2 powinna pozostać nietknięta (R=0)"
                    
    visualize_graph(graph, title="After P1 on Q1, checking Q2 unaffected", filepath=f"{VIS_DIR}/after_P1_on_Q1_checking_Q2.png")
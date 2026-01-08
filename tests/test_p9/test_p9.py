from src.productions.p9 import ProductionP9
from tests.graphs import get_hexagonal_graph_marked 
from src.utils.visualization import visualize_graph
from src.elements import Hyperedge, Vertex
from src.graph import Graph 


def get_graph_with_unmarked_element() -> Graph:
    """
    Tworzy graf z elementem S (P1) z R=0 (nieoznaczony).
    """
    graph = get_hexagonal_graph_marked()
    # Zmieniamy domyślne R=1 na R=0 dla elementu P1 (Label='S')
    graph.update_hyperedge("P1", r=0) 
    return graph

def get_graph_with_marked_element() -> Graph:
    """
    Tworzy graf z elementem S (P1) z R=1 (oznaczony).
    """
    # get_hexagonal_graph_marked domyślnie tworzy P1 z R=1
    return get_hexagonal_graph_marked()


def test_p9_isomorphism_and_application():
    """
    Sprawdza, czy P9 poprawnie znajduje element S z R=0 i ustawia mu R=1.
    """
    graph = get_graph_with_unmarked_element() 

    visualize_graph(graph, "P9: Przed", filepath="tests/test_p9/before_p9.png")

    p9 = ProductionP9()
    matches = p9.find_lhs(graph)

    assert len(matches) == 1
    assert matches[0].uid == "P1" 

    graph = p9.apply(graph)
    visualize_graph(graph, "P9: Po", filepath="tests/test_p9/after_p9.png")

    element_p1 = graph.get_hyperedge("P1")
    assert element_p1.r == 1, "Element P1 (S) powinien mieć R=1 po zastosowaniu P9"
    


def test_p9_ignored_if_element_is_already_marked_r1():
    """
    P9 nie powinna działać na elemencie S (P1), który ma już R=1.
    """
    graph = get_graph_with_marked_element()

    p9 = ProductionP9()
    matches = p9.find_lhs(graph)
    
    assert len(matches) == 0, "P9 nie powinna znaleźć dopasowania dla elementu z R=1"


def test_p9_selects_unmarked_among_many():
    """
    Sprawdza, czy P9 wybiera tylko element S z R=0, ignorując elementy S z R=1.
    """
    graph = get_graph_with_unmarked_element()

    # Dodajemy S2 (oznaczony R=1)
    s2 = Hyperedge(uid="S2", label="S", r=1, b=0)
    graph.add_hyperedge(s2)
    graph.connect("S2", 1)
    graph.connect("S2", 2)
    graph.connect("S2", 3) 

    p9 = ProductionP9()
    matches = p9.find_lhs(graph)

    # Powinno znaleźć tylko P1 (R=0)
    assert len(matches) == 1
    assert matches[0].uid == "P1"

    graph = p9.apply(graph)
    assert graph.get_hyperedge("P1").r == 1
    assert graph.get_hyperedge("S2").r == 1


def test_p9_only_targets_label_s():
    """
    P9 powinna dopasowywać tylko element 'S', ignorując inne elementy (np. 'E') z R=0.
    """
    graph = get_graph_with_unmarked_element()

    # E1 jest krawędzią (label='E', R=0) w hexagonal_graph_marked
    edge_e = graph.get_hyperedge("E1")
    assert edge_e.r == 0
    assert edge_e.label == 'E'

    p9 = ProductionP9()
    matches = p9.find_lhs(graph)

    # Powinno znaleźć tylko P1 (label='S', R=0)
    assert len(matches) == 1
    assert matches[0].uid == "P1"
    assert matches[0].label == 'S'



def test_p9_broken_topology_missing_vertex():
    """
    P9 nie powinna działać, jeśli element S (P1) nie ma 6 wierzchołków.
    """
    graph = get_graph_with_unmarked_element()
    
    # Odłączamy wierzchołek 6 od P1
    graph.remove_edge("P1", 6)

    p9 = ProductionP9()
    matches = p9.find_lhs(graph)
    
    assert len(matches) == 0, "P9 powinna zignorować S, który nie jest połączony z 6 wierzchołkami"

def test_p9_broken_topology_wrong_label_r0():
    """
    P9 ignoruje element z R=0, który ma poprawną topologię (6 wierzchołków), ale niepoprawną etykietę ('Q').
    """
    graph = get_graph_with_unmarked_element()

    # Ustawiamy P1 (S) na R=1, żeby wykluczyć go z dopasowania
    graph.update_hyperedge("P1", r=1) 

    # Tworzymy nowy element Q1 (R=0, 6 wierzchołków)
    q1 = Hyperedge(uid="Q1", label="Q", r=0, b=0)
    graph.add_hyperedge(q1)
    
    # Podłączamy Q1 do 6 wierzchołków (1..6)
    for vid in range(1, 7):
        graph.connect("Q1", vid)
    
    p9 = ProductionP9()
    matches = p9.find_lhs(graph)

    assert len(matches) == 0, "P9 powinna zignorować Q1, ponieważ jego label to nie 'S'"

def test_p9_missing_boundary_edge():
    """
    P9 nie powinna działać, jeśli brakuje choć jednej krawędzi 'E' na obwodzie.
    """
    graph = get_graph_with_unmarked_element()
    
    # Usuwamy jedną krawędź brzegową (np. E1)
    graph.remove_node("E1")

    p9 = ProductionP9()
    matches = p9.find_lhs(graph)
    
    assert len(matches) == 0, "P9 nie powinna znaleźć dopasowania, gdy brakuje krawędzi E"
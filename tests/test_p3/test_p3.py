import pytest
from src.productions.p3 import ProductionP3
from tests.graphs import get_graph_with_shared_edge_marked
from src.utils.visualization import visualize_graph


def test_p3_isomorphism_and_application():
    """
    Sprawdza czy P3 poprawnie wykrywa LHS i aplikuje RHS.
    Oczekiwane: Krawędź E_shared znika, powstają dwie nowe, powstaje wierzchołek w środku.
    """
    graph = get_graph_with_shared_edge_marked()
    visualize_graph(graph, "P3: Przed", filepath="tests/test_p3/before_p3.png")

    p3 = ProductionP3()
    # E_shared jest jedynym kandydatem (R=1, B=0)
    matches = p3.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "E_shared"

    graph = p3.apply(graph)
    visualize_graph(graph, "P3: Po", filepath="tests/test_p3/after_p3.png")

    # Weryfikacja
    # 1. Stara krawędź usunięta
    with pytest.raises(ValueError):
        graph.get_hyperedge("E_shared")

    # 2. Nowy wierzchołek dodany
    new_v_id = "E_shared_v_new"
    new_vertex = graph.get_vertex(new_v_id)
    assert new_vertex.x == 1.0  # (0+2)/2
    assert new_vertex.y == 0.0  # (0+0)/2
    assert new_vertex.hanging == True

    # 3. Dwie nowe krawędzie
    e1 = graph.get_hyperedge("E_shared_e1")
    e2 = graph.get_hyperedge("E_shared_e2")
    assert e1.r == 0
    assert e2.r == 0
    assert e1.b == 0
    assert e2.b == 0


def test_p3_incorrect_b_attribute():
    """
    Testuje czy P3 ignoruje krawędzie z B=1 (brzegowe).
    """
    graph = get_graph_with_shared_edge_marked()
    # Psujemy graf - ustawiamy B=1 dla docelowej krawędzi
    graph.update_hyperedge("E_shared", b=1)

    p3 = ProductionP3()
    matches = p3.find_lhs(graph)
    assert len(matches) == 0, "P3 nie powinna działać na krawędziach brzegowych (B=1)"


def test_p3_incorrect_r_attribute():
    """
    Testuje czy P3 ignoruje krawędzie z R=0 (nieoznaczone).
    """
    graph = get_graph_with_shared_edge_marked()
    graph.update_hyperedge("E_shared", r=0)

    p3 = ProductionP3()
    matches = p3.find_lhs(graph)
    assert len(matches) == 0


def test_p3_missing_vertex():
    """
    Testuje odporność na uszkodzony graf (krawędź bez wierzchołka).
    """
    graph = get_graph_with_shared_edge_marked()
    # Usuwamy jeden wierzchołek połączony z E_shared (ID 2)
    # Najpierw usuwamy krawędź grafową, żeby stan był niespójny logicznie dla algorytmu
    graph.remove_edge("E_shared", 2)

    p3 = ProductionP3()
    matches = p3.find_lhs(graph)
    assert len(matches) == 0, "P3 nie powinna działać jeśli krawędź nie ma 2 wierzchołków"

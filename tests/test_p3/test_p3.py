import pytest
from src.productions.p3 import ProductionP3
from tests.graphs import get_graph_with_shared_edge_marked_extended, get_graph_with_shared_edge_marked_simple
from src.utils.visualization import visualize_graph


@pytest.mark.parametrize("graph_func,desc", [
    (get_graph_with_shared_edge_marked_simple, "simple"),
    (get_graph_with_shared_edge_marked_extended, "complex"),
])
def test_p3_isomorphism_and_application(graph_func, desc):
    """
    Sprawdza czy P3 poprawnie wykrywa LHS i aplikuje RHS.
    Zgodnie z diagramem: stara krawędź zostaje (R: 1->0), powstają 2 nowe krawędzie i wierzchołek V.
    """
    graph = graph_func()
    
    # Liczba krawędzi E przed
    edges_before = [n for n, d in graph.nx_graph.nodes(data=True) 
                    if hasattr(d.get("data"), "label") and d.get("data").label == "E"]
    count_before = len(edges_before)
    
    visualize_graph(graph, f"P3 ({desc}): Przed", filepath=f"tests/test_p3/before_p3_{desc}.png")

    p3 = ProductionP3()
    # E_shared jest jedynym kandydatem (R=1, B=0)
    matches = p3.find_lhs(graph)
    assert len(matches) == 1
    assert matches[0].uid == "E_shared"

    graph = p3.apply(graph)
    
    # Liczba krawędzi E po - powinna wzrosnąć o 2 (stara zostaje + 2 nowe)
    edges_after = [n for n, d in graph.nx_graph.nodes(data=True) 
                   if hasattr(d.get("data"), "label") and d.get("data").label == "E"]
    count_after = len(edges_after)
    assert count_after == count_before + 2, f"Liczba krawędzi E powinna wzrosnąć o 2 ({count_before} -> {count_after})"
    
    visualize_graph(graph, f"P3 ({desc}): Po", filepath=f"tests/test_p3/after_p3_{desc}.png")

    # Weryfikacja
    # 1. Stara krawędź POZOSTAJE z zaktualizowanym R
    e_shared = graph.get_hyperedge("E_shared")
    assert e_shared.r == 0, "Stara krawędź powinna mieć R=0"
    assert e_shared.b == 0, "Stara krawędź powinna zachować B=0"
    
    # Sprawdź że stara krawędź wciąż łączy te same wierzchołki
    e_shared_verts = graph.get_hyperedge_vertices("E_shared")
    assert len(e_shared_verts) == 2
    e_shared_vert_ids = {v.uid for v in e_shared_verts}
    assert e_shared_vert_ids == {1, 2}, "Stara krawędź powinna łączyć wierzchołki 1 i 2"

    # 2. Nowy wierzchołek dodany
    new_v_id = "E_shared_v"
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
    
    # Sprawdź topologię nowych krawędzi
    e1_verts = graph.get_hyperedge_vertices("E_shared_e1")
    e2_verts = graph.get_hyperedge_vertices("E_shared_e2")
    e1_vert_ids = {v.uid for v in e1_verts}
    e2_vert_ids = {v.uid for v in e2_verts}
    
    assert e1_vert_ids == {1, "E_shared_v"}, "E_shared_e1 powinna łączyć v1 z V"
    assert e2_vert_ids == {2, "E_shared_v"}, "E_shared_e2 powinna łączyć V z v2"


def test_p3_incorrect_b_attribute():
    """
    Testuje czy P3 ignoruje krawędzie z B=1 (brzegowe).
    """
    graph = get_graph_with_shared_edge_marked_extended()
    # Psujemy graf - ustawiamy B=1 dla docelowej krawędzi
    graph.update_hyperedge("E_shared", b=1)

    p3 = ProductionP3()
    matches = p3.find_lhs(graph)
    assert len(matches) == 0, "P3 nie powinna działać na krawędziach brzegowych (B=1)"


def test_p3_incorrect_r_attribute():
    """
    Testuje czy P3 ignoruje krawędzie z R=0 (nieoznaczone).
    """
    graph = get_graph_with_shared_edge_marked_extended()
    graph.update_hyperedge("E_shared", r=0)

    p3 = ProductionP3()
    matches = p3.find_lhs(graph)
    assert len(matches) == 0


def test_p3_missing_vertex():
    """
    Testuje odporność na uszkodzony graf (krawędź bez wierzchołka).
    """
    graph = get_graph_with_shared_edge_marked_extended()
    # Usuwamy jeden wierzchołek połączony z E_shared (ID 2)
    # Najpierw usuwamy krawędź grafową, żeby stan był niespójny logicznie dla algorytmu
    graph.remove_edge("E_shared", 2)

    p3 = ProductionP3()
    matches = p3.find_lhs(graph)
    assert len(matches) == 0, "P3 nie powinna działać jeśli krawędź nie ma 2 wierzchołków"

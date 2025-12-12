# Projekt Poly-DPG

Implementacja w języku Python systemu gramatyk grafowych do adaptacji siatek przy użyciu reprezentacji hipergrafowych. Projekt implementuje produkcje (transformacje grafów) na grafach geometrycznych z hiperkrawędziami reprezentującymi elementy logiczne (wnętrza i krawędzie) oraz wierzchołkami reprezentującymi punkty geometryczne.

## Spis treści

- [Przegląd](#przegląd)
- [Instalacja](#instalacja)
- [Struktura projektu](#struktura-projektu)
- [Użycie](#użycie)
- [Testowanie](#testowanie)
- [Licencja](#licencja)

## Przegląd

Projekt implementuje system oparty na hipergrafach do reprezentacji i manipulacji siatkami 2D. Kluczowe koncepcje to:

- **Wierzchołki (Vertices)**: Geometryczne punkty w przestrzeni 2D (współrzędne x, y)
- **Hiperkrawędzie (Hyperedges)**: Elementy logiczne reprezentujące komponenty siatki
  - `Q`: Elementy wewnętrzne (czworokąty)
  - `E`: Elementy krawędziowe
  - `P`, `S`: Inne typy elementów
- **Produkcje (Productions)**: Reguły transformacji grafów (np. P0 do oznaczania elementów do refinacji)
- **Graf (Graph)**: Wrapper wokół NetworkX zarządzający strukturą hipergrafu

System wspiera operacje refinacji siatki, gdzie elementy mogą być oznaczane (R=0 → R=1) i dzielone zgodnie z regułami produkcji.

## Instalacja

### Wymagania wstępne

- Python 3.12 lub wyższy
- uv; może poetry; w najgorszym wypadku pip

### Konfiguracja

1. Sklonuj repozytorium:

```bash
git clone <repository-url>
cd GG_proj
```

2. Zainstaluj zależności najlepiej używając `uv` (może `poetry` też zadziała, nie wiem) lub zainstaluj zależności ręcznie:

```bash
pip install matplotlib networkx pytest
```

### Zależności

- **matplotlib** (≥3.10.8): Wizualizacja grafów
- **networkx** (≥3.6.1): Struktura danych grafu i algorytmy
- **pytest** (≥9.0.2): Framework testowy

## Struktura projektu

```
GG_proj/
├── .pre-commit-config.yaml           # Definicje pre-push hooka
├── LICENSE                           # Licencja projektu
├── README.md                         # README (wersja angielska)
├── README-pl.md                      # Ten plik (wersja polska)
├── pyproject.toml                    # Konfiguracja projektu i zależności
├── main.py                           # Główny punkt wejścia i przykład użycia
├── src/                              # Kod źródłowy
│   ├── __init__.py                   # Inicjalizator pakietu
│   ├── elements.py                   # Klasy danych Vertex i Hyperedge
│   ├── graph.py                      # Klasa Graph opakowująca NetworkX
│   ├── productions/                  # Reguły transformacji grafu
│   │   ├── __init__.py               # Inicjalizator pakietu produkcji
│   │   ├── production.py             # Abstrakcyjna klasa bazowa dla produkcji
│   │   └── p0.py                     # Produkcja P0 (oznaczanie elementów)
│   └── utils/                        # Moduły narzędziowe
│       └── visualization.py          # Funkcje wizualizacji grafów
├── tests/                            # Zestaw testów
│   ├── graphs.py                     # Generatory grafów testowych (siatka 2x2, itd.)
│   └── test_p0/                      # Testy dla produkcji P0
│       ├── test_from_presentation.py # Testy parametryczne dla P0
│       └── test_hexagonal.py         # Testy siatek heksagonalnych
└── visualizations/                   # Katalog wyjściowy dla wygenerowanych obrazów
    └── tests/                        # Wizualizacje wyjściowe testów
        └── test_p0/
            ├── from_presentation/
            └── hexagonal/
```

### Opisy plików

#### Pliki główne

- **[LICENSE](LICENSE)**: Zawiera informacje o licencji projektu
- **[pyproject.toml](pyproject.toml)**: Metadane projektu i specyfikacja zależności (zgodne z PEP 518)
- **[main.py](main.py)**: Demonstracja podstawowego użycia - tworzy początkowy graf czworokąta, aplikuje produkcję P0 i generuje wizualizacje

#### Kod źródłowy (`src/`)

- **[elements.py](src/elements.py)**: Definiuje podstawowe klasy danych
  - `Vertex`: Reprezentuje geometryczny punkt 2D ze współrzędnymi (x, y) i opcjonalną flagą węzła wiszącego
  - `Hyperedge`: Reprezentuje logiczne elementy siatki z etykietą (Q/E/P/S), flagą refinacji (R) i flagą brzegu (B)

- **[graph.py](src/graph.py)**: Główna klasa grafu zarządzająca strukturą hipergrafu
  - Opakowuje graf NetworkX dla efektywnych operacji grafowych
  - Metody do dodawania/aktualizowania/usuwania wierzchołków i hiperkrawędzi
  - Przechodzenie grafu i zapytania o sąsiadów
  - Zarządzanie łącznością hiperkrawędź-wierzchołek

#### Produkcje (`src/productions/`)

- **[production.py](src/productions/production.py)**: Abstrakcyjna klasa bazowa definiująca wzorzec produkcji
  - `find_lhs()`: Identyfikuje pasujące podgrafy (lewa strona)
  - `apply_rhs()`: Transformuje dopasowane podgrafy (prawa strona)
  - `apply()`: Metoda szablonowa orkiestrująca aplikację produkcji

- **[p0.py](src/productions/p0.py)**: Implementuje produkcję P0
  - Oznacza elementy Q do refinacji przez ustawienie R=0 → R=1
  - Waliduje, że elementy Q są połączone z dokładnie 4 wierzchołkami
  - Wspiera ukierunkowaną lub automatyczną aplikację do wszystkich kandydatów

#### Narzędzia (`src/utils/`)

- **[visualization.py](src/utils/visualization.py)**: Funkcje wizualizacji grafów
  - `visualize_graph()`: Tworzy wizualizacje matplotlib hipergrafów
  - Pozycjonuje węzły hiperkrawędzi w centroidach połączonych wierzchołków
  - Koloruje węzły według typu (wierzchołki vs. hiperkrawędzie)
  - Etykiety pokazują typ elementu oraz flagi refinacji/brzegu

#### Testy (`tests/`)

- **[graphs.py](tests/graphs.py)**: Generatory grafów testowych
  - `get_2x2_grid_graph()`: Tworzy siatkę 2×2 z 4 elementami czworokątnymi
  - `get_hexagonal_graph()`: Tworzy wzorce siatek heksagonalnych
  - Używane przez zestawy testów do tworzenia spójnych scenariuszy testowych

- **[test_p0/test_from_presentation.py](tests/test_p0/test_from_presentation.py)**: Kompleksowe testy P0
  - Testy walidacji stanu początkowego
  - Testy parametryczne dla aplikacji P0 do konkretnych elementów Q
  - Testy automatycznej aplikacji P0 do wszystkich kandydatów
  - Waliduje, że tylko docelowe elementy są modyfikowane

- **[test_p0/test_hexagonal.py](tests/test_p0/test_hexagonal.py)**: Testy P0 na siatkach heksagonalnych

## Użycie

### Podstawowy przykład

Uruchom główny skrypt, aby zobaczyć prostą demonstrację:

```bash
python main.py
```

To spowoduje:

1. Utworzenie początkowego grafu czworokąta
2. Aplikację produkcji P0 w celu oznaczenia go do refinacji
3. Wygenerowanie plików wizualizacyjnych PNG (`step_0_init.png`, `step_1_after_p0.png`)

### Używanie biblioteki

```python
from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p0 import ProductionP0
from src.utils.visualization import visualize_graph

# Utwórz graf
graph = Graph()

# Dodaj wierzchołki
v1 = Vertex(uid=1, x=0.0, y=0.0)
v2 = Vertex(uid=2, x=1.0, y=0.0)
graph.add_vertex(v1)
graph.add_vertex(v2)

# Dodaj hiperkrawędź
edge = Hyperedge(uid="E1", label="E", r=0, b=1)
graph.add_hyperedge(edge)
graph.connect("E1", 1)
graph.connect("E1", 2)

# Zastosuj produkcję
p0 = ProductionP0()
graph = p0.apply(graph, target_id="Q1")

# Wizualizuj
visualize_graph(graph, "Mój Graf", filepath="output.png")
```

## Testowanie

Uruchom zestaw testów z pytest:

```bash
# Uruchom wszystkie testy
pytest

# Uruchom konkretny plik testowy
pytest tests/test_p0/test_from_presentation.py

# Uruchom z szczegółowym wyjściem
pytest -v

# Uruchom konkretny test
pytest tests/test_p0/test_from_presentation.py::test_2x2_grid_initial_state
```

Zestaw testów obejmuje:

- Testy jednostkowe dla operacji grafowych
- Testy walidacji reguł produkcji
- Testy poprawności transformacji siatki
- Testy parametryczne dla różnych konfiguracji grafów

## Licencja

Zobacz plik [LICENSE](LICENSE) dla szczegółów.

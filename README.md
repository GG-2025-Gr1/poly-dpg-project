# Poly-DPG Project

A Python implementation of a graph grammar system for mesh adaptation using hypergraph representations. The project implements productions (graph transformations) on geometric graphs with hyperedges representing logical elements (interiors and edges) and vertices representing geometric points.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Testing](#testing)
- [License](#license)

## Overview

This project implements a hypergraph-based system for representing and manipulating 2D meshes. The key concepts are:

- **Vertices**: Geometric points in 2D space (x, y coordinates)
- **Hyperedges**: Logical elements representing mesh components
  - `Q`: Interior elements (quadrilaterals)
  - `E`: Edge elements
  - `P`, `S`: Other element types
- **Productions**: Graph transformation rules (e.g., P0 for marking elements for refinement)
- **Graph**: A wrapper around NetworkX managing the hypergraph structure

The system supports mesh refinement operations where elements can be marked (R=0 → R=1) and subdivided according to production rules.

## Installation

### Prerequisites

- Python 3.12 or higher
- uv; maybe poetry; in the worst case scenario pip

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd GG_proj
```

2. Install dependencies using `uv` (maybe `poetry` will also work, I don't know) or install dependencies manually:

```bash
pip install matplotlib networkx pytest
```

### Dependencies

- **matplotlib** (≥3.10.8): Graph visualization
- **networkx** (≥3.6.1): Graph data structure and algorithms
- **pytest** (≥9.0.2): Testing framework

## Project Structure

```
GG_proj/
├── .pre-commit-config.yaml           # Definition of pre-push hook
├── LICENSE                           # Project license
├── README.md                         # This file
├── README-pl.md                      # This file but in Polish
├── pyproject.toml                    # Project configuration and dependencies
├── main.py                           # Main entry point and example usage
├── src/                              # Source code
│   ├── __init__.py                   # Package initializer
│   ├── elements.py                   # Vertex and Hyperedge data classes
│   ├── graph.py                      # Graph class wrapping NetworkX
│   ├── productions/                  # Graph transformation rules
│   │   ├── __init__.py               # Productions package initializer
│   │   ├── production.py             # Abstract base class for productions
│   │   └── p0.py                     # P0 production (element marking)
│   └── utils/                        # Utility modules
│       └── visualization.py          # Graph visualization functions
├── tests/                            # Test suite
│   ├── graphs.py                     # Test graph generators (2x2 grid, etc.)
│   └── test_p0/                      # Tests for P0 production
│       ├── test_from_presentation.py # Parametric tests for P0
│       └── test_hexagonal.py         # Hexagonal mesh tests
└── visualizations/                   # Output directory for generated images
    └── tests/                        # Test visualization outputs
        └── test_p0/
            ├── from_presentation/
            └── hexagonal/
```

### File Descriptions

#### Root Files

- **[LICENSE](LICENSE)**: Contains the project's license information
- **[pyproject.toml](pyproject.toml)**: Project metadata and dependency specification (PEP 518 compliant)
- **[main.py](main.py)**: Demonstrates basic usage - creates an initial quadrilateral graph, applies P0 production, and generates visualizations

#### Source Code (`src/`)

- **[elements.py](src/elements.py)**: Defines core data classes
  - `Vertex`: Represents a geometric 2D point with coordinates (x, y) and optional hanging node flag
  - `Hyperedge`: Represents logical mesh elements with label (Q/E/P/S), refinement flag (R), and boundary flag (B)

- **[graph.py](src/graph.py)**: Main graph class managing the hypergraph structure
  - Wraps NetworkX graph for efficient graph operations
  - Methods for adding/updating/removing vertices and hyperedges
  - Graph traversal and neighbor queries
  - Hyperedge-vertex connectivity management

#### Productions (`src/productions/`)

- **[production.py](src/productions/production.py)**: Abstract base class defining the production pattern
  - `find_lhs()`: Identifies matching subgraphs (left-hand side)
  - `apply_rhs()`: Transforms matched subgraphs (right-hand side)
  - `apply()`: Template method orchestrating the production application

- **[p0.py](src/productions/p0.py)**: Implements P0 production
  - Marks Q elements for refinement by setting R=0 → R=1
  - Validates that Q elements are connected to exactly 4 vertices
  - Supports targeted or automatic application to all candidates

#### Utilities (`src/utils/`)

- **[visualization.py](src/utils/visualization.py)**: Graph visualization functions
  - `visualize_graph()`: Creates matplotlib visualizations of hypergraphs
  - Positions hyperedge nodes at centroids of connected vertices
  - Color-codes nodes by type (vertices vs. hyperedges)
  - Labels show element type and refinement/boundary flags

#### Tests (`tests/`)

- **[graphs.py](tests/graphs.py)**: Test graph generators
  - `get_2x2_grid_graph()`: Creates a 2×2 mesh with 4 quadrilateral elements
  - `get_hexagonal_graph()`: Creates hexagonal mesh patterns
  - Used by test suites to create consistent test scenarios

- **[test_p0/test_from_presentation.py](tests/test_p0/test_from_presentation.py)**: Comprehensive P0 tests
  - Tests initial state validation
  - Parametric tests for applying P0 to specific Q elements
  - Tests automatic P0 application to all candidates
  - Validates that only target elements are modified

- **[test_p0/test_hexagonal.py](tests/test_p0/test_hexagonal.py)**: Tests P0 on hexagonal meshes

## Usage

### Basic Example

Run the main script to see a simple demonstration:

```bash
python main.py
```

This will:

1. Create an initial quadrilateral graph
2. Apply the P0 production to mark it for refinement
3. Generate visualization PNG files (`step_0_init.png`, `step_1_after_p0.png`)

### Using the Library

```python
from src.graph import Graph
from src.elements import Vertex, Hyperedge
from src.productions.p0 import ProductionP0
from src.utils.visualization import visualize_graph

# Create a graph
graph = Graph()

# Add vertices
v1 = Vertex(uid=1, x=0.0, y=0.0)
v2 = Vertex(uid=2, x=1.0, y=0.0)
graph.add_vertex(v1)
graph.add_vertex(v2)

# Add hyperedge
edge = Hyperedge(uid="E1", label="E", r=0, b=1)
graph.add_hyperedge(edge)
graph.connect("E1", 1)
graph.connect("E1", 2)

# Apply production
p0 = ProductionP0()
graph = p0.apply(graph, target_id="Q1")

# Visualize
visualize_graph(graph, "My Graph", filepath="output.png")
```

## Testing

Run the test suite with pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_p0/test_from_presentation.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_p0/test_from_presentation.py::test_2x2_grid_initial_state
```

The test suite includes:

- Unit tests for graph operations
- Production rule validation tests
- Mesh transformation correctness tests
- Parametric tests for different graph configurations

## License

See [LICENSE](LICENSE) file for details.

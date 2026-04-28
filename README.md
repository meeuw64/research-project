# Research Project – 4D Polytope Unfoldings

This project explores graph-based methods for studying all unfoldings (nets) of convex 4-polytopes, with a focus on regular examples such as the tesseract and the 16-cell.

The main idea is to represent a 4-polytope by its dual graph, where:

* vertices correspond to 3D cells
* edges correspond to shared facets between cells

Spanning trees of the dual graph correspond to candidate unfolding structures. The problem then is to classify them into equivalent unfolding groups. So the final output of the algorithm is then all the distinct unfoldings.

Idea for a pipeline:
- Given some polytope P:
- Generate 1-skeleton of dual polytope of P, call this graph G (dual graph)
- Compute Aut(G), i.e. all automorphisms φ : V(G) → V(G) such that φ is a bijection and e(u, v) ⇔ e(φ(u), φ(v))
- Label all edges in G as {e_1,e_2,e_3 ... e_n}
- For each T ∈ τ(G):
  * Compute minimum canonical bitstring of T under Aut(G)  
  * Insert this bitstring into a Set O (two spanning trees T1, T2 will have the same bitstring iff T1 ~ T2 under Aut(G))
  * Every element of this set O represents an orbit and thus a unique unfolding
- |O| = #unique unfoldings

Computing the canonical bitstring:
- Given some tree T, Aut(G) and set of edge labeling E:
- For each φ ∈ Aut(G):
  - Apply φ to T (group action)
  - Initialize bitstring b = 0000...0 (length |E|)
  - For each e ∈ E: 
    - b_i = 1 if e ∈ E(φ(T)) else 0
- Return minimum b using lexicographical ordering

Future: Check for net overlap, so this algorithm works for arbitrary polytope P 

---

## Goals

* Generate dual graphs of regular 4-polytopes
* Enumerate spanning trees
* Classify trees up to symmetry
* Investigate distinct unfoldings
* Explore computational methods for larger polytopes

---

## Project Structure

```text
research-project/
│── requirements.txt
│── README.md
│── src/
│   ├── generate_spanning_trees.py
│   ├── dual_graph_generator.py
│   ├── main.py
│   └── utils.py
│── data/
```

---

## Installation

Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

---

## Dependencies

Main libraries used:

* Python 3.x
* NetworkX
* SciPy
* NumPy
* Matplotlib

---

## Example Usage

Run spanning tree generation:

```bash
python src/generate_unfoldings --polytope_name
```

---


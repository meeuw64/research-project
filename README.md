# Research Project – 4D Polytope Unfoldings

This project explores graph-based methods for studying all unfoldings (nets) of convex 4-polytopes, with a focus on regular examples such as the tesseract and the 16-cell.

The main idea is to represent a 4-polytope by its dual graph, where:

* vertices correspond to 3D cells
* edges correspond to shared facets between cells

Spanning trees of the dual graph correspond to candidate unfolding structures. The problem then is to classify them into equivalent unfolding groups. So the final output of the algorithm is then all the distinct unfoldings.

Idea for a pipeline:
- Given some polytope P:
- Generate 1-skeleton of dual polytope of P, call this graph DG (dual graph)
- Compute automorphism graphs of DG (because automorphism graphs permute the vertices on the graph)
- While enumerating all spanning trees T of DG:
  * Compute canonical bitstring of T using automorphisms 
  * Put T into hashmap using bitstring as key
  * Every bucket in the hashmap will contain isomorphic graphs that all correspond to one particular unique unfolding
- #buckets in hash map corresponds to the #unique unfoldings 

- Future: Check for net overlap, so this algorithm works for arbitrary polytope P 

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


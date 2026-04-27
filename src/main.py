import networkx as nx
import time
import dual_graph_generator
import symmetry_reduction
from itertools import combinations


# Returns an iterator which enumerates all spanning trees of G
def spanning_tree_iterator(G):
    nodes = list(G.nodes)
    edges = list(G.edges)

    for subset in combinations(edges, len(nodes) - 1):
        T = nx.Graph()
        T.add_nodes_from(nodes)
        T.add_edges_from(subset)
        if nx.is_tree(T):
            yield T


if __name__ == "__main__":
    start = time.perf_counter()

    # Original graph from which the spanning trees were generated
    base_graph = dual_graph_generator.dual_graph_tesseract()

    automorphisms, edge_index = symmetry_reduction.compute_automorphisms(base_graph)

    print(f"Number of automorphisms: {len(automorphisms)}")

    # Spanning trees
    trees = spanning_tree_iterator(base_graph)
    n_spanning_trees = int(nx.number_of_spanning_trees(base_graph))

    print(f"Number of spanning trees: {n_spanning_trees}")

    unique = symmetry_reduction.compute_unique_unfoldings(automorphisms, edge_index, trees, n_spanning_trees)

    unique_trees = list(unique.values())

    end = time.perf_counter()
    print("\r----------- RESULTS -----------\n", end="", flush=True)
    print(f"Runtime: {end - start:.6f} seconds")
    print(f"Number of unique unfoldings: {len(unique_trees)}")
import dual_graph_generator
import symmetry_reduction
import networkx as nx
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


def unique_unfoldings(polytope_name):
    base_graph = dual_graph_generator.POLYTOPE_NAME_TO_DUAL_GRAPH[polytope_name]

    automorphisms, edge_index = symmetry_reduction.compute_automorphisms(base_graph)

    print(f"Number of automorphisms: {len(automorphisms)}")

    # Spanning trees
    trees = spanning_tree_iterator(base_graph)
    n_spanning_trees = round(nx.number_of_spanning_trees(base_graph))

    print(f"Number of spanning trees: {n_spanning_trees}")

    unique = symmetry_reduction.group_equivalent_unfoldings(automorphisms, edge_index, trees, n_spanning_trees)

    return unique
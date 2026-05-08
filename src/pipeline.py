import dual_graph_generator
import symmetry_reduction
import networkx as nx
from graph_utils import spanning_tree_edges_iterator


def unique_unfoldings(polytope_name):
    base_graph = dual_graph_generator.POLYTOPE_NAME_TO_DUAL_GRAPH[polytope_name]

    automorphisms, edge_index = symmetry_reduction.compute_edge_automorphisms(base_graph)

    print(f"Number of automorphisms: {len(automorphisms)}")

    # Spanning trees
    tree_edge_lists = spanning_tree_edges_iterator(base_graph)
    n_spanning_trees = round(nx.number_of_spanning_trees(base_graph))

    print(f"Number of spanning trees: {n_spanning_trees}")

    unique = symmetry_reduction.group_equivalent_unfoldings(automorphisms, edge_index, tree_edge_lists,n_spanning_trees)

    return unique
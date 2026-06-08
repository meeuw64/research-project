import dual_graph_generator
import symmetry_reduction
import networkx as nx
import math
from graph_utils import spanning_tree_edges_iterator

def polytope_info(polytope_name):
    base_graph = dual_graph_generator.POLYTOPE_NAME_TO_DUAL_GRAPH[polytope_name]

    n = base_graph.number_of_nodes()
    m = base_graph.number_of_edges()

    print(f"Polytope info about the {polytope_name}:")
    print(f"Number of vertices in dual graph: {n}")
    print(f"Number of edges in dual graph: {m}")

    # Automorphisms
    automorphisms, edge_index = symmetry_reduction.compute_edge_automorphisms(base_graph)
    n_automorphisms = len(automorphisms)

    print(f"Number of automorphisms: {n_automorphisms}")

    # Spanning trees
    n_spanning_trees = round(nx.number_of_spanning_trees(base_graph))

    print(f"Number of spanning trees: {n_spanning_trees}")

    # Orbit estimate
    orbit_lower_bound = math.ceil(n_spanning_trees / n_automorphisms)

    print(f"Minimum possible number of orbits: {orbit_lower_bound}")


def unique_unfoldings(base_graph):
    automorphisms, edge_index = symmetry_reduction.compute_edge_automorphisms(base_graph)

    print(f"Number of automorphisms: {len(automorphisms)}")

    # Spanning trees
    tree_edge_lists = spanning_tree_edges_iterator(base_graph)
    n_spanning_trees = round(nx.number_of_spanning_trees(base_graph))

    print(f"Number of spanning trees: {n_spanning_trees}")

    unique = symmetry_reduction.group_equivalent_unfoldings(automorphisms, edge_index, tree_edge_lists,n_spanning_trees)

    return edge_index, unique
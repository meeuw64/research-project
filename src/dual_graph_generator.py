import networkx as nx
from enum import Enum

"""
Methods to generate the dual graph (facet-adjacency graph) of 
various types of shapes in various dimensions
"""

# 3D
def dual_graph_tetrahedron():
    return nx.complete_graph(4)


def dual_graph_cube():
    labels = ["+x", "-x", "+y", "-y", "+z", "-z"]

    G = nx.complete_graph(labels)

    opposites = [("+x", "-x"), ("+y", "-y"), ("+z", "-z")]
    G.remove_edges_from(opposites)
    return G


def dual_graph_octahedron():
    return nx.hypercube_graph(3)

# Archimedean
def dual_graph_truncated_tetrahedron():
    hexagons = ["h1","h2", "h3", "h4"]
    triangles = ["t1", "t2", "t3", "t4"]

    # all hexagons connected
    G = nx.complete_graph(hexagons)

    # add triangle nodes
    G.add_nodes_from(triangles)

    # connect every triangle to every hexagon
    G.add_edges_from((t, h) for t in triangles for h in hexagons)

    # remove the opposite hexagon from each triangle
    G.remove_edges_from(zip(triangles, hexagons))

    return G

# 4D
def dual_graph_tesseract():
    # dual graph of the n-cube can be formed (in this case n = 4)
    # by removing a perfect matching from the complete graph of 2n vertices
    labels = ["+x", "-x", "+y", "-y", "+z", "-z", "+w", "-w"]

    G = nx.complete_graph(labels)

    opposites = [("+x", "-x"), ("+y", "-y"), ("+z", "-z"), ("+w", "-w")]
    G.remove_edges_from(opposites)
    return G


def dual_graph_4_simplex():
    return nx.complete_graph(5)


def dual_graph_4_orthoplex():
    return nx.hypercube_graph(4) # tesseract is the dual of orthoplex

POLYTOPE_NAME_TO_DUAL_GRAPH = {
    "tetrahedron": dual_graph_tetrahedron(),
    "cube": dual_graph_cube(),
    "octahedron": dual_graph_octahedron(),
    "trunc-tetrahedron": dual_graph_truncated_tetrahedron(),
    "tesseract": dual_graph_tesseract(),
    "4-simplex": dual_graph_4_simplex(),
    "4-orthoplex": dual_graph_4_orthoplex()
}
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

# TODO orthoplex_4_dual_graph():

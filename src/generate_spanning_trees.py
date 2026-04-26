import networkx as nx
from itertools import combinations
import dual_graph_generator
import pickle
from utils import DATA

def all_spanning_trees(G):
    nodes = list(G.nodes)
    edges = list(G.edges)

    n = nx.number_of_spanning_trees(G)

    i = 0
    for subset in combinations(edges, len(nodes) - 1):
        T = nx.Graph()
        T.add_nodes_from(nodes)
        T.add_edges_from(subset)
        if nx.is_tree(T):
            i += 1
            print(f"\r{i / n:.1%} done", end="", flush=True)
            yield T

    print("\nSpanning tree generation done\n")

# Generating all spanning trees:

# Select polytope
G = dual_graph_generator.dual_graph_4_orthoplex()

trees = list(all_spanning_trees(G))

output_path = DATA / "4_orthoplex_trees.pkl"

with open(output_path, "wb") as f:
    pickle.dump(trees, f)

print(f"Saved {len(trees)} trees to {output_path}")

import networkx as nx
import utils
import numpy as np
import matplotlib.pyplot as plt
from collections import deque


if __name__ == "__main__":
    trees = utils.load_spanning_trees("tesseract_trees.pkl")

    trees = deque(trees)

    # Each bucket contains a list of graphs
    # that are isomorphic to each other
    isomorphic_buckets = []

    while trees:
        G = trees.popleft()

        isomorphic_to_G = [G]
        non_isomorphic_to_G = deque()

        while trees:
            H = trees.popleft()
            if nx.is_isomorphic(G, H):
                isomorphic_to_G.append(H)
            else:
                non_isomorphic_to_G.append(H)

        isomorphic_buckets.append(isomorphic_to_G)
        trees = non_isomorphic_to_G

        # Distinct unfoldings

    print(len(isomorphic_buckets))


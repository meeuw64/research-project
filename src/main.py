import networkx as nx
import utils
import dual_graph_generator


def edge_key(u, v):
    return tuple(sorted((u, v)))


def canonical_form(T, automorphisms, edge_index):
    """
    Returns the canonical bitstring of T under all automorphisms
    of the base graph.
    """
    best = None

    for phi in automorphisms:
        bits = [0] * len(edge_index)

        for u, v in T.edges():
            a, b = phi[u], phi[v]
            e = edge_key(a, b)
            bits[edge_index[e]] = 1

        code = tuple(bits)

        if best is None or code < best:
            best = code

    return best


if __name__ == "__main__":
    trees = utils.load_spanning_trees("tesseract_trees.pkl")

    # Original graph from which the spanning trees were generated
    base_graph = dual_graph_generator.dual_graph_tesseract()

    edge_list = sorted(edge_key(u, v) for u, v in base_graph.edges())
    edge_index = {e: i for i, e in enumerate(edge_list)}

    matcher = nx.algorithms.isomorphism.GraphMatcher(base_graph, base_graph)
    automorphisms = list(matcher.isomorphisms_iter())

    print(f"Number of automorphisms: {len(automorphisms)}")
    print(f"Number of spanning trees: {len(trees)}")

    unique = {}

    for i, T in enumerate(trees, start=1):
        code = canonical_form(T, automorphisms, edge_index)

        if code not in unique:
            unique[code] = T

        if i % 1000 == 0:
            print(f"Processed {i}/{len(trees)} trees")

    unique_trees = list(unique.values())

    print(f"Number of unique unfoldings: {len(unique_trees)}")
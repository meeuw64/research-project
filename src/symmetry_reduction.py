import networkx as nx


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


def compute_automorphisms(G):
    edge_list = sorted(edge_key(u, v) for u, v in G.edges())
    edge_index = {e: i for i, e in enumerate(edge_list)}

    matcher = nx.algorithms.isomorphism.GraphMatcher(G, G)
    return list(matcher.isomorphisms_iter()), edge_index


def compute_unique_unfoldings(automorphisms, edge_index, trees, n_spanning_trees):
    unique = {}

    for i, T in enumerate(trees, start=1):
        code = canonical_form(T, automorphisms, edge_index)

        if code not in unique:
            unique[code] = T

        print(f"\r{i / n_spanning_trees:.1%} done", end="", flush=True)

    return unique
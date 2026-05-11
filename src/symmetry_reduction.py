import networkx as nx


def canonical_form(E_t, automorphisms, edge_index):
    tree_edge_indices = tuple(edge_index[e] for e in E_t)

    best = float("inf")

    for edge_map in automorphisms:
        code = 0
        for idx in tree_edge_indices:
            code |= 1 << edge_map[idx]

        if code < best:
            best = code

    return best


# Returns a list of edge maps, where each edge map dictates how the edges get mapped under one of the automorphisms
def compute_edge_automorphisms(G):
    # edge -> index
    edge_index = {}

    # label all edges with some index
    for i, (u, v) in enumerate(G.edges()):
        edge_index[(u, v)] = i
        edge_index[(v, u)] = i

    # An automorphism is an isomorphism between the graph and itself
    matcher = nx.algorithms.isomorphism.GraphMatcher(G, G)

    edge_maps = []

    for phi in matcher.isomorphisms_iter():
        # edge_map : old edge index -> new edge index
        edge_map = [0] * (len(edge_index) // 2)

        for (u, v) in G.edges():
            old_idx = edge_index[(u, v)]

            a, b = phi[u], phi[v]
            new_idx = edge_index[(a, b)]

            edge_map[old_idx] = new_idx

        edge_maps.append(edge_map)

    return edge_maps, edge_index


def group_equivalent_unfoldings(automorphisms, edge_index, tree_edge_lists, n_spanning_trees):
    unique = set()

    for i, E_t in enumerate(tree_edge_lists, start=1):
        code = canonical_form(E_t, automorphisms, edge_index)
        unique.add(code)

        if i % 1000 == 0 or i == n_spanning_trees:
            print(f"\r{i / n_spanning_trees:.1%} done", end="", flush=True)

    return unique
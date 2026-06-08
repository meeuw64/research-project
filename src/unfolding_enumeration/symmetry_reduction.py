import networkx as nx


def build_edge_index(G):
    """
    Returns a dictionary mapping both orientations of each edge to the same index.
    Assumes G is an undirected simple graph.
    """
    edge_index = {}

    for i, (u, v) in enumerate(G.edges()):
        edge_index[(u, v)] = i
        edge_index[(v, u)] = i

    return edge_index


def tree_to_bitmask(E_t, edge_index):
    """
    Encode a spanning tree edge list as an integer bitmask.
    """
    code = 0

    for e in E_t:
        code |= 1 << edge_index[e]

    return code


def apply_edge_map_to_bitmask(code, edge_map):
    """
    Apply one edge automorphism to a tree bitmask.
    """
    image = 0
    i = 0

    while code:
        if code & 1:
            image |= 1 << edge_map[i]

        code >>= 1
        i += 1

    return image


def compute_edge_automorphisms(G):
    """
    Returns:
        edge_maps: list of edge maps, where each map sends old edge index -> new edge index
        edge_index: dictionary mapping directed edge tuples to edge indices
    """
    edge_index = build_edge_index(G)
    m = G.number_of_edges()

    matcher = nx.algorithms.isomorphism.GraphMatcher(G, G)

    edge_maps = []

    for phi in matcher.isomorphisms_iter():
        edge_map = [0] * m

        for u, v in G.edges():
            old_idx = edge_index[(u, v)]
            new_idx = edge_index[(phi[u], phi[v])]
            edge_map[old_idx] = new_idx

        edge_maps.append(edge_map)

    return edge_maps, edge_index


def orbit_of_tree_bitmask(code, edge_automorphisms):
    """
    Generate all images of one spanning tree under the automorphism group.
    """
    for edge_map in edge_automorphisms:
        yield apply_edge_map_to_bitmask(code, edge_map)


def canonical_form_from_bitmask(code, edge_automorphisms):
    """
    Optional helper: returns the minimum bitmask in the orbit.
    Useful if you specifically want canonical labels.
    """
    return min(orbit_of_tree_bitmask(code, edge_automorphisms))


def group_equivalent_unfoldings(
    edge_automorphisms,
    edge_index,
    tree_edge_lists,
    n_spanning_trees=None,
):
    """
    Groups spanning trees up to graph automorphism.

    Instead of canonicalizing every spanning tree against every automorphism,
    this marks the whole orbit of a newly discovered representative as seen.

    Returns:
        representatives: set of bitmasks, one representative per orbit
    """
    seen = set()
    representatives = set()

    for i, E_t in enumerate(tree_edge_lists, start=1):
        code = tree_to_bitmask(E_t, edge_index)

        if code not in seen:
            representatives.add(code)

            for image_code in orbit_of_tree_bitmask(code, edge_automorphisms):
                seen.add(image_code)

        if n_spanning_trees is not None:
            if i % 1000 == 0 or i == n_spanning_trees:
                print(f"\r{i / n_spanning_trees:.1%} done", end="", flush=True)

    return representatives
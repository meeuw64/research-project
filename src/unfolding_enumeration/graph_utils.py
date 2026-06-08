# Returns an iterator which enumerates all edge lists of spanning trees of G
# NOTE: This method was written by generative AI
def spanning_tree_edges_iterator(G):
    nodes = list(G.nodes())
    n = len(nodes)

    if n == 0:
        return

    node_to_i = {node: i for i, node in enumerate(nodes)}
    edges = [(u, v) for u, v in G.edges()]
    m = len(edges)

    parent = list(range(n))
    rank = [0] * n
    chosen = []

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return None

        if rank[ra] < rank[rb]:
            ra, rb = rb, ra

        parent[rb] = ra
        rank_inc = rank[ra] == rank[rb]
        if rank_inc:
            rank[ra] += 1

        return rb, ra, rank_inc

    def undo(change):
        if change is None:
            return
        rb, ra, rank_inc = change
        parent[rb] = rb
        if rank_inc:
            rank[ra] -= 1

    def dfs(i):
        if len(chosen) == n - 1:
            yield list(chosen)
            return

        if i == m:
            return

        # Not enough edges left to complete a tree
        if len(chosen) + (m - i) < n - 1:
            return

        u, v = edges[i]
        a, b = node_to_i[u], node_to_i[v]

        # Include this edge if it does not create a cycle
        change = union(a, b)
        if change is not None:
            chosen.append((u, v))
            yield from dfs(i + 1)
            chosen.pop()
            undo(change)

        # Exclude this edge
        yield from dfs(i + 1)

    yield from dfs(0)


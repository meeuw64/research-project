from pathlib import Path
import json
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def graph_to_data(G):
    return {
        "nodes": list(G.nodes()),
        "edges": [list(edge) for edge in G.edges()],
    }

def edge_bitstring_to_data(bitmap, G):
    edges = []
    for i, (u, v) in enumerate(G.edges()):
        if (bitmap >> i) & 1:
            edges.append((u,v))

    return edges


# turns spanning tree bitstring representation to networkx graph
def edge_bitstring_to_graph(bitmap, G):
    result = nx.Graph()
    result.add_nodes_from(G.nodes)

    for i, (u, v) in enumerate(G.edges()):
        if (bitmap >> i) & 1:
            result.add_edge(u, v)

    return result


def save_unfoldings(
        path,
        original_graph,
        unfoldings,
):
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "graph": graph_to_data(original_graph)
            },
            f,
        )
        f.write("\n")

        for i, edge_bitstring in enumerate(unfoldings):
            json.dump(
                {
                    "index": i,
                    "spanning-edges": edge_bitstring_to_data(edge_bitstring, original_graph),
                },
                f,
            )
            f.write("\n")

    print("Successfully saved unfoldings to " + str(path))
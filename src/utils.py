from pathlib import Path
from polytope_core import polytope_builder
import json
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
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


def data_to_graph(edge_data, original_graph):
    tree = nx.Graph()

    tree.add_nodes_from(original_graph.nodes(data=True))

    for u, v in edge_data:
        if not original_graph.has_edge(u, v):
            raise ValueError(
                f"Serialized edge ({u!r}, {v!r}) does not exist "
                "in the original graph."
            )

        edge_attributes = original_graph.get_edge_data(u, v) or {}
        tree.add_edge(u, v, **edge_attributes)

    return tree


# turns spanning tree bitstring representation to networkx graph
def edge_bitstring_to_graph(bitmap, G):
    result = nx.Graph()
    result.add_nodes_from(G.nodes)

    for i, (u, v) in enumerate(G.edges()):
        if (bitmap >> i) & 1:
            result.add_edge(u, v)

    return result


# loads all serialized spanning trees.
# If 'i' is not None, only a single spanning tree is given at index 'i'
def load_spanning_trees(path, i : int | None = None):

    spanning_trees = []

    with path.open("r", encoding="utf-8") as f:
        first_line = f.readline()

        metadata = json.loads(first_line)
        polytope_name = metadata["polytope-name"]

        for line_number, line in enumerate(f, start=2):
            if i and i != line_number-2:
                continue

            if not line.strip():
                continue

            record = json.loads(line)

            spanning_trees.append(record["spanning-edges"])

    if len(spanning_trees) == 0:
        raise ValueError("no spanning tree found")

    return polytope_name, spanning_trees


# Returns tuple with the polytope object together with all its unfoldings
def load_polytope_unfoldings(path: Path):
    polytope_name, spanning_tree_data = load_spanning_trees(path)
    polytope = polytope_builder.POLYTOPE_NAME_MAP[polytope_name]

    unfoldings = [
        data_to_graph(edges, polytope.dual_graph())
        for edges in spanning_tree_data
    ]

    return polytope, unfoldings

# Returns tuple with polytope and a single unfolding
def load_single_polytope_unfolding(path, i):
    polytope_name, spanning_tree_data = load_spanning_trees(path, i)
    polytope = polytope_builder.POLYTOPE_NAME_MAP[polytope_name]
    edges = spanning_tree_data[0]

    unfolding = data_to_graph(edges, polytope.dual_graph())

    return polytope, unfolding

def save_unfoldings(
        path,
        original_graph,
        polytope_name,
        unfoldings,
):
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "polytope-name": polytope_name
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
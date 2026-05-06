from pathlib import Path
import json
import dual_graph_generator

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def graph_to_data(G):
    return {
        "nodes": list(G.nodes()),
        "edges": [list(edge) for edge in G.edges()],
    }

def save_unfoldings(
        path,
        polytope_name,
        unfoldings,
):
    original_graph = dual_graph_generator.POLYTOPE_NAME_TO_DUAL_GRAPH[polytope_name]
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "graph": graph_to_data(original_graph)
            },
            f,
        )
        f.write("\n")

        for i, tree in enumerate(unfoldings):
            json.dump(
                {
                    "index": i,
                    "spanning-edges": [list(edge) for edge in tree.edges()],
                },
                f,
            )
            f.write("\n")

    print("Successfully saved unfoldings to " + str(path))
import utils
from unfolding_enumeration import symmetry_reduction

import json
from pathlib import Path

import networkx as nx

def read_dual_graphs_from_json_files(
    input_directory: str | Path = utils.DATA / "johnson_solids_dual_graphs",
) -> dict[int, nx.Graph]:
    """
    Read J1.json through J92.json into memory.

    Returns:
        {
            1: nx.Graph(...),
            2: nx.Graph(...),
            ...
            92: nx.Graph(...),
        }
    """
    input_directory = Path(input_directory)

    if not input_directory.is_dir():
        raise FileNotFoundError(
            f"Directory does not exist: {input_directory.resolve()}"
        )

    duals: dict[int, nx.Graph] = {}

    for input_file in input_directory.glob("J*.json"):
        filename = input_file.stem  # For example: "J32"

        try:
            johnson_index = int(filename[1:])
        except ValueError:
            # Ignore files that do not follow the J<number>.json format.
            continue

        with input_file.open("r", encoding="utf-8") as file:
            graph_data = json.load(file)

        if "nodes" not in graph_data or "edges" not in graph_data:
            raise ValueError(
                f"{input_file} does not contain 'nodes' and 'edges'"
            )

        graph = nx.Graph()
        graph.add_nodes_from(graph_data["nodes"])
        graph.add_edges_from(graph_data["edges"])

        graph.graph.update(
            {
                "johnson_index": johnson_index,
                "name": f"J{johnson_index} dual graph",
                "source_file": str(input_file),
            }
        )

        duals[johnson_index] = graph

    if not duals:
        raise FileNotFoundError(
            f"No files matching J*.json found in "
            f"{input_directory.resolve()}"
        )

    return dict(sorted(duals.items()))

johnson_symmetry_order = {
     1: 8,   2: 10,  3: 6,   4: 8,   5: 10,  6: 10,
     7: 6,   8: 8,   9: 10, 10: 8,  11: 10, 12: 12,
    13: 20, 14: 12, 15: 16, 16: 20, 17: 16, 18: 6,
    19: 8,  20: 10, 21: 10, 22: 6,  23: 8,  24: 10,
    25: 10, 26: 8,  27: 12, 28: 16, 29: 16, 30: 20,
    31: 20, 32: 10, 33: 10, 34: 20, 35: 12, 36: 12,
    37: 16, 38: 20, 39: 20, 40: 10, 41: 10, 42: 20,
    43: 20, 44: 6,  45: 8,  46: 10, 47: 5,  48: 10,
    49: 4,  50: 4,  51: 12, 52: 4,  53: 4,  54: 4,
    55: 8,  56: 4,  57: 12, 58: 10, 59: 20, 60: 4,
    61: 6,  62: 4,  63: 6,  64: 6,  65: 6,  66: 8,
    67: 16, 68: 10, 69: 20, 70: 4,  71: 6,  72: 10,
    73: 20, 74: 4,  75: 6,  76: 10, 77: 10, 78: 2,
    79: 2,  80: 20, 81: 4,  82: 2,  83: 6,  84: 8,
    85: 16, 86: 4,  87: 2,  88: 4,  89: 4,  90: 8,
    91: 8,  92: 6,
}

if __name__ == "__main__":
    duals = read_dual_graphs_from_json_files()

    for i in range(1, 93):
        G = duals[i]
        aut, _ = symmetry_reduction.compute_edge_automorphisms(G)

        aut_order = len(aut)
        symm_order = johnson_symmetry_order[i]

        assert aut_order == symm_order, f"Symmetry order of J_{i} is {symm_order}, but computed automorphism order is {aut_order}"

        print("All symmetry orders correspond to graph automorphism orders.")

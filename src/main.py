import sys
import time
import argparse
import utils
from unfolding_enumeration import pipeline
from polytope_core import polytope_builder

if __name__ == "__main__":
    # --------------- PROGRAM ARGUMENTS ---------------
    parser = argparse.ArgumentParser()

    parser.add_argument("--polytope",
                        type=str,
                        required=True,
                        choices=polytope_builder.POLYTOPE_NAME_MAP.keys(),
                        help="Name of polytope to analyze")

    parser.add_argument(
        "--info",
        action="store_true",
        help=f"Only prints: |Aut(G_P*)|, |Orbits|, "
    )

    parser.add_argument(
        "--save-trees",
        nargs="?",
        const="",
        default=None,
        metavar="FILE_NAME",
        help="Save all spanning trees, uses <polytope_name>.jsonl as default."
    )

    args = parser.parse_args()

    # --------------- RUN PIPELINE ---------------
    polytope_name = args.polytope
    dual_graph = polytope_builder.POLYTOPE_NAME_MAP[polytope_name].dual_graph()

    if args.info:
        pipeline.polytope_info(dual_graph, polytope_name)
        sys.exit(0)

    start = time.perf_counter()

    edge_index, unique_trees = pipeline.unique_unfoldings(dual_graph)

    end = time.perf_counter()

    # --------------- SHOW RESULTS ---------------
    print("\r----------- RESULTS -----------\n", end="", flush=True)
    print(f"Runtime: {end - start:.6f} seconds")
    print(f"Number of unique unfoldings: {len(unique_trees)}")

    # --------------- WRITE RESULTS ---------------
    if args.save_trees is None:
        pass
    elif args.save_trees == "":
        save_path = utils.DATA / (polytope_name + ".jsonl")
        utils.save_unfoldings(save_path, dual_graph, polytope_name, unique_trees)
    else:
        save_path = utils.DATA / (args.save_trees + ".jsonl")
        utils.save_unfoldings(save_path, dual_graph, polytope_name, unique_trees)

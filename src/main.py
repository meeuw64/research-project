import time
import dual_graph_generator
import argparse
import pipeline
import utils

if __name__ == "__main__":
    # --------------- PROGRAM ARGUMENTS ---------------
    parser = argparse.ArgumentParser()

    parser.add_argument("--polytope",
                        type=str,
                        required=True,
                        choices=dual_graph_generator.POLYTOPE_NAME_TO_DUAL_GRAPH.keys(),
                        help="Name of polytope to analyze")

    default_path = utils.DATA / "unfoldings.jsonl"
    parser.add_argument(
        "--save-trees",
        nargs="?",
        const=default_path,
        metavar="PATH",
        help=f"Save all spanning trees to PATH; defaults to {default_path}"
    )

    args = parser.parse_args()

    # --------------- RUN PIPELINE ---------------
    start = time.perf_counter()

    unique = pipeline.unique_unfoldings(args.polytope)
    unique_trees = list(unique.values())

    end = time.perf_counter()

    # --------------- SHOW RESULTS ---------------
    print("\r----------- RESULTS -----------\n", end="", flush=True)
    print(f"Runtime: {end - start:.6f} seconds")
    print(f"Number of unique unfoldings: {len(unique_trees)}")

    # --------------- WRITE RESULTS ---------------
    if args.save_trees:
        utils.save_unfoldings(args.save_trees, args.polytope, unique_trees)

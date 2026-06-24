import sys
import time
import argparse
import utils
from unfolding_enumeration import pipeline
from polytope_core import polytope_builder
from unfolding_plotting import geometry_generator, unfolding_plotter

if __name__ == "__main__":
    # --------------- PROGRAM ARGUMENTS ---------------
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--polytope",
        type=str,
        required=False,
        choices=polytope_builder.POLYTOPE_NAME_MAP.keys(),
        help=f"Name of polytope to analyze, available polytopes: {polytope_builder.POLYTOPE_NAME_MAP.keys()}",
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Only prints: |Aut(G_P*)|, |Orbits|",
    )

    parser.add_argument(
        "--save-trees",
        nargs="?",
        const="",
        default=None,
        metavar="FILE_NAME",
        help="Save all spanning trees, uses <polytope_name>.jsonl as default.",
    )

    parser.add_argument(
        "--render",
        nargs=2,
        metavar=("FILE_NAME", "INDEX"),
        help="Render one saved unfolding from data/<FILE_NAME>.jsonl at spanning-tree index INDEX.",
    )

    args = parser.parse_args()

    # --------------- RENDER SAVED UNFOLDING ---------------
    if args.render is not None:
        file_name, index_string = args.render

        if not file_name.endswith(".jsonl"):
            file_name += ".jsonl"

        try:
            tree_index = int(index_string)
        except ValueError:
            parser.error("INDEX must be an integer.")

        polytope, spanning_tree = utils.load_single_polytope_unfolding(
            utils.DATA / file_name,
            tree_index,
        )

        unfolding = geometry_generator.unfold_polytope(
            polytope=polytope,
            tree=spanning_tree,
            root=0,
        )

        plotter = unfolding_plotter.plot_unfolding(
            polytope,
            unfolding,
            show_cell_ids=False,
            face_opacity=1.0,
            hide_internal_faces=False,
        )
        plotter.show()
        sys.exit(0)

    # --------------- RUN PIPELINE ---------------
    if args.polytope is None:
        parser.error("--polytope is required unless --render is used.")

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

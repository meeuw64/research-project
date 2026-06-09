import utils
from unfolding_plotting import geometry_generator
from unfolding_plotting import unfolding_plotter

if __name__ == "__main__":
    polytope, spanning_tree = utils.load_single_polytope_unfolding(utils.DATA / "unfoldings.jsonl", 0)
    dual = polytope.dual_graph()

    unfolding = geometry_generator.unfold_polytope(
        polytope=polytope,
        tree=spanning_tree,
        root=0,
    )

    plotter = unfolding_plotter.plot_unfolding(polytope, unfolding, face_opacity=1.0)
    plotter.show()
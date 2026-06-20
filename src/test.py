import utils
from unfolding_plotting import geometry_generator
from unfolding_plotting import unfolding_plotter

if __name__ == "__main__":
    polytope_name = "tesseract"
    polytope1, spanning_tree1 = utils.load_single_polytope_unfolding(utils.DATA / (polytope_name + ".jsonl"), 5)
    polytope2, spanning_tree2 = utils.load_single_polytope_unfolding(utils.DATA / (polytope_name + ".jsonl"), 164)
    dual1 = polytope1.dual_graph()
    dual2 = polytope2.dual_graph()


    unfolding1 = geometry_generator.unfold_polytope(
        polytope=polytope1,
        tree=spanning_tree1,
        root=0,
    )

    unfolding2 = geometry_generator.unfold_polytope(
        polytope=polytope2,
        tree=spanning_tree2,
        root=0,
    )

    plotter = unfolding_plotter.plot_unfolding(polytope1, unfolding1, face_opacity=1.0)
    plotter.show()
    plotter = unfolding_plotter.plot_unfolding(polytope2, unfolding2, face_opacity=1.0)
    plotter.show()
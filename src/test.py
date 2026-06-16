import utils
from unfolding_plotting import unfolding_plotter, geometry_generator

polytope, spanning_tree = utils.load_single_polytope_unfolding(utils.DATA / "rectified-5-cell.jsonl", 0)
unfolding = geometry_generator.unfold_polytope(
                polytope=polytope,
                tree=spanning_tree,
                root=0,
                )
plotter = unfolding_plotter.plot_unfolding(polytope, unfolding, face_opacity=1, show_cell_ids=False, exploded_view=True, explosion_factor=1.5)

def save_screenshot():
    filename = "net_render4.png"

    plotter.screenshot(
        filename,
        transparent_background=True,
    )

    print(f"Saved {filename}")
    print("Camera position:", plotter.camera_position)

plotter.add_key_event("p", save_screenshot)

plotter.show()

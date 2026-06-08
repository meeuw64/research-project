import pyvista as pv
from polytope_core.polytope_builder import PolytopeBuilder
from unfolding_enumeration import pipeline, utils
from polytope_core.polytope import *
from geometry_generator import unfold_polytope


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------


def _cyclic_polygon_indices(points: FloatArray) -> NDArray[np.int64]:
    """Return local point indices in cyclic order around a coplanar polygon."""
    centroid = points.mean(axis=0)
    centered = points - centroid
    _, _, vh = np.linalg.svd(centered, full_matrices=False)

    coordinates_2d = np.column_stack(
        (centered @ vh[0], centered @ vh[1])
    )
    angles = np.arctan2(coordinates_2d[:, 1], coordinates_2d[:, 0])
    return np.argsort(angles).astype(np.int64)


def _cell_surface_mesh(
    polytope: Polytope,
    unfolding: Unfolding,
    cell_id: int,
    hide_internal_faces: bool,
) -> pv.PolyData:
    """Build a polygonal PyVista surface mesh for one unfolded 3-cell."""
    placement = unfolding.placements[cell_id]
    local_index = {
        vertex_id: index
        for index, vertex_id in enumerate(placement.vertex_ids)
    }

    internal_ridges: set[int] = set()
    if hide_internal_faces:
        dual = polytope.dual_graph()
        internal_ridges = {
            int(dual[cell_a][cell_b]["ridge"])
            for cell_a, cell_b in unfolding.tree.edges
        }

    faces: list[int] = []

    for ridge_id in polytope.cells[cell_id].ridges:
        if ridge_id in internal_ridges:
            continue

        ridge = polytope.ridges[ridge_id]
        ridge_indices = np.asarray(
            [local_index[vertex_id] for vertex_id in ridge.vertices],
            dtype=np.int64,
        )
        ridge_points = placement.coordinates[ridge_indices]
        order = _cyclic_polygon_indices(ridge_points)
        ordered_indices = ridge_indices[order]

        faces.append(len(ordered_indices))
        faces.extend(int(index) for index in ordered_indices)

    return pv.PolyData(
        placement.coordinates.copy(),
        faces=np.asarray(faces, dtype=np.int64),
    )


def plot_unfolding(
    polytope: Polytope,
    unfolding: Unfolding,
    show_cell_ids: bool = True,
    face_opacity: float = 0.28,
    hide_internal_faces: bool = False,
    window_size: tuple[int, int] = (1200, 900),
    off_screen: bool = False,
) -> pv.Plotter:
    """
    Create an interactive PyVista plot of the unfolded 3-cells.

    The function returns the plotter without opening the window, so call
    ``plotter.show()`` yourself. Set ``off_screen=True`` for screenshots or
    headless rendering.
    """
    plotter = pv.Plotter(
        window_size=window_size,
        off_screen=off_screen,
    )

    palette = (
        "#4C78A8",
        "#F58518",
        "#E45756",
        "#72B7B2",
        "#54A24B",
        "#EECA3B",
        "#B279A2",
        "#FF9DA6",
        "#9D755D",
        "#BAB0AC",
    )

    label_points: list[FloatArray] = []
    labels: list[str] = []

    for cell_id in sorted(unfolding.placements):
        placement = unfolding.placements[cell_id]
        mesh = _cell_surface_mesh(
            polytope,
            unfolding,
            cell_id,
            hide_internal_faces=hide_internal_faces,
        )

        plotter.add_mesh(
            mesh,
            color=palette[cell_id % len(palette)],
            opacity=face_opacity,
            show_edges=True,
            edge_color="black",
            line_width=2.0,
            name=f"cell-{cell_id}",
        )

        if show_cell_ids:
            label_points.append(placement.coordinates.mean(axis=0))
            labels.append(str(cell_id))

    if show_cell_ids and label_points:
        plotter.add_point_labels(
            np.vstack(label_points),
            labels,
            show_points=False,
            shape=None,
            always_visible=True,
            font_size=16,
            text_color="black",
            name="cell-labels",
        )

    plotter.add_axes()
    plotter.add_text("Spanning-tree unfolding", font_size=12)
    plotter.view_isometric()
    plotter.reset_camera()

    return plotter


if __name__ == "__main__":
    polytope = PolytopeBuilder.build_tetrahedral_prism()
    dual = polytope.dual_graph()

    edge_index, unfoldings = pipeline.unique_unfoldings(dual)
    unfoldings = [utils.edge_bitstring_to_graph(unfolding, dual) for unfolding in unfoldings]
    spanning_tree = unfoldings[0]

    unfolding = unfold_polytope(
        polytope=polytope,
        tree=spanning_tree,
        root=0,
    )

    print(f"Dual graph: {dual.number_of_nodes()} cells, {dual.number_of_edges()} adjacencies")
    print(f"Tree edges: {spanning_tree.number_of_edges()}")

    for cell_id in sorted(unfolding.placements):
        placement = unfolding.placements[cell_id]
        print(f"\nCell {cell_id}")
        for vertex_id, coordinate in zip(
            placement.vertex_ids,
            placement.coordinates,
        ):
            print(f"  vertex {vertex_id:2d}: {coordinate}")

    plotter = plot_unfolding(polytope, unfolding, face_opacity=1.0)
    plotter.show()

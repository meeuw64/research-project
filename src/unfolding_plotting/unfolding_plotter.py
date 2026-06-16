from __future__ import annotations

import colorsys
import pyvista as pv
from polytope_core.polytope import *


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


def _ridge_rgb(ridge_id: int) -> NDArray[np.uint8]:
    """
    Return a deterministic RGB color for a ridge.

    The golden-ratio hue spacing distributes consecutive ridge colors
    reasonably evenly around the color wheel.
    """
    golden_ratio = 0.6180339887498949
    hue = (0.08 + ridge_id * golden_ratio) % 1.0

    red, green, blue = colorsys.hsv_to_rgb(
        hue,
        0.62,
        0.92,
    )

    return np.rint(
        255.0 * np.asarray([red, green, blue])
    ).astype(np.uint8)


def _tree_ridge_ids(
    polytope: Polytope,
    unfolding: Unfolding,
) -> set[int]:
    """Return the ridges retained as hinges by the unfolding tree."""
    dual = polytope.dual_graph()

    return {
        int(dual[cell_a][cell_b]["ridge"])
        for cell_a, cell_b in unfolding.tree.edges
    }


def _cell_surface_mesh(
    polytope: Polytope,
    unfolding: Unfolding,
    cell_id: int,
    internal_ridges: set[int],
) -> pv.PolyData:
    """
    Build a polygonal surface mesh for one unfolded 3-cell.

    Each polygon receives the color associated with its original ridge.
    Consequently, the two faces corresponding to the same ridge receive
    exactly the same color.
    """
    placement = unfolding.placements[cell_id]

    local_index = {
        vertex_id: index
        for index, vertex_id in enumerate(placement.vertex_ids)
    }

    faces: list[int] = []
    face_colors: list[NDArray[np.uint8]] = []
    ridge_ids: list[int] = []

    for ridge_id in polytope.cells[cell_id].ridges:
        if ridge_id in internal_ridges:
            continue

        ridge = polytope.ridges[ridge_id]

        ridge_indices = np.asarray(
            [
                local_index[vertex_id]
                for vertex_id in ridge.vertices
            ],
            dtype=np.int64,
        )

        ridge_points = placement.coordinates[ridge_indices]
        order = _cyclic_polygon_indices(ridge_points)
        ordered_indices = ridge_indices[order]

        faces.append(len(ordered_indices))
        faces.extend(int(index) for index in ordered_indices)

        face_colors.append(_ridge_rgb(ridge_id))
        ridge_ids.append(ridge_id)

    mesh = pv.PolyData(
        placement.coordinates.copy(),
        faces=np.asarray(faces, dtype=np.int64),
    )

    mesh.cell_data["ridge_colors"] = np.asarray(
        face_colors,
        dtype=np.uint8,
    ).reshape((-1, 3))

    mesh.cell_data["ridge_ids"] = np.asarray(
        ridge_ids,
        dtype=np.int64,
    )

    return mesh


def plot_unfolding(
    polytope: Polytope,
    unfolding: Unfolding,
    show_cell_ids: bool = True,
    face_opacity: float = 0.28,
    exploded_view: bool = False,
    explosion_factor: float = 1.15,
    window_size: tuple[int, int] = (1200, 900),
    off_screen: bool = False,
) -> pv.Plotter:
    """
    Create an interactive PyVista plot of the unfolded 3-cells.

    Faces originating from the same ridge receive the same color. Thus,
    matching colors indicate which faces are paired when the polytope is
    glued back together.

    With ``hide_internal_faces=True``, faces corresponding to the hinges
    in the unfolding tree are hidden. The remaining matching face pairs
    are precisely the cut ridges.

    With ``exploded_view=True``, cell centroids are scaled away from the
    center of the unfolding while preserving each cell's orientation.

    ``explosion_factor=1.0`` leaves the cells unchanged. Values greater
    than one move the cells farther apart.
    """
    plotter = pv.Plotter(
        window_size=window_size,
        off_screen=off_screen,
    )

    cell_centroids = {
        cell_id: placement.coordinates.mean(axis=0)
        for cell_id, placement in unfolding.placements.items()
    }

    unfolding_center = np.mean(
        np.vstack(list(cell_centroids.values())),
        axis=0,
    )


    label_points: list[FloatArray] = []
    labels: list[str] = []

    for cell_id in sorted(unfolding.placements):
        mesh = _cell_surface_mesh(
            polytope=polytope,
            unfolding=unfolding,
            cell_id=cell_id,
        )

        offset = np.zeros(3, dtype=np.float64)

        if exploded_view:
            offset = (
                explosion_factor - 1.0
            ) * (
                cell_centroids[cell_id] - unfolding_center
            )

            mesh.translate(offset, inplace=True)

        if mesh.n_cells > 0:
            plotter.add_mesh(
                mesh,
                scalars="ridge_colors",
                rgb=True,
                opacity=face_opacity,
                show_edges=True,
                edge_color="black",
                line_width=2.0,
                show_scalar_bar=False,
                name=f"cell-{cell_id}",
            )

        if show_cell_ids:
            label_points.append(
                cell_centroids[cell_id] + offset
            )
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

    title = "Spanning-tree unfolding — faces colored by ridge"

    if exploded_view:
        title += " — exploded view"

    plotter.add_axes()
    plotter.add_text(title, font_size=12)
    plotter.view_isometric()
    plotter.reset_camera()

    return plotter
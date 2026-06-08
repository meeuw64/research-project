from collections import deque
from polytope_core.polytope import *


# ---------------------------------------------------------------------------
# Script for computing the 3D geometry of a polytope unfolding
# ---------------------------------------------------------------------------


def intrinsic_cell_geometry(
    polytope: Polytope,
    cell_id: int,
    tolerance: float = 1e-10,
) -> LocalCellGeometry:
    """
    Project one 3-dimensional cell from R^4 into intrinsic R^3 coordinates.

    The projection is an isometry on the affine hull of the cell.
    """
    cell = polytope.cells[cell_id]
    vertex_ids = cell.vertices
    points_4d = polytope.vertices[np.asarray(vertex_ids, dtype=int)]

    centroid = points_4d.mean(axis=0)
    centered = points_4d - centroid

    _, singular_values, vh = np.linalg.svd(centered, full_matrices=False)
    scale = max(float(singular_values[0]), 1.0)
    rank = int(np.sum(singular_values > tolerance * scale))

    if rank != 3:
        raise ValueError(
            f"Cell {cell_id} must have affine dimension 3, but its rank is {rank}."
        )

    # Columns form an orthonormal basis of the cell's affine hull in R^4.
    basis_4d = vh[:3].T
    coordinates_3d = centered @ basis_4d

    return LocalCellGeometry(
        vertex_ids=vertex_ids,
        coordinates=coordinates_3d,
    )


def _choose_stable_frame_indices(
    points: FloatArray,
    vertex_ids: tuple[int, ...],
    tolerance: float,
) -> tuple[int, int, int]:
    """Choose three well-separated non-collinear ridge vertices."""
    first = 0

    distances = np.linalg.norm(points - points[first], axis=1)
    maximum_distance = float(np.max(distances))
    if maximum_distance <= tolerance:
        raise ValueError("A ridge contains coincident vertices.")

    second_candidates = np.flatnonzero(
        np.isclose(distances, maximum_distance, rtol=1e-10, atol=tolerance)
    )
    second = min(second_candidates, key=lambda index: vertex_ids[index])

    direction = points[second] - points[first]
    direction /= np.linalg.norm(direction)

    differences = points - points[first]
    perpendicular = differences - np.outer(differences @ direction, direction)
    perpendicular_distances = np.linalg.norm(perpendicular, axis=1)
    maximum_perpendicular = float(np.max(perpendicular_distances))

    if maximum_perpendicular <= tolerance:
        raise ValueError("A ridge is collinear instead of two-dimensional.")

    third_candidates = np.flatnonzero(
        np.isclose(
            perpendicular_distances,
            maximum_perpendicular,
            rtol=1e-10,
            atol=tolerance,
        )
    )
    third = min(third_candidates, key=lambda index: vertex_ids[index])

    return first, second, third


def _orthonormal_frame(
    points: FloatArray,
    indices: tuple[int, int, int],
) -> tuple[FloatArray, FloatArray]:
    """Return an origin and a right-handed orthonormal frame."""
    first, second, third = indices
    origin = points[first]

    axis_u = points[second] - origin
    axis_u /= np.linalg.norm(axis_u)

    axis_v = points[third] - origin
    axis_v -= np.dot(axis_v, axis_u) * axis_u
    axis_v /= np.linalg.norm(axis_v)

    normal = np.cross(axis_u, axis_v)
    normal /= np.linalg.norm(normal)

    frame = np.column_stack((axis_u, axis_v, normal))
    return origin, frame


def _reflection_across_plane(
    point_on_plane: FloatArray,
    unit_normal: FloatArray,
) -> tuple[FloatArray, FloatArray]:
    """
    Return H and c for the reflection x -> H x + c across a plane.
    """
    linear = np.eye(3) - 2.0 * np.outer(unit_normal, unit_normal)
    translation = 2.0 * np.dot(unit_normal, point_on_plane) * unit_normal
    return linear, translation


def unfold_polytope(
    polytope: Polytope,
    tree: nx.Graph,
    root: int = 0,
    tolerance: float = 1e-8,
) -> Unfolding:
    """
    Realize a spanning-tree ridge unfolding in R^3.

    The root cell is placed using its intrinsic coordinates. For every tree
    edge, the child cell's shared ridge is aligned with the already placed
    parent ridge. If the two cell interiors end up on the same side of the
    ridge plane, the child is reflected through that plane.

    This produces a geometric unfolding. It does not test whether non-neighboring
    cells overlap.
    """

    if root not in tree:
        raise ValueError(f"Root cell {root} is not in the spanning tree.")

    dual = polytope.dual_graph()
    local_geometry = {
        cell_id: intrinsic_cell_geometry(polytope, cell_id)
        for cell_id in range(len(polytope.cells))
    }

    root_local = local_geometry[root]
    placements: dict[int, CellPlacement] = {
        root: CellPlacement(
            vertex_ids=root_local.vertex_ids,
            coordinates=root_local.coordinates.copy(),
            linear=np.eye(3),
            translation=np.zeros(3),
        )
    }

    parent: dict[int, int | None] = {root: None}
    hinge_ridge: dict[int, int | None] = {root: None}
    queue: deque[int] = deque([root])

    while queue:
        parent_cell = queue.popleft()
        parent_placement = placements[parent_cell]
        parent_vertices = parent_placement.vertex_map()

        for child_cell in tree.neighbors(parent_cell):
            if child_cell in placements:
                continue

            ridge_id = int(dual[parent_cell][child_cell]["ridge"])
            ridge = polytope.ridges[ridge_id]
            ridge_vertex_ids = tuple(sorted(ridge.vertices))

            child_local = local_geometry[child_cell]
            child_local_vertices = child_local.vertex_map()

            source_ridge = np.vstack(
                [child_local_vertices[vertex_id] for vertex_id in ridge_vertex_ids]
            )
            target_ridge = np.vstack(
                [parent_vertices[vertex_id] for vertex_id in ridge_vertex_ids]
            )

            frame_indices = _choose_stable_frame_indices(
                source_ridge,
                ridge_vertex_ids,
                tolerance,
            )
            source_origin, source_frame = _orthonormal_frame(
                source_ridge,
                frame_indices,
            )
            target_origin, target_frame = _orthonormal_frame(
                target_ridge,
                frame_indices,
            )

            # Column-vector form: x_world = linear @ x_local + translation.
            linear = target_frame @ source_frame.T
            translation = target_origin - linear @ source_origin

            child_coordinates = (
                child_local.coordinates @ linear.T + translation
            )

            # Confirm that every shared ridge vertex agrees, not just the three
            # vertices used to construct the frame.
            temporary_vertex_map = {
                vertex_id: child_coordinates[index]
                for index, vertex_id in enumerate(child_local.vertex_ids)
            }
            fitted_ridge = np.vstack(
                [temporary_vertex_map[vertex_id] for vertex_id in ridge_vertex_ids]
            )
            fit_error = float(
                np.max(np.linalg.norm(fitted_ridge - target_ridge, axis=1))
            )

            if fit_error > tolerance:
                raise ValueError(
                    f"Cells {parent_cell} and {child_cell} disagree geometrically "
                    f"on ridge {ridge_id}; maximum alignment error is {fit_error}."
                )

            ridge_normal = target_frame[:, 2]
            parent_centroid = parent_placement.coordinates.mean(axis=0)
            child_centroid = child_coordinates.mean(axis=0)

            parent_side = float(
                np.dot(parent_centroid - target_origin, ridge_normal)
            )
            child_side = float(
                np.dot(child_centroid - target_origin, ridge_normal)
            )

            if abs(parent_side) <= tolerance or abs(child_side) <= tolerance:
                raise ValueError(
                    f"Could not determine the interior side of ridge {ridge_id}."
                )

            # A net places adjacent cell interiors on opposite sides of the
            # shared ridge plane.
            if parent_side * child_side > 0.0:
                reflection_linear, reflection_translation = (
                    _reflection_across_plane(target_origin, ridge_normal)
                )

                linear = reflection_linear @ linear
                translation = (
                    reflection_linear @ translation + reflection_translation
                )
                child_coordinates = (
                    child_local.coordinates @ linear.T + translation
                )

            placements[child_cell] = CellPlacement(
                vertex_ids=child_local.vertex_ids,
                coordinates=child_coordinates,
                linear=linear,
                translation=translation,
            )
            parent[child_cell] = parent_cell
            hinge_ridge[child_cell] = ridge_id
            queue.append(child_cell)

    return Unfolding(
        placements=placements,
        tree=tree,
        root=root,
        parent=parent,
        hinge_ridge=hinge_ridge,
    )

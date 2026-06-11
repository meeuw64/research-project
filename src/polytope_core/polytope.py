from __future__ import annotations

from dataclasses import dataclass
import networkx as nx
from numpy.typing import NDArray
import numpy as np

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class Ridge:
    """A 2-face of a convex 4-polytope."""

    vertices: tuple[int, ...]
    incident_cells: tuple[int, int]


@dataclass(frozen=True)
class Cell:
    """A 3-dimensional facet of a convex 4-polytope."""

    ridges: tuple[int, ...]
    vertices: tuple[int, ...]


@dataclass
class Polytope:
    """
    Minimal geometric representation used by the unfolding algorithm.

    vertices
        Shape (number_of_vertices, 4), containing coordinates in R^4.
    ridges
        The 2-faces. Every ridge must be incident to exactly two cells.
    cells
        The 3-dimensional facets.
    """

    vertices: FloatArray
    ridges: list[Ridge]
    cells: list[Cell]

    def __post_init__(self) -> None:
        self.vertices = np.asarray(self.vertices, dtype=np.float64)

    def dual_graph(self) -> nx.Graph:
        """
        Return the cell-neighbor graph.

        A graph node is a cell ID. Every graph edge has a ``ridge``
        attribute containing the ID of the shared ridge.
        """
        graph = nx.Graph()
        graph.add_nodes_from(range(len(self.cells)))

        for ridge_id, ridge in enumerate(self.ridges):
            cell_a, cell_b = ridge.incident_cells

            if graph.has_edge(cell_a, cell_b):
                raise ValueError(
                    f"Cells {cell_a} and {cell_b} share multiple ridges; "
                    "a simple dual graph cannot represent this input."
                )

            graph.add_edge(cell_a, cell_b, ridge=ridge_id)

        return graph


@dataclass(frozen=True)
class LocalCellGeometry:
    """Intrinsic R^3 coordinates of one cell."""

    vertex_ids: tuple[int, ...]
    coordinates: FloatArray

    def vertex_map(self) -> dict[int, FloatArray]:
        return {
            vertex_id: self.coordinates[index]
            for index, vertex_id in enumerate(self.vertex_ids)
        }


@dataclass(frozen=True)
class CellPlacement:
    """One unfolded cell placed in the common R^3 net."""

    vertex_ids: tuple[int, ...]
    coordinates: FloatArray
    linear: FloatArray
    translation: FloatArray

    def vertex_map(self) -> dict[int, FloatArray]:
        return {
            vertex_id: self.coordinates[index]
            for index, vertex_id in enumerate(self.vertex_ids)
        }


@dataclass
class Unfolding:
    placements: dict[int, CellPlacement]
    tree: nx.Graph
    root: int
    parent: dict[int, int | None]
    hinge_ridge: dict[int, int | None]

    def is_congruent_to(
        self,
        other: "Unfolding",
        tol: float = 1e-8,
    ) -> bool:
        """
        Return whether one global Euclidean isometry maps this unfolding
        onto ``other``.

        Correspondence is determined by ``(cell_id, vertex_id)``. This is
        important because one polytope vertex may occur at several distinct
        positions in an unfolding after cuts are made.

        The permitted isometry is

            x -> x @ Q + t

        where Q is any orthogonal 3x3 matrix. Thus rotations, reflections,
        and translations are all allowed.
        """
        if not isinstance(other, Unfolding):
            return False

        if tol < 0.0:
            raise ValueError("tol must be non-negative.")

        def occurrence_map(
            unfolding: "Unfolding",
        ) -> dict[tuple[int, int], FloatArray]:
            occurrences: dict[tuple[int, int], FloatArray] = {}

            for cell_id, placement in unfolding.placements.items():
                coordinates = np.asarray(
                    placement.coordinates,
                    dtype=np.float64,
                )

                expected_shape = (len(placement.vertex_ids), 3)
                if coordinates.shape != expected_shape:
                    raise ValueError(
                        f"Cell {cell_id} has coordinate shape "
                        f"{coordinates.shape}; expected {expected_shape}."
                    )

                for index, vertex_id in enumerate(placement.vertex_ids):
                    key = (cell_id, vertex_id)

                    if key in occurrences:
                        raise ValueError(
                            f"Cell {cell_id} contains duplicate vertex "
                            f"{vertex_id}."
                        )

                    occurrences[key] = coordinates[index]

            return occurrences

        source_map = occurrence_map(self)
        target_map = occurrence_map(other)

        # The same cell-vertex occurrences must be present in both nets.
        if source_map.keys() != target_map.keys():
            return False

        if not source_map:
            return True

        occurrence_keys = sorted(source_map)

        source = np.vstack(
            [source_map[key] for key in occurrence_keys]
        )
        target = np.vstack(
            [target_map[key] for key in occurrence_keys]
        )

        if not np.all(np.isfinite(source)):
            return False
        if not np.all(np.isfinite(target)):
            return False

        # Remove translation.
        source_centroid = source.mean(axis=0)
        target_centroid = target.mean(axis=0)

        source_centered = source - source_centroid
        target_centered = target - target_centroid

        # Orthogonal Procrustes problem:
        #
        #     minimize ||source_centered @ Q - target_centered||
        #
        # over every orthogonal matrix Q.
        covariance = source_centered.T @ target_centered
        left, _, right_transpose = np.linalg.svd(covariance)

        orthogonal = left @ right_transpose

        # Do not perform the usual determinant correction here. Such a
        # correction would forbid reflections by forcing det(Q) = +1.
        aligned = source_centered @ orthogonal

        errors = np.linalg.norm(
            aligned - target_centered,
            axis=1,
        )
        maximum_error = float(np.max(errors))

        # Interpret tol relative to the geometric size of the unfolding,
        # while retaining an absolute tolerance for small coordinates.
        source_radius = float(
            np.max(np.linalg.norm(source_centered, axis=1))
        )
        target_radius = float(
            np.max(np.linalg.norm(target_centered, axis=1))
        )
        scale = max(1.0, source_radius, target_radius)

        return maximum_error <= tol * scale
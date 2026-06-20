from __future__ import annotations

from dataclasses import dataclass
import networkx as nx
from numpy.typing import NDArray
import numpy as np
import hashlib

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
        Fast congruence fingerprint for two unfoldings.

        This method collects every placed
        cell-local vertex copy, computes all pairwise distances, sorts them,
        and compares the resulting distance spectra.

        Translation, rotation, and reflection do not change pairwise distances.

        The distance spectrum is cached on each Unfolding object, so repeated
        pairwise comparisons are much faster.
        """

        if tol < 0.0:
            raise ValueError("tol must be non-negative.")

        if len(self.placements) != len(other.placements):
            return False

        def all_points(unfolding):
            point_blocks = []

            for placement in unfolding.placements.values():
                coordinates = np.asarray(placement.coordinates, dtype=np.float64)

                if coordinates.ndim != 2 or coordinates.shape[1] != 3:
                    return None

                if not np.all(np.isfinite(coordinates)):
                    return None

                point_blocks.append(coordinates)

            if not point_blocks:
                return np.empty((0, 3), dtype=np.float64)

            return np.vstack(point_blocks)

        def cache_key(points):
            contiguous = np.ascontiguousarray(points, dtype=np.float64)
            digest = hashlib.blake2b(
                contiguous.view(np.uint8),
                digest_size=16,
            ).digest()

            return (
                contiguous.shape,
                contiguous.dtype.str,
                digest,
            )

        def distance_spectrum(unfolding):
            points = all_points(unfolding)

            if points is None:
                return None, None

            key = cache_key(points)

            cached = getattr(unfolding, "_congruence_distance_spectrum_cache", None)

            if cached is not None:
                cached_key, cached_spectrum = cached

                if cached_key == key:
                    return points, cached_spectrum

            n = len(points)

            if n < 2:
                spectrum = np.empty(0, dtype=np.float64)
            else:
                # Squared pairwise distances using a Gram matrix:
                #
                # ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a.b
                #
                # This avoids a Python loop over all pairs.
                squared_norms = np.einsum("ij,ij->i", points, points)
                squared_distances = (
                        squared_norms[:, np.newaxis]
                        + squared_norms[np.newaxis, :]
                        - 2.0 * points @ points.T
                )

                # Numerical roundoff can create tiny negative values.
                np.maximum(squared_distances, 0.0, out=squared_distances)

                upper_i, upper_j = np.triu_indices(n, k=1)
                spectrum = np.sqrt(squared_distances[upper_i, upper_j])
                spectrum.sort()

            setattr(
                unfolding,
                "_congruence_distance_spectrum_cache",
                (key, spectrum),
            )

            return points, spectrum

        points_a, spectrum_a = distance_spectrum(self)
        points_b, spectrum_b = distance_spectrum(other)

        if points_a is None or points_b is None:
            return False

        if points_a.shape != points_b.shape:
            return False

        if spectrum_a.shape != spectrum_b.shape:
            return False

        scale = max(
            1.0,
            float(spectrum_a[-1]) if spectrum_a.size else 1.0,
            float(spectrum_b[-1]) if spectrum_b.size else 1.0,
        )

        return bool(
            np.allclose(
                spectrum_a,
                spectrum_b,
                rtol=tol,
                atol=tol * scale,
            )
        )
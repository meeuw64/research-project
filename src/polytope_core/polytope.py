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

    def mesh_vertices_array(self, tol: float = 1e-8) -> FloatArray:
        unique_vertices: list[np.ndarray] = []

        for placement in self.placements.values():
            for coordinate in placement.coordinates:
                for existing in unique_vertices:
                    if np.allclose(
                        coordinate,
                        existing,
                        atol=tol,
                        rtol=0.0,
                    ):
                        break
                else:
                    unique_vertices.append(coordinate)

        return np.asarray(unique_vertices, dtype=np.float64)

    @staticmethod
    def _canonical_cloud(cloud: FloatArray) -> FloatArray:
        """
        Transform a centered point cloud into a canonical frame.
        """

        frame = Unfolding._canonical_frame(cloud)

        candidates = []

        for sign in (1.0, -1.0):
            transformed = cloud @ frame.T

            transformed[:, 2] *= sign

            order = np.lexsort(
                (
                    np.round(transformed[:, 2], 12),
                    np.round(transformed[:, 1], 12),
                    np.round(transformed[:, 0], 12),
                )
            )

            candidates.append(
                np.round(transformed[order], 12)
            )

        return min(
            candidates,
            key=lambda array: array.tobytes(),
        )

    @staticmethod
    def _canonical_frame(cloud: FloatArray) -> FloatArray:
        """
        Construct a deterministic orthonormal basis from the cloud.
        """

        norms = np.linalg.norm(cloud, axis=1)

        first_index = np.argmax(norms)
        e1 = cloud[first_index]
        e1 /= np.linalg.norm(e1)

        residuals = cloud - np.outer(cloud @ e1, e1)

        residual_norms = np.linalg.norm(residuals, axis=1)

        second_index = np.argmax(residual_norms)

        e2 = residuals[second_index]
        e2 /= np.linalg.norm(e2)

        e3 = np.cross(e1, e2)
        e3 /= np.linalg.norm(e3)

        return np.vstack((e1, e2, e3))

    def is_congruent_to(
            self,
            other: "Unfolding",
            tol: float = 1e-8,
    ) -> bool:
        """
        Congruency up to translation, rotation and reflection.

        Uses canonical registration of the vertex clouds.
        """

        vertices_a = self.mesh_vertices_array(tol)
        vertices_b = other.mesh_vertices_array(tol)

        if len(vertices_a) != len(vertices_b):
            return False

        if len(vertices_a) == 0:
            return True

        cloud_a = vertices_a - vertices_a.mean(axis=0)
        cloud_b = vertices_b - vertices_b.mean(axis=0)

        canonical_a = self._canonical_cloud(cloud_a)
        canonical_b = self._canonical_cloud(cloud_b)

        return np.allclose(
            canonical_a,
            canonical_b,
            atol=tol,
            rtol=0.0,
        )
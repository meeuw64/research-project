from __future__ import annotations

from dataclasses import dataclass
import networkx as nx
from numpy.typing import NDArray
from scipy.spatial.distance import pdist
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

    # converts the unfolding to a point cloud of the vertices
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

    def is_congruent_to(
        self,
        other: "Unfolding",
        tol: float = 1e-8,
    ) -> bool:
        """
        Check whether two unfoldings are congruent up to
        translation, rotation, and reflection.

        Uses pairwise distance invariants of the vertex clouds.
        """

        vertices_a = self.mesh_vertices_array(tol)
        vertices_b = other.mesh_vertices_array(tol)

        if len(vertices_a) != len(vertices_b):
            return False

        if len(vertices_a) <= 1:
            return True

        distances_a = np.sort(pdist(vertices_a))
        distances_b = np.sort(pdist(vertices_b))

        return np.allclose(
            distances_a,
            distances_b,
            atol=tol,
            rtol=0.0,
        )
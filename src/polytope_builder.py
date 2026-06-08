from __future__ import annotations
from itertools import combinations, product, permutations
import numpy as np
from polytope import Polytope
from polytope import Ridge
from polytope import Cell


class PolytopeBuilder:

    @staticmethod
    def build_tesseract() -> Polytope:
        """Construct a tesseract centered at the origin."""
        signs = list(product((-1, 1), repeat=4))
        vertices = np.asarray(signs, dtype=np.float64) * (1 / 2.0)

        # A cubic cell is determined by fixing one coordinate to -1 or +1.
        cell_descriptions: list[tuple[int, int]] = []
        cell_vertices: list[tuple[int, ...]] = []

        for coordinate in range(4):
            for value in (-1, 1):
                vertex_ids = tuple(
                    vertex_id
                    for vertex_id, sign_vector in enumerate(signs)
                    if sign_vector[coordinate] == value
                )
                cell_descriptions.append((coordinate, value))
                cell_vertices.append(tuple(sorted(vertex_ids)))

        # A square ridge is determined by fixing two coordinates.
        ridges: list[Ridge] = []
        cell_ridges: list[list[int]] = [
            [] for _ in range(len(cell_descriptions))
        ]

        for coordinate_a, coordinate_b in combinations(range(4), 2):
            for value_a in (-1, 1):
                for value_b in (-1, 1):
                    ridge_vertices = tuple(
                        sorted(
                            vertex_id
                            for vertex_id, sign_vector in enumerate(signs)
                            if sign_vector[coordinate_a] == value_a
                            and sign_vector[coordinate_b] == value_b
                        )
                    )

                    cell_a = cell_descriptions.index((coordinate_a, value_a))
                    cell_b = cell_descriptions.index((coordinate_b, value_b))
                    ridge_id = len(ridges)

                    ridges.append(
                        Ridge(
                            vertices=ridge_vertices,
                            incident_cells=(cell_a, cell_b),
                        )
                    )
                    cell_ridges[cell_a].append(ridge_id)
                    cell_ridges[cell_b].append(ridge_id)

        cells = [
            Cell(
                ridges=tuple(sorted(cell_ridges[cell_id])),
                vertices=cell_vertices[cell_id],
            )
            for cell_id in range(len(cell_descriptions))
        ]

        return Polytope(vertices=vertices, ridges=ridges, cells=cells)

    @staticmethod
    def build_16_cell() -> Polytope:

        #
        # vertices
        #

        vertices = np.array(
            [
                [1, 0, 0, 0],
                [-1, 0, 0, 0],

                [0, 1, 0, 0],
                [0, -1, 0, 0],

                [0, 0, 1, 0],
                [0, 0, -1, 0],

                [0, 0, 0, 1],
                [0, 0, 0, -1],
            ],
            dtype=float,
        )

        #
        # 16 tetrahedral cells
        #

        opposite_pairs = [
            (0, 1),
            (2, 3),
            (4, 5),
            (6, 7),
        ]

        cell_vertices = []

        for choice in product((0, 1), repeat=4):
            verts = tuple(
                opposite_pairs[i][choice[i]]
                for i in range(4)
            )

            cell_vertices.append(tuple(sorted(verts)))

        #
        # ridges
        #

        ridge_to_cells = {}

        for cell_id, verts in enumerate(cell_vertices):

            #
            # tetrahedron faces
            #

            for face in combinations(verts, 3):
                face = tuple(sorted(face))

                ridge_to_cells.setdefault(
                    face,
                    []
                ).append(cell_id)

        ridges = []

        cell_ridges = [[] for _ in range(len(cell_vertices))]

        for ridge_id, (face, cells) in enumerate(
                ridge_to_cells.items()
        ):

            assert len(cells) == 2

            ridges.append(
                Ridge(
                    vertices=face,
                    incident_cells=tuple(cells),
                )
            )

            for c in cells:
                cell_ridges[c].append(ridge_id)

        #
        # cells
        #

        cells = []

        for verts, rids in zip(
                cell_vertices,
                cell_ridges,
        ):
            cells.append(
                Cell(
                    vertices=verts,
                    ridges=tuple(sorted(rids)),
                )
            )

        return Polytope(
            vertices=vertices,
            ridges=ridges,
            cells=cells,
        )


    @staticmethod
    def build_rectified_5_cell():

        verts5 = np.asarray(
            sorted(set(permutations((1, 1, 1, 0, 0)))),
            dtype=float,
        )

        verts4 = project_to_R4(verts5)

        cells_vertices = []

        #
        # tetrahedra
        #

        for i in range(5):
            cells_vertices.append(
                tuple(
                    j
                    for j, v in enumerate(verts5)
                    if v[i] == 1
                )
            )

        #
        # octahedra
        #

        for i in range(5):
            cells_vertices.append(
                tuple(
                    j
                    for j, v in enumerate(verts5)
                    if v[i] == 0
                )
            )

        #
        # ridges
        #

        ridges = []
        cell_ridges = [[] for _ in range(10)]

        for a in range(10):

            for b in range(a + 1, 10):

                inter = sorted(
                    set(cells_vertices[a])
                    &
                    set(cells_vertices[b])
                )

                if len(inter) == 3:
                    rid_id = len(ridges)

                    ridges.append(
                        Ridge(
                            vertices=tuple(inter),
                            incident_cells=(a, b),
                        )
                    )

                    cell_ridges[a].append(rid_id)
                    cell_ridges[b].append(rid_id)

        cells = [
            Cell(
                vertices=tuple(sorted(vs)),
                ridges=tuple(sorted(rs)),
            )
            for vs, rs in zip(
                cells_vertices,
                cell_ridges,
            )
        ]

        return Polytope(
            vertices=verts4,
            ridges=ridges,
            cells=cells,
        )

def project_to_R4(points):

    centroid = points.mean(axis=0)

    U, S, VT = np.linalg.svd(points - centroid)

    basis = VT[:4]

    return (points - centroid) @ basis.T
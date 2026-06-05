import networkx as nx
import numpy as np


def opposite(label):
    return ("-" if label[0] == "+" else "+") + label[1]


def compute_tesseract_unfolding(tree):
    root = "+x"

    centroids = {
        root: np.array([0, 0, 0], dtype=float)
    }

    # For the root +x cube, its local 3D axes are y, z, w.
    axes = {
        root: {
            "+y": np.array([1, 0, 0], dtype=float),
            "-y": np.array([-1, 0, 0], dtype=float),
            "+z": np.array([0, 1, 0], dtype=float),
            "-z": np.array([0, -1, 0], dtype=float),
            "+w": np.array([0, 0, 1], dtype=float),
            "-w": np.array([0, 0, -1], dtype=float),
        }
    }

    for parent, child in nx.bfs_edges(tree, root):
        # child is attached in the direction of the child's 4D normal,
        # as seen from the parent cube
        move_dir = axes[parent][child]

        centroids[child] = centroids[parent] + move_dir

        # Child orientation is inherited, except the parent normal
        # becomes the direction back toward the parent.
        child_axes = axes[parent].copy()

        child_axes[parent] = -move_dir
        child_axes[opposite(parent)] = move_dir

        # Remove child's own normal directions because those are no longer
        # directions inside the child cube.
        child_axes.pop(child, None)
        child_axes.pop(opposite(child), None)

        axes[child] = child_axes

    return list(centroids.values())
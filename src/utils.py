import pickle
import networkx as nx
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIGURES = ROOT / "figures"


def load_spanning_trees(filename):
    """
    Load spanning trees from /data directory.

    Parameters
    ----------
    filename : str
        Name of the pickle file, e.g. "tesseract_trees.pkl"

    Returns
    -------
    list[nx.Graph]
        List of NetworkX graph objects.
    """
    path = DATA / filename

    with open(path, "rb") as f:
        trees = pickle.load(f)

    return trees
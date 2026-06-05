import pyvista as pv
import pipeline
import utils
import dual_graph_generator
from src import geometry_generator

polytope = "tesseract"
graph = dual_graph_generator.POLYTOPE_NAME_TO_DUAL_GRAPH[polytope]
edge_index, unfoldings = pipeline.unique_unfoldings(polytope)
unfoldings = [utils.edge_bitstring_to_graph(unfolding, graph) for unfolding in unfoldings]

def plot_cubes(centroids):
    mesh = pv.merge([pv.Cube(center=c) for c in centroids])
    surface = mesh.extract_surface(algorithm="dataset_surface")

    pl = pv.Plotter()
    pl.add_mesh(surface, show_edges=True, opacity=0.6)
    pl.show()


tree = unfoldings[0]
plot_cubes(geometry_generator.compute_tesseract_unfolding(tree))
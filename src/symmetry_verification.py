from itertools import combinations

import networkx as nx
import utils
from unfolding_plotting import geometry_generator


def verify_unfoldings(unfoldings) -> bool:

    n = len(unfoldings)
    total_pairs = len(unfoldings) * (len(unfoldings) - 1) // 2
    congruency_found = False

    validated = 0

    # verification step
    for i, j in combinations(range(n), 2):
        unfolding_A = unfoldings[i]
        unfolding_B = unfoldings[j]

        if unfolding_A.is_congruent_to(unfolding_B):
            print(f"\nUnfolding {i} is congruent to unfolding {j}")
            congruency_found = True

        validated += 1
        print(f"\r{validated}/{total_pairs} validated, currently comparing against unfolding {i}", end="", flush=True)

    return congruency_found

if __name__ == "__main__":
    # check if generated data sets contain congruent unfoldings
    polytope, spanning_trees = utils.load_polytope_unfoldings(utils.DATA / "tesseract.jsonl")

    unfoldings = []
    for tree in spanning_trees:
        unfolding = geometry_generator.unfold_polytope(
                polytope=polytope,
                tree=tree,
                root=0,
                )
        unfoldings.append(unfolding)


    print(f"\nCongruency found: {verify_unfoldings(unfoldings)}, expected: False")

    # Verify that congruency is found in obviously congruent cases (enumerating all spanning trees of 5-cell):
    polytope, _ = utils.load_polytope_unfoldings(utils.DATA / "5-cell.jsonl")
    spanning_trees = []
    for tree in nx.SpanningTreeIterator(polytope.dual_graph()):
        spanning_trees.append(tree)

    unfoldings = []
    for tree in spanning_trees:
        unfolding = geometry_generator.unfold_polytope(
                polytope=polytope,
                tree=tree,
                root=0,
                )
        unfoldings.append(unfolding)

    congruency_found = verify_unfoldings(unfoldings)

    assert congruency_found == True, "No congruency found in set of all spanning trees of 5-cell, which is not possible"


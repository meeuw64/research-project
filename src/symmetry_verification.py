import random
import time
from itertools import combinations

import utils
from unfolding_plotting import geometry_generator

if __name__ == "__main__":
    # preparing data for verification
    polytope, spanning_trees = utils.load_polytope_unfoldings(utils.DATA / "rectified-5-cell.jsonl")
    unfoldings = []
    for tree in spanning_trees:
        unfolding = geometry_generator.unfold_polytope(
                polytope=polytope,
                tree=tree,
                root=0,
                )
        unfoldings.append(unfolding)

    n = len(unfoldings)
    total = len(unfoldings) * (len(unfoldings) - 1) // 2
    congruency_found = False

    # All possible unique unordered pairs (i < j)
    validated = 0
    pairs = list(combinations(range(n), 2))

    for i, j in pairs:
        unfolding_A = unfoldings[i]
        unfolding_B = unfoldings[j]

        print(f"\r{validated} validated, currently comparing against unfolding {i}", end="", flush=True)
        start2 = time.perf_counter_ns()
        if unfolding_A.is_congruent_to(unfolding_B):
            print(f"\nUnfolding {i} is congruent to unfolding {j}")
            congruency_found = True

        validated += 1

    print("\nCongruency found:",congruency_found)

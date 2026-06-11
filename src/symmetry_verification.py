from itertools import combinations

import utils
from unfolding_plotting import geometry_generator

if __name__ == "__main__":
    # preparing data for verification
    polytope, spanning_trees = utils.load_polytope_unfoldings(utils.DATA / "tesseract.jsonl")
    unfoldings = []
    for tree in spanning_trees:
        unfolding = geometry_generator.unfold_polytope(
                polytope=polytope,
                tree=tree,
                root=0,
                )
        unfoldings.append(unfolding)

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


    print("\nCongruency found:",congruency_found)

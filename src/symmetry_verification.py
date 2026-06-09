import utils
from unfolding_plotting import geometry_generator
from itertools import combinations

if __name__ == "__main__":
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
    total = len(unfoldings) * (len(unfoldings) - 1) // 2
    congruency_found = False

    for (i, unfolding_A), (j, unfolding_B) in combinations(enumerate(unfoldings), 2):
        done = i * (2 * n - i - 1) // 2 + (j - i)
        if done % 100:
            print(f"\r{done / total:.1%}", end="", flush=True)

        if unfolding_A.is_congruent_to(unfolding_B):
            print(f"\nUnfolding {i} is congruent to unfolding {j}")
            congruency_found = True

    print("\nCongruency found:",congruency_found)

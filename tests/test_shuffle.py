from src.core.shuffle import pick_restaurant_subset


def test_shuffle_is_deterministic():
    restaurants = [{"title": f"R{i}"} for i in range(20)]

    a = pick_restaurant_subset(restaurants, seed=1, k=5)
    b = pick_restaurant_subset(restaurants, seed=1, k=5)

    assert a == b


def test_shuffle_respects_k_limit():
    restaurants = [{"title": f"R{i}"} for i in range(20)]

    subset = pick_restaurant_subset(restaurants, seed=2, k=7)

    assert len(subset) == 7

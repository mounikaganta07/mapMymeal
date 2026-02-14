import random
from typing import List, Dict, Any

def pick_restaurant_subset(restaurants: List[Dict[str, Any]], seed: int, k: int = 12):
    if not restaurants:
        return []
    rng = random.Random(seed)
    rs = restaurants[:]
    rng.shuffle(rs)
    return rs[: min(k, len(rs))]

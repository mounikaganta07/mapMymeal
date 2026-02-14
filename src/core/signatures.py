import hashlib
def input_signature(location: str, diet: str, budget: int) -> str:
    key = f"{location.strip()}|{diet.strip()}|{int(budget)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

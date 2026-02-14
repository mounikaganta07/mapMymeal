from src.core.signatures import input_signature
def test_input_signature_same_inputs_same_hash():
    a = input_signature("Chennai", "Any", 200)
    b = input_signature("Chennai", "Any", 200)
    assert a == b


def test_input_signature_changes_when_inputs_change():
    a = input_signature("Chennai", "Any", 200)
    b = input_signature("Chennai", "Vegetarian", 200)
    c = input_signature("Bengaluru", "Any", 200)
    assert a != b
    assert a != c

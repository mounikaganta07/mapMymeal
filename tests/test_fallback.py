from src.core.fallback import fallback_meal_plan


def test_fallback_has_exactly_4_lines():
    output = fallback_meal_plan("Chennai", "Any", 300)

    lines = [line for line in output.split("\n") if line.strip()]

    assert len(lines) == 4
    assert lines[0].startswith("🍲 Breakfast:")
    assert lines[1].startswith("🍛 Lunch:")
    assert lines[2].startswith("🥪 Snacks:")
    assert lines[3].startswith("🥗 Dinner:")

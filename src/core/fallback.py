def fallback_meal_plan(location: str, diet: str, budget: int) -> str:
    """
    Demo-safe fallback when OpenRouter fails.
    Keeps the SAME strict 4-line format your UI expects.
    """
    b = int(budget)

    if diet == "Vegan":
        return (
            f"🍲 Breakfast: Poha at Local Cafe (~₹{min(150, b)})\n"
            f"🍛 Lunch: Veg meals (no dairy) at South Indian Hotel (~₹{min(300, b)})\n"
            f"🥪 Snacks: Fruit bowl + juice at Juice Center (~₹{min(180, b)})\n"
            f"🥗 Dinner: Veg pulao (no ghee) at Home Style Kitchen (~₹{min(350, b)})"
        )

    if diet == "Vegetarian":
        return (
            f"🍲 Breakfast: Idli, chutney at Tiffin Center (~₹{min(140, b)})\n"
            f"🍛 Lunch: Rice, sambar, poriyal at South Indian Hotel (~₹{min(300, b)})\n"
            f"🥪 Snacks: Tea + samosa at Snack Point (~₹{min(120, b)})\n"
            f"🥗 Dinner: Roti, paneer curry at Family Restaurant (~₹{min(380, b)})"
        )

    if diet == "Non-Vegetarian":
        return (
            f"🍲 Breakfast: Eggs bhurji, toast at Cafe (~₹{min(180, b)})\n"
            f"🍛 Lunch: Chicken curry, rice at Family Restaurant (~₹{min(400, b)})\n"
            f"🥪 Snacks: Tea + chicken puff at Bakery (~₹{min(160, b)})\n"
            f"🥗 Dinner: Roti, egg curry at Diner (~₹{min(350, b)})"
        )

    return (
        f"🍲 Breakfast: Dosa at Tiffin Center (~₹{min(160, b)})\n"
        f"🍛 Lunch: Veg thali at Restaurant (~₹{min(320, b)})\n"
        f"🥪 Snacks: Tea + bonda at Snack Point (~₹{min(130, b)})\n"
        f"🥗 Dinner: Roti, dal at Family Restaurant (~₹{min(300, b)})"
    )

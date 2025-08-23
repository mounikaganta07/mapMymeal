import streamlit as st
import requests
from textwrap import dedent
import pandas as pd

st.set_page_config(page_title="Meal Recommender", page_icon="🍽", layout="wide")
st.title("📍MapMyMeal🍲")

# ---------- Theme-aware cards (no feature changes) ----------
st.markdown("""
<style>
:root, [data-theme="light"]{
  --mm-card-bg: var(--secondary-background-color);
  --mm-card-text: var(--text-color);
  --mm-card-border: var(--background-color);
  --mm-muted: var(--secondary-text-color);
}
[data-theme="dark"]{
  --mm-card-bg: var(--secondary-background-color);
  --mm-card-text: var(--text-color);
  --mm-card-border: var(--background-color);
  --mm-muted: var(--secondary-text-color);
}

.mm-card{
  padding:12px;
  margin-bottom:12px;
  border:1px solid var(--mm-card-border);
  border-radius:12px;
  background:var(--mm-card-bg);
  color:var(--mm-card-text);
}

.mm-restaurant{
  padding:8px;
  margin-bottom:8px;
  border:1px solid var(--mm-card-border);
  border-radius:8px;
  background:var(--mm-card-bg);
  color:var(--mm-card-text);
}

.restaurant-name{ font-weight:700; color:var(--mm-card-text) !important; }
.small-muted{ font-size:12px; color:var(--mm-muted) !important; }
.mm-note{ font-size:14px; color:var(--mm-muted) !important; }

h1, h2, h3, h4, h5, h6 { color: var(--text-color) !important; }
</style>
""", unsafe_allow_html=True)

# —————————————————
# Initialize session state
# —————————————————
if "submit_clicked" not in st.session_state:
    st.session_state["submit_clicked"] = False
if "suggestion" not in st.session_state:
    st.session_state["suggestion"] = ""
if "coords" not in st.session_state:
    st.session_state["coords"] = None
if "restaurants" not in st.session_state:
    st.session_state["restaurants"] = []
if "restaurant_menus" not in st.session_state:
    st.session_state["restaurant_menus"] = {}

# —————————————————
# Load API keys from Streamlit secrets
# —————————————————

def get_secret(name: str) -> str:
    try:
        return st.secrets[name]
    except Exception:
        st.error(f"Missing secret: {name}. Add it in .streamlit/secrets.toml.")
        st.stop()

SERPAPI_KEY = get_secret("SERPAPI_KEY")
OPENROUTER_API_KEY = get_secret("OPENROUTER_API_KEY")

# —————————————————
# Helpers
# —————————————————

def geocode_location(query: str):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "meal-recommendation-app (educational use)"}
    params = {"format": "json", "q": query}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        return float(data[0]["lat"]), float(data[0]["lon"])
    except requests.RequestException as e:
        st.error(f"Error fetching coordinates: {e}")
        return None



def fetch_restaurants(lat: float, lon: float, diet: str = "Any", limit: int = 50):
    if diet == "Vegetarian":
        query = f"vegetarian restaurants"
    elif diet == "Vegan":
        query = f"vegan restaurants"
    elif diet == "Non-Vegetarian":
        query = f"non-veg restaurants"
    else:
        query = f"restaurants"

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_maps",
        "q": query,
        "google_domain": "google.com",
        "hl": "en",
        "api_key": SERPAPI_KEY,
        "ll": f"@{lat},{lon},14z",   # ✅ use lat/lon for real nearby results
    }

    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("local_results", [])
        return results[:limit]
    except requests.RequestException as e:
        st.error(f"Error fetching restaurants: {e}")
        return []

def extract_menus(restaurants):
    menus = {}
    for r in restaurants:
        name = r.get("title", "Unknown")
        menu_items = []
        if "menu" in r and isinstance(r["menu"], list):
            menu_items = [item.get("name") for item in r["menu"] if "name" in item]
        elif "menu_items" in r and isinstance(r["menu_items"], list):
            menu_items = [item.get("name") for item in r["menu_items"] if "name" in item]
        menus[name] = menu_items[:20]
    return menus

def ai_meal_plan(location: str, budget: int, diet: str, restaurants: list, menus: dict) -> str:
    lines = []
    for r in restaurants:
        name = r.get("title", "Unknown")
        rating = r.get("rating", "N/A")
        price_level = r.get("price", "N/A")
        addr = r.get("address", "")
        lines.append(f"- {name} | ⭐ {rating} | {price_level} | {addr}")
    restaurant_block = "\n".join(lines) if lines else "No restaurants found."

    menu_block = ""
    for name, items in menus.items():
        if items:
            menu_block += f"\n{name} menu: {', '.join(items)}"

    prompt = dedent(f"""
    You are a helpful Indian meal planner.
    City/Area: {location}
    Budget per meal: ₹{budget}
    Diet: {diet}

    Nearby restaurants & menus:
    {menu_block if menu_block else restaurant_block}

    Task:
    1) Suggest exactly four meal times: 🍲 Breakfast, 🍛 Lunch, 🥪 Snacks, 🥗 Dinner.
    2) Each meal should have 2–3 items.
    3) Use dishes ONLY from menus if available; otherwise realistic Indian dishes.
    4) Respect the diet strictly.
    5) Estimate prices under the budget.
    6) Output ONLY in this format:

    🍲 Breakfast: <dish 1>, <dish 2> at <restaurant> (~₹price)
    🍛 Lunch: <dish 1>, <dish 2> at <restaurant> (~₹price)
    🥪 Snacks: <dish 1>, <dish 2> at <restaurant> (~₹price)
    🥗 Dinner: <dish 1>, <dish 2> at <restaurant> (~₹price)
    """).strip()

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Meal Recommendation App",
    }

    payload = {
        "model": "inflection/inflection-3-pi",
        "messages": [
            {"role": "system", "content": "You format concise, budget-friendly Indian meal suggestions."},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=40)
        resp.raise_for_status()
        data = resp.json()
        if show_debug:
            st.write("🔍 OpenRouter raw response:", data)
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"❌ OpenRouter error: {data['error'].get('message','Unknown error')}"
        else:
            return f"⚠ Unexpected response: {data}"
    except requests.RequestException as e:
        return f"OpenRouter request failed: {e}"

# ————————————————————
# Layout
# ————————————————————
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    location = st.text_input("📍 Enter your location (e.g., Chennai, Bengaluru, Delhi)")
    budget_input = st.text_input("💰 Enter your per-meal budget greater than ₹50", placeholder="Enter amount")
    diet = st.selectbox("🥗 Choose your diet", ["Any", "Vegetarian", "Vegan", "Non-Vegetarian"])

    if st.button("Generate Meal Plan"):
        if not location:
            st.warning("⚠️ Please enter a valid location.")
        elif not budget_input:
            st.warning("⚠️ Please enter your budget.")
        elif not budget_input.isdigit() or int(budget_input) <= 50:
            st.warning("⚠️ Budget must be a number greater than ₹50.")
        else:
            budget = int(budget_input)
            st.session_state["submit_clicked"] = True
            st.session_state["suggestion"] = ""  # reset previous suggestions


with col2:
    if not st.session_state["submit_clicked"]:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.image("panda.jpg", width=360)
            st.markdown(
                """
                <div style="text-align:center; font-size:21px; color:#555; margin-top:10px;">
                    Welcome  <b>Foodie Finder!</b> 🐼<br>
                    Enter your location & budget for meals.
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        if not location:
            st.warning("Please enter a location.")
            st.stop()

        # Geocode + coordinates display
        if st.session_state["coords"] is None:
            coords = geocode_location(location)
            if not coords:
                st.error("❌ Could not find coordinates for the given location.")
                st.stop()
            st.session_state["coords"] = coords
        lat, lon = st.session_state["coords"]

        # (Fix formatting: make the numbers bold properly)
        st.markdown(f"📌 Coordinates found: **{lat:.4f}, {lon:.4f}**")

        # Fetch restaurants using lat/lon
        if not st.session_state["restaurants"]:
            restaurants = fetch_restaurants(lat, lon, diet=diet)
            if not restaurants:
                st.warning("No restaurants returned by SerpAPI.")
                st.stop()
            st.session_state["restaurants"] = restaurants
        else:
            restaurants = st.session_state["restaurants"]

        # Extract menus
        if not st.session_state["restaurant_menus"]:
            restaurant_menus = extract_menus(restaurants)
            st.session_state["restaurant_menus"] = restaurant_menus
        else:
            restaurant_menus = st.session_state["restaurant_menus"]

        # Suggestion generation function
        def generate_suggestion():
            return ai_meal_plan(
                location,
                int(budget),
                diet,
                restaurants,
                menus=restaurant_menus
            )

        # Header with shuffle button
        col_a, col_b = st.columns([0.9, 0.1])
        with col_a:
            st.subheader("✨ Recommended Meal Plan")
        with col_b:
            shuffle_clicked = st.button("🔄")

        # Generate new suggestion if first time or shuffle clicked
        if st.session_state["suggestion"] == "" or shuffle_clicked:
            with st.spinner("🍴 Cooking up your personalized meal plan..."):
                st.session_state["suggestion"] = generate_suggestion()

        # Display suggestion (keep cards, no blank ones) — now theme-aware
        for line in st.session_state["suggestion"].split("\n"):
            if line.strip():  # skip blank lines
                st.markdown(
                    f"<div class='mm-card'>{line.strip()}</div>",
                    unsafe_allow_html=True,
                )

        # Note about prices/availability — theme-aware card
        st.markdown(
            "<div class='mm-card mm-note'>💡 Note: Prices and availability may vary depending on restaurant and time.</div>",
            unsafe_allow_html=True,
        )

        # Nearby restaurants (expander kept; items now use theme-aware card)
        st.markdown("### 📍 Nearby Restaurants")
        with st.expander("📍 See nearby restaurants"):
            for r in restaurants[:8]:
                st.markdown(
                    f"""
                    <div class="mm-restaurant">
                        <b class="restaurant-name">{r.get('title','Unknown')}</b> — ⭐ {r.get('rating','N/A')} — {r.get('price','N/A')}
                        <br><span class="small-muted">{r.get("address","")}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ————————————————————
# Map
# ————————————————————
if st.session_state["submit_clicked"] and st.session_state["coords"]:
    st.markdown("## 🌍 Explore the Area")
    df_map = pd.DataFrame([{ "lat": float(st.session_state["coords"][0]),
                             "lon": float(st.session_state["coords"][1]),
                             "size": 20 }])
    st.map(df_map, zoom=12, use_container_width=True)


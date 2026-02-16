import streamlit as st
import requests
from textwrap import dedent
import pandas as pd
import time
import random
import hashlib
from src.apis.nominatim import geocode_location as _geocode_location
from src.apis.serp import fetch_restaurants as _fetch_restaurants, extract_menus
from src.apis.openrouter import chat_completions
from src.core.fallback import fallback_meal_plan



# ------------------------
# Debug flag
# ------------------------
show_debug = False

st.set_page_config(page_title="Meal Recommender", page_icon="🍽", layout="wide")

# ---------- Custom header (replaces st.title for cleaner spacing) ----------
st.markdown("""
<div class="mm-header">
  <div class="mm-header-left">
    <div class="mm-logo">📍</div>
    <div>
      <div class="mm-brand">MapMyMeal <span class="mm-brand-emoji">🍜</span></div>
      <div class="mm-tagline">Location-based AI meal planner • budget-friendly • reliable</div>
    </div>
  </div>
  <div class="mm-header-right">
    <span class="mm-badge">⚡ Cached</span>
    <span class="mm-badge">🧪 Tested</span>
    <span class="mm-badge">✅ CI</span>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)


# ---------- Theme-aware cards (no feature changes) ----------
st.markdown("""
<style>
:root, [data-theme="light"], [data-theme="dark"]{
  --mm-card-bg: var(--secondary-background-color);
  --mm-card-text: var(--text-color);
  --mm-card-border: rgba(128,128,128,0.18);
  --mm-muted: var(--secondary-text-color);
  --mm-accent: rgba(255, 165, 0, 0.20);
}

/* ============================= */
/* Page spacing + header */
/* ============================= */

/* Reduce top padding so UI doesn't feel "floating" */
.block-container{
  padding-top: 5rem !important;
}


/* Header */
.mm-header{
  display:flex;
  justify-content:space-between;
  align-items:flex-end;
  gap:16px;
  margin: 6px 0 18px 0;
}

.mm-header-left{
  display:flex;
  align-items:center;
  gap:12px;
}

.mm-logo{
  font-size:40px;
  line-height:1;
}

.mm-brand{
  font-size:44px;
  font-weight:900;
  line-height:1.05;
  color: var(--mm-card-text);
}

.mm-brand-emoji{
  font-size:28px;
}

.mm-tagline{
  margin-top:4px;
  font-size:14px;
  color: var(--mm-muted);
}

.mm-header-right{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  justify-content:flex-end;
}

.mm-badge{
  font-size:12px;
  padding:6px 10px;
  border-radius:999px;
  border:1px solid var(--mm-card-border);
  background: var(--mm-card-bg);
  color: var(--mm-card-text);
}

/* ============================= */
/* Generic Cards */
/* ============================= */

.mm-card{
  padding:16px;
  margin-bottom:12px;
  border:1px solid var(--mm-card-border);
  border-radius:14px;
  background:var(--mm-card-bg);
  color:var(--mm-card-text);
}

.mm-restaurant{
  padding:10px;
  margin-bottom:10px;
  border:1px solid var(--mm-card-border);
  border-radius:12px;
  background:var(--mm-card-bg);
  color:var(--mm-card-text);
}

.restaurant-name{
  font-weight:700;
  color:var(--mm-card-text) !important;
}

.small-muted{
  font-size:12px;
  color:var(--mm-muted) !important;
}

.mm-note{
  font-size:14px;
  color:var(--mm-muted) !important;
}

h1, h2, h3, h4, h5, h6 {
  color: var(--text-color) !important;
}

/* ============================= */
/* Form Card Styling */
/* ============================= */

.mm-form-card{
  padding:18px;
  border:1px solid var(--mm-card-border);
  border-radius:18px;
  background: var(--mm-card-bg);
  box-shadow: 0 6px 18px rgba(0,0,0,0.06);
  margin-bottom: 15px;
}

/* Premium button */
.mm-form-card div.stButton > button{
  border-radius: 12px;
  font-weight: 700;
  padding: 10px 16px;
}


/* Rounded inputs (ONLY inside our form card) */
.mm-form-card div[data-baseweb="input"] > div,
.mm-form-card div[data-baseweb="select"] > div{
  border-radius: 12px !important;
}


/* ============================= */
/* Cute Animated Hero */
/* ============================= */

.mm-hero{
  border:1px solid var(--mm-card-border);
  border-radius:22px;
  padding:22px;
  background: linear-gradient(135deg, rgba(255,165,0,0.10), var(--mm-card-bg));
  box-shadow: 0 6px 18px rgba(0,0,0,0.06);
  text-align:center;
}

/* Bowl container */
.mm-bowl{
  position:relative;
  width:90px;
  height:70px;
  margin: 0 auto 12px auto;
}

/* Bowl emoji */
.mm-bowl-emoji{
  position:absolute;
  left:50%;
  bottom:0;
  transform: translateX(-50%);
  font-size:52px;
  line-height:1;
}

/* Steam animation */
.mm-steam{
  position:absolute;
  top:0;
  left:50%;
  width:6px;
  height:18px;
  background: currentColor;
  border-radius:50px;
  opacity:0.55;
  transform: translate(var(--x, 0px), 0px) scaleY(1);
  animation: steamUp 2.5s infinite ease-in-out;
}

.mm-steam:nth-child(1){ --x: -18px; animation-delay:0s; }
.mm-steam:nth-child(2){ --x: -3px;  animation-delay:0.4s; }
.mm-steam:nth-child(3){ --x: 12px;  animation-delay:0.8s; }

@keyframes steamUp{
  0%   { transform: translate(var(--x, 0px), 0px) scaleY(1); opacity:0.55; }
  50%  { transform: translate(var(--x, 0px), -10px) scaleY(1.35); opacity:0.35; }
  100% { transform: translate(var(--x, 0px), 0px) scaleY(1); opacity:0.55; }
}

.mm-hero-title{
  font-size:24px;
  font-weight:900;
  margin:6px 0;
}

.mm-hero-sub{
  font-size:14px;
  color: var(--mm-muted);
  margin-bottom:10px;
}

.mm-chip-row{
  display:flex;
  justify-content:center;
  gap:8px;
  flex-wrap:wrap;
  margin-top:8px;
}

/* cleaner chips */
.mm-chip{
  font-size:12px;
  padding:6px 10px;
  border-radius:999px;
  border:1px solid var(--mm-card-border);
  background: transparent;
  color: var(--mm-card-text);
}

.mm-tip{
  margin-top:10px;
  font-size:12px;
  color: var(--mm-muted);
}


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
if "budget" not in st.session_state:
    st.session_state["budget"] = 500  # default value
if "last_inputs" not in st.session_state:
    st.session_state["last_inputs"] = ""
if "shuffle_seed" not in st.session_state:
    st.session_state["shuffle_seed"] = 0


def reset_on_input_change(location: str, diet: str, budget: int):
    key = f"{location}|{diet}|{budget}"
    if st.session_state.get("last_inputs") != key:
        st.session_state["last_inputs"] = key
        st.session_state["coords"] = None
        st.session_state["restaurants"] = []
        st.session_state["restaurant_menus"] = {}
        st.session_state["suggestion"] = ""
        st.session_state["shuffle_seed"] = 0



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


def pick_restaurant_subset(restaurants: list, seed: int, k: int = 12) -> list:
    if not restaurants:
        return []
    rng = random.Random(seed)
    rs = restaurants[:]
    rng.shuffle(rs)              # deterministic re-order
    return rs[:min(k, len(rs))]  # take first k after shuffle


def geocode_location(query: str):
    try:
        return _geocode_location(query)
    except requests.RequestException as e:
        st.error(f"Error fetching coordinates: {e}")
        return None


def fetch_restaurants(lat: float, lon: float, diet: str = "Any", limit: int = 50):
    try:
        return _fetch_restaurants(lat, lon, serpapi_key=SERPAPI_KEY, diet=diet, limit=limit)
    except requests.RequestException as e:
        st.error(f"Error fetching restaurants: {e}")
        return []


def ai_meal_plan(location: str, budget: int, diet: str, restaurants: list, menus: dict) -> str:
    # --- prompt is IDENTICAL to your current app.py ---
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
    Diet: {diet}
    Budget per meal (hard limit): ₹{budget}
    Nearby restaurants & menus:
    {menu_block if menu_block else restaurant_block}

    Rules (must follow):
    1) Give exactly four meals in this order only:
    🍲 Breakfast, 🍛 Lunch, 🥪 Snacks, 🥗 Dinner
    2) Meal-appropriate items ONLY:
    - Breakfast: breakfast foods (idli/dosa/poha/upma/paratha/oats/eggs etc.)
    - Lunch: full meal foods (rice/roti + curry/dal + side)
    - Snacks: ONLY snack items (tea/coffee/juice + samosa/pakoda/bonda/puffs/sandwich/chaat/fruit)
    - Dinner: light-to-regular dinner (roti/rice + curry/dal; avoid heavy biryani as “snacks”)
    3) Each meal must have 1–2 items max (keep it realistic).
    4) Use menu dishes if menus are provided. If menus are missing/empty, use realistic Indian dishes.
    5) Diet must be respected strictly:
    - Vegetarian: no meat/fish/egg
    - Vegan: no dairy/ghee/paneer/curd, no egg/meat
    - Non-Vegetarian: can include meat/egg but keep it realistic
    6) Pricing realism:
    - Keep (~₹price) <= ₹{budget}
    - Also keep prices believable: Breakfast ₹60–₹180, Lunch ₹120–₹400, Snacks ₹50–₹200, Dinner ₹120–₹450
    7) Output ONLY these 4 lines (no extra text, no bullets, no blank lines). Use this exact format:

    🍲 Breakfast: <item 1>, <item 2> at <restaurant> (~₹price)
    🍛 Lunch: <item 1>, <item 2> at <restaurant> (~₹price)
    🥪 Snacks: <item 1>, <item 2> at <restaurant> (~₹price)
    🥗 Dinner: <item 1>, <item 2> at <restaurant> (~₹price)
    """).strip()

    try:
        data = chat_completions(
            openrouter_api_key=OPENROUTER_API_KEY,
            model="inflection/inflection-3-pi",
            messages=[
                {"role": "system", "content": "You format concise, budget-friendly Indian meal suggestions."},
                {"role": "user", "content": prompt},
            ],
            timeout=40,
        )

        if show_debug:
            st.write("🔍 OpenRouter raw response:", data)

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"❌ OpenRouter error: {data['error'].get('message','Unknown error')}"
        else:
            return f"⚠ Unexpected response: {data}"

    except requests.RequestException as e:
        # same “never crash” goal; fallback keeps demo stable
        return fallback_meal_plan(location, diet, budget)


# ------------------------
# Cached wrappers (quota protection)
# ------------------------
@st.cache_data(ttl=7*24*3600, show_spinner=False)  # 7 days
def cached_geocode_location(query: str):
    return geocode_location(query)

@st.cache_data(ttl=24*3600, show_spinner=False)  # 24 hours
def cached_fetch_restaurants(lat: float, lon: float, diet: str, limit: int = 50):
    return fetch_restaurants(lat, lon, diet=diet, limit=limit)

@st.cache_data(ttl=6*3600, show_spinner=False)  # 6 hours
def cached_ai_meal_plan(location: str, budget: int, diet: str, restaurants: list, menus: dict, seed: int) -> str:
    return ai_meal_plan(location, budget, diet, restaurants, menus)



# ————————————————————
# Layout
# ————————————————————
col1, col2 = st.columns([1, 1.1])

# ==========================
# LEFT COLUMN — FORM
# ==========================
with col1:
    with st.container(border=True):
        location = st.text_input(
            "📍 Enter your location (e.g., Chennai, Bengaluru, Delhi)",
            autocomplete="off"
        )

        budget_input = st.text_input(
            "💰 Enter your per-meal budget greater than ₹50",
            placeholder="Enter amount",
            autocomplete="off"
        )

        diet = st.selectbox(
            "🥗 Choose your diet",
            ["Any", "Vegetarian", "Vegan", "Non-Vegetarian"]
        )

        submit = st.button("✨ Generate Meal Plan", use_container_width=True)

        # ✅ Wire the button click -> enables the right-side pipeline
        if submit:
            loc = (location or "").strip()
            if not loc:
                st.warning("Please enter a location.")
                st.stop()

            try:
                budget_val = int(str(budget_input).strip())
            except Exception:
                st.warning("Please enter a valid budget number (example: 150).")
                st.stop()

            if budget_val < 50:
                st.warning("Budget must be at least ₹50.")
                st.stop()

            st.session_state["budget"] = budget_val
            reset_on_input_change(loc, diet, budget_val)
            st.session_state["submit_clicked"] = True
            st.session_state["suggestion"] = ""  # refresh output cleanly



# ==========================
# RIGHT COLUMN — HERO / OUTPUT
# ==========================
with col2:

    if not st.session_state["submit_clicked"]:
        st.markdown(
            """
            <div class="mm-hero">

              <div class="mm-bowl">
                <div class="mm-steam"></div>
                <div class="mm-steam"></div>
                <div class="mm-steam"></div>
                <div class="mm-bowl-emoji">🍜</div>
              </div>

              <div class="mm-hero-title">Welcome to MapMyMeal ✨</div>

              <div class="mm-hero-sub">
                Tell me your <b>location</b>, <b>diet</b>, and <b>budget</b> —
                I’ll create a realistic 4-meal plan from nearby places.
              </div>

              <div class="mm-chip-row">
                <span class="mm-chip">📍 Location</span>
                <span class="mm-chip">🥗 Diet</span>
                <span class="mm-chip">💰 Budget</span>
                <span class="mm-chip">🔄 Shuffle</span>
              </div>

              <div class="mm-tip">
                Fresh meal ideas loading... ✨
              </div>

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
            coords = cached_geocode_location(location)
            if not coords:
                st.error("❌ Could not find coordinates for the given location.")
                st.stop()
            st.session_state["coords"] = coords
        lat, lon = st.session_state["coords"]

        st.markdown(f"📌 Coordinates found: **{lat:.4f}, {lon:.4f}**")

        # Fetch restaurants
        if not st.session_state["restaurants"]:
            restaurants = cached_fetch_restaurants(lat, lon, diet=diet)
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
            seed = st.session_state["shuffle_seed"]
            # pick different restaurants per shuffle without calling SerpAPI again
            chosen_restaurants = pick_restaurant_subset(restaurants, seed=seed, k=12)

            # build menus only for chosen restaurants (fast + varies the prompt)
            chosen_menus = extract_menus(chosen_restaurants)

            return cached_ai_meal_plan(
                location,
                st.session_state.get("budget", 500),
                diet,
                chosen_restaurants,
                chosen_menus,
                seed,
            )


        # Header with shuffle button
        col_a, col_b = st.columns([0.9, 0.1])
        with col_a:
            st.subheader("✨ Recommended Meal Plan")
        with col_b:
            shuffle_clicked = st.button("🔄")
        if shuffle_clicked:
            st.session_state["shuffle_seed"] += 1
            st.session_state["suggestion"] = ""
        st.caption(f"Shuffle seed: {st.session_state['shuffle_seed']}")



        # Generate new suggestion
        if st.session_state["suggestion"] == "" or shuffle_clicked:
            with st.spinner("🍴 Cooking up your personalized meal plan..."):
                st.session_state["suggestion"] = generate_suggestion()

        # Display suggestion
        for line in st.session_state["suggestion"].split("\n"):
            if line.strip():
                st.markdown(
                    f"<div class='mm-card'>{line.strip()}</div>",
                    unsafe_allow_html=True,
                )

        # Note
        st.markdown(
            "<div class='mm-card mm-note'>💡 Note: Prices and availability may vary depending on restaurant and time.</div>",
            unsafe_allow_html=True,
        )

        # Nearby restaurants
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
    df_map = pd.DataFrame([{
        "lat": float(st.session_state["coords"][0]),
        "lon": float(st.session_state["coords"][1]),
        "size": 20
    }])
    st.map(df_map, zoom=12, use_container_width=True)

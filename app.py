import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Weather & Health", page_icon="cloud", layout="centered")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { max-width: 700px; padding-top: 2.5rem; }

    h1 {
        font-family: 'Syne', sans-serif !important;
        font-size: 2rem !important;
        color: #0a0a0a !important;
        letter-spacing: -0.03em;
        line-height: 1.1 !important;
    }

    .w-card {
        background: #0a0a0a;
        border-radius: 20px;
        padding: 2rem 2.5rem 2.5rem;
        margin-top: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .w-card::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
        border-radius: 50%;
    }
    .w-location {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.1rem;
    }
    .w-sub { font-size: 0.85rem; color: #475569; margin-bottom: 1.8rem; }
    .w-temp {
        font-family: 'Syne', sans-serif;
        font-size: 4.5rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1;
        margin-bottom: 0.4rem;
    }
    .w-condition { font-size: 1rem; color: #94a3b8; margin-bottom: 2rem; text-transform: capitalize; }
    .stats { display: flex; gap: 0.75rem; }
    .stat {
        flex: 1;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        text-align: center;
    }
    .stat-label { font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase; color: #475569; margin-bottom: 0.3rem; }
    .stat-value { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 600; color: #e2e8f0; }

    .h-card { border-radius: 16px; padding: 1.4rem 1.75rem; margin-top: 1.2rem; border-left: 4px solid; }
    .h-card.hot  { background: #fff7ed; border-color: #f97316; }
    .h-card.cold { background: #eff6ff; border-color: #3b82f6; }
    .h-card.rain { background: #f0f9ff; border-color: #0ea5e9; }
    .h-card.wind { background: #f5f3ff; border-color: #8b5cf6; }
    .h-card.mild { background: #f0fdf4; border-color: #22c55e; }

    .h-title { font-family: 'Syne', sans-serif; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.6rem; }
    .h-card.hot  .h-title { color: #c2410c; }
    .h-card.cold .h-title { color: #1d4ed8; }
    .h-card.rain .h-title { color: #0369a1; }
    .h-card.wind .h-title { color: #6d28d9; }
    .h-card.mild .h-title { color: #15803d; }

    .h-advice { font-size: 0.9rem; color: #374151; line-height: 1.6; }
    .h-advice li { margin-bottom: 0.25rem; }

    .err { background: #fff1f2; border: 1px solid #fecdd3; border-radius: 12px; padding: 0.9rem 1.1rem; color: #be123c; font-size: 0.9rem; margin-top: 1rem; }

    div[data-testid="stTextInput"] input {
        border-radius: 12px !important;
        border: 1.5px solid #e2e8f0 !important;
        background: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        color: #0a0a0a !important;
        padding: 0.65rem 1rem !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #0a0a0a !important;
        box-shadow: 0 0 0 3px rgba(10,10,10,0.08) !important;
    }
    div[data-testid="stButton"] button {
        background: #0a0a0a !important;
        color: #f8fafc !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em;
        padding: 0.6rem 1.5rem !important;
        width: 100%;
        transition: opacity 0.2s;
    }
    div[data-testid="stButton"] button:hover { opacity: 0.8 !important; }
    .footer { text-align: center; color: #94a3b8; font-size: 0.72rem; margin-top: 2.5rem; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# WMO code helpers
# ---------------------------------------------------------------------------
WMO_LABEL = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Freezing drizzle", 57: "Heavy freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}

WMO_ICON = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️", 56: "🌨️", 57: "🌨️",
    61: "🌧️", 63: "🌧️", 65: "🌧️", 66: "🌨️", 67: "🌨️",
    71: "❄️", 73: "❄️", 75: "❄️", 77: "🌨️",
    80: "🌦️", 81: "🌧️", 82: "⛈️", 85: "🌨️", 86: "🌨️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}

RAIN_CODES = {51,53,55,56,57,61,63,65,66,67,80,81,82,85,86,95,96,99}
SNOW_CODES = {71,73,75,77}

def weather_category(code: int, temp: float, wind: float) -> str:
    if code in RAIN_CODES:
        return "rain"
    if code in SNOW_CODES or temp <= 5:
        return "cold"
    if wind >= 40:
        return "wind"
    if temp >= 28:
        return "hot"
    if temp <= 12:
        return "cold"
    return "mild"

HEALTH_ADVICE = {
    "hot": {
        "css": "hot", "title": "Hot Weather Advisory", "icon": "🌡️",
        "tips": [
            "Drink at least 2-3 litres of water throughout the day.",
            "Wear light-coloured, loose-fitting, breathable clothing.",
            "Avoid direct sun exposure between 11 am and 3 pm.",
            "Apply sunscreen (SPF 30+) and wear a wide-brimmed hat.",
            "Seek shade or air-conditioned spaces if you feel dizzy or overheated.",
        ],
    },
    "cold": {
        "css": "cold", "title": "Cold Weather Advisory", "icon": "🧥",
        "tips": [
            "Wear multiple layers — thermal base, insulating mid-layer, windproof outer layer.",
            "Cover extremities: gloves, warm socks, a hat, and a scarf.",
            "Drink warm fluids such as herbal tea, soup, or warm water.",
            "Limit prolonged time outdoors; warm up gradually when returning inside.",
            "Watch for signs of hypothermia: persistent shivering, confusion, or numbness.",
        ],
    },
    "rain": {
        "css": "rain", "title": "Rainy Weather Advisory", "icon": "☂️",
        "tips": [
            "Carry an umbrella or a waterproof rain jacket before heading out.",
            "Wear waterproof footwear to keep your feet dry.",
            "Change into dry clothes as soon as possible if you get wet.",
            "Be cautious on slippery surfaces — slow down when walking or driving.",
            "Stay indoors during thunder or lightning storms.",
        ],
    },
    "wind": {
        "css": "wind", "title": "Windy Weather Advisory", "icon": "💨",
        "tips": [
            "Wear wraparound sunglasses or goggles to protect your eyes from dust.",
            "Choose close-fitting clothing so fabric does not catch the wind.",
            "Secure loose outdoor items that could become airborne hazards.",
            "Exercise extra caution when cycling or driving high-sided vehicles.",
            "People with respiratory conditions should limit outdoor exposure.",
        ],
    },
    "mild": {
        "css": "mild", "title": "Conditions Look Good", "icon": "✅",
        "tips": [
            "Comfortable conditions — a great time for outdoor activities.",
            "Stay hydrated even in mild weather, especially if exercising.",
            "Wear a light layer in the evening as temperatures may drop.",
            "Enjoy the outdoors and make the most of the pleasant weather.",
        ],
    },
}


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def geocode(city: str):
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        return None
    d = results[0]
    return {
        "name":    d.get("name", city),
        "country": d.get("country", ""),
        "admin1":  d.get("admin1", ""),
        "lat":     d["latitude"],
        "lon":     d["longitude"],
    }

def fetch_weather(lat: float, lon: float):
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude":  lat,
            "longitude": lon,
            "current":   "temperature_2m,apparent_temperature,relative_humidity_2m,"
                         "weather_code,wind_speed_10m,wind_direction_10m",
            "wind_speed_unit": "kmh",
            "timezone":  "auto",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["current"]

def wind_compass(deg: float) -> str:
    return ["N","NE","E","SE","S","SW","W","NW"][round(deg / 45) % 8]


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("Weather & Health Advisor")
st.markdown(
    "<p style='color:#64748b;font-size:0.9rem;margin-top:-0.6rem;margin-bottom:1.8rem;'>"
    "Enter any city to get current conditions and personalised health tips.</p>",
    unsafe_allow_html=True,
)

col_in, col_btn = st.columns([4, 1])
with col_in:
    city_input = st.text_input("city", placeholder="e.g. Kumasi, London, Tokyo ...", label_visibility="collapsed")
with col_btn:
    search = st.button("Search")

if search:
    if not city_input.strip():
        st.markdown("<div class='err'>Please enter a city name before searching.</div>", unsafe_allow_html=True)
    else:
        with st.spinner("Fetching weather data..."):
            try:
                location = geocode(city_input.strip())
                if location is None:
                    st.markdown(
                        f"<div class='err'>City not found: <strong>{city_input}</strong>. "
                        "Check the spelling or try a nearby major city.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    w         = fetch_weather(location["lat"], location["lon"])
                    code      = w.get("weather_code", 0)
                    temp      = w["temperature_2m"]
                    feels     = w["apparent_temperature"]
                    humidity  = w["relative_humidity_2m"]
                    wind_spd  = w["wind_speed_10m"]
                    wind_deg  = w.get("wind_direction_10m", 0)
                    condition = WMO_LABEL.get(code, "Unknown")
                    icon      = WMO_ICON.get(code, "🌡️")
                    region    = f"{location['admin1']}, " if location["admin1"] else ""

                    st.markdown(f"""
                    <div class="w-card">
                        <div class="w-location">{icon} {location['name']}</div>
                        <div class="w-sub">{region}{location['country']}</div>
                        <div class="w-temp">{temp}°C</div>
                        <div class="w-condition">{condition}</div>
                        <div class="stats">
                            <div class="stat">
                                <div class="stat-label">Feels Like</div>
                                <div class="stat-value">{feels}°C</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Humidity</div>
                                <div class="stat-value">{humidity}%</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Wind</div>
                                <div class="stat-value">{wind_spd} km/h {wind_compass(wind_deg)}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    cat    = weather_category(code, temp, wind_spd)
                    advice = HEALTH_ADVICE[cat]
                    tips_html = "".join(f"<li>{t}</li>" for t in advice["tips"])
                    st.markdown(f"""
                    <div class="h-card {advice['css']}">
                        <div class="h-title">{advice['icon']} {advice['title']}</div>
                        <ul class="h-advice">{tips_html}</ul>
                    </div>
                    """, unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.markdown("<div class='err'>Connection failed. Check your internet connection and try again.</div>", unsafe_allow_html=True)
            except requests.exceptions.Timeout:
                st.markdown("<div class='err'>The request timed out. Please try again in a moment.</div>", unsafe_allow_html=True)
            except requests.exceptions.HTTPError as e:
                st.markdown(f"<div class='err'>API error: {e}</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='footer'>Powered by Open-Meteo — free, open-source weather API, no key required</div>",
    unsafe_allow_html=True,
)

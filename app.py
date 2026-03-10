import streamlit as st
import requests

# --- Page Config ---
st.set_page_config(page_title="Weather App", page_icon="cloud", layout="centered")

# --- Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .block-container { max-width: 680px; padding-top: 2.5rem; }

    h1 {
        font-family: 'DM Mono', monospace !important;
        font-size: 1.5rem !important;
        color: #1a1a2e !important;
        letter-spacing: -0.01em;
    }

    .card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem 2.5rem;
        margin-top: 1.5rem;
        color: white;
    }

    .card-city {
        font-family: 'DM Mono', monospace;
        font-size: 1.6rem;
        font-weight: 500;
        color: #e2e8f0;
        margin-bottom: 0.15rem;
    }

    .card-condition {
        font-size: 0.95rem;
        color: #94a3b8;
        text-transform: capitalize;
        margin-bottom: 1.8rem;
    }

    .card-temp {
        font-family: 'DM Mono', monospace;
        font-size: 4rem;
        font-weight: 500;
        color: #f1f5f9;
        line-height: 1;
        margin-bottom: 2rem;
    }

    .card-temp sup {
        font-size: 1.8rem;
        vertical-align: super;
        color: #94a3b8;
    }

    .stats-row {
        display: flex;
        gap: 1rem;
    }

    .stat {
        flex: 1;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 0.85rem 1rem;
        text-align: center;
    }

    .stat-label {
        font-size: 0.65rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 0.3rem;
    }

    .stat-value {
        font-family: 'DM Mono', monospace;
        font-size: 1.05rem;
        color: #e2e8f0;
    }

    .error-box {
        background: #fff1f2;
        border: 1px solid #fecdd3;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        color: #be123c;
        font-size: 0.9rem;
        margin-top: 1rem;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 0.9rem !important;
        background: #f8fafc !important;
        color: #1a1a2e !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #0f3460 !important;
        box-shadow: 0 0 0 3px rgba(15, 52, 96, 0.1) !important;
    }

    div[data-testid="stButton"] button {
        background: #0f3460 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.04em;
        padding: 0.55rem 1.4rem !important;
        transition: opacity 0.2s;
        width: 100%;
    }

    div[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.75rem;
        margin-top: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- WMO Weather Code Mapping ---
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Freezing drizzle", 57: "Heavy freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}

WMO_ICONS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️",
    56: "🌨️", 57: "🌨️",
    61: "🌧️", 63: "🌧️", 65: "🌧️",
    66: "🌨️", 67: "🌨️",
    71: "❄️", 73: "❄️", 75: "❄️", 77: "🌨️",
    80: "🌦️", 81: "🌧️", 82: "⛈️",
    85: "🌨️", 86: "🌨️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}


def geocode_city(city: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(url, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        return None
    r = results[0]
    return {
        "name": r.get("name"),
        "country": r.get("country", ""),
        "admin1": r.get("admin1", ""),
        "lat": r["latitude"],
        "lon": r["longitude"],
    }


def fetch_weather(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m",
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()["current"]


def wind_dir_label(deg: float) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[round(deg / 45) % 8]


# --- UI ---
st.title("WEATHER")
st.markdown(
    "<p style='color:#64748b; font-size:0.9rem; margin-top:-0.6rem; margin-bottom:1.5rem;'>"
    "No API key required — powered by Open-Meteo</p>",
    unsafe_allow_html=True,
)

col_in, col_btn = st.columns([4, 1])
with col_in:
    city_input = st.text_input("city", placeholder="Enter a city name...", label_visibility="collapsed")
with col_btn:
    search = st.button("Search")

if search:
    if not city_input.strip():
        st.markdown("<div class='error-box'>Please enter a city name.</div>", unsafe_allow_html=True)
    else:
        with st.spinner("Looking up weather..."):
            try:
                location = geocode_city(city_input.strip())
                if location is None:
                    st.markdown(
                        f"<div class='error-box'>City not found: <strong>{city_input}</strong>. "
                        "Check the spelling or try a nearby city.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    weather = fetch_weather(location["lat"], location["lon"])
                    code = weather.get("weather_code", 0)
                    condition = WMO_CODES.get(code, "Unknown")
                    icon = WMO_ICONS.get(code, "🌡️")
                    temp = weather["temperature_2m"]
                    feels = weather["apparent_temperature"]
                    humidity = weather["relative_humidity_2m"]
                    wind_speed = weather["wind_speed_10m"]
                    wind_deg = weather.get("wind_direction_10m", 0)
                    region = f"{location['admin1']}, " if location['admin1'] else ""

                    st.markdown(f"""
                    <div class="card">
                        <div class="card-city">{icon} {location['name']}</div>
                        <div class="card-condition">{region}{location['country']} &nbsp;·&nbsp; {condition}</div>
                        <div class="card-temp">{temp}<sup>°C</sup></div>
                        <div class="stats-row">
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
                                <div class="stat-value">{wind_speed} km/h {wind_dir_label(wind_deg)}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.markdown("<div class='error-box'>Connection failed. Check your internet connection.</div>", unsafe_allow_html=True)
            except requests.exceptions.Timeout:
                st.markdown("<div class='error-box'>Request timed out. Please try again.</div>", unsafe_allow_html=True)
            except requests.exceptions.HTTPError as e:
                st.markdown(f"<div class='error-box'>API error: {e}</div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>Data from Open-Meteo &amp; Open-Meteo Geocoding API — free and open source</div>", unsafe_allow_html=True)

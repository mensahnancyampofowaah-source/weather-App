# Weather & Health Advisor

A lightweight Streamlit web app that fetches real-time weather data for any city and provides personalised health tips based on current conditions. No API key required.

---

## Features

- Search any city or town by name
- Displays current temperature, feels-like temperature, humidity, and wind speed
- Shows a weather condition label derived from WMO weather codes
- Provides context-aware health advice for hot, cold, rainy, windy, and mild conditions
- Clean, responsive interface with no external dependencies beyond Streamlit and Requests

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| Geocoding | [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) |
| Weather data | [Open-Meteo Forecast API](https://open-meteo.com/en/docs) |
| HTTP client | [Requests](https://requests.readthedocs.io) |

Both APIs are free and open-source. No account or API key is needed.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/weather-health-advisor.git
cd weather-health-advisor

# Install dependencies
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## Project Structure

```
weather-health-advisor/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## Health Advice Logic

The app maps current conditions to one of five categories and displays the appropriate advice panel:

| Category | Trigger Condition | Advice Focus |
|---|---|---|
| Hot | Temperature 28°C or above | Hydration, sun protection, light clothing |
| Cold | Temperature 12°C or below, or snow | Layering, warm fluids, hypothermia awareness |
| Rainy | Any precipitation weather code | Umbrella, waterproof footwear, indoor safety |
| Windy | Wind speed 40 km/h or above | Eye protection, securing loose items |
| Mild | All other conditions | General wellbeing, outdoor activity |

---

## Deployment on Streamlit Cloud

1. Push this repository to GitHub (must be public)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** and select this repository
4. Set the main file path to `app.py`
5. Click **Deploy**

No environment variables or secrets are required.

---

## Dependencies

```
streamlit>=1.32.0
requests>=2.31.0
```

---

## License

This project is open source and available under the [MIT License](LICENSE).

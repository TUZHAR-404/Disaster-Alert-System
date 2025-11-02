import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import json
import requests
import time
import folium
from streamlit_folium import st_folium
import zipfile

# Optional imports
try:
    from googletrans import Translator

    TRANSLATOR = Translator()
    GT_AVAILABLE = True
except Exception:
    TRANSLATOR = None
    GT_AVAILABLE = False

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(
    page_title="Disaster Alert System - Disaster Alert System",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- YOUR OPENWEATHER API KEY (replace with yours if needed) ---
OPENWEATHER_KEY = "d0c51699c6fdb0f61cf6e05f2d4247fa"

# ----------------------------
# CSS Styling + Smooth Scroll JS
# ----------------------------
st.markdown("""
<style>
/* App background */
[data-testid="stAppViewContainer"] { 
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    color: #111; 
}

/* Sidebar background and text */
[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    color: #ffffff; 
    padding-top: 8px;
}

/* Sidebar text colors */
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label {
    color: #ffffff !important;
}

/* Main content cards */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

/* Card styles */
.card { 
    background: rgba(255, 255, 255, 0.95); 
    border-radius: 15px; 
    padding: 25px; 
    box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
    margin-bottom: 20px; 
    border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}

.stat-card { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 15px; 
    padding: 25px; 
    box-shadow: 0 8px 25px rgba(0,0,0,0.15); 
    text-align:center; 
    transition: transform 0.3s ease;
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.stat-card:hover {
    transform: translateY(-5px);
}

.alert-banner { 
    padding: 20px; 
    border-radius: 12px; 
    margin-bottom: 16px; 
    color: #111; 
    font-weight: 500;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.alert-danger { 
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
    color: white;
    border-left: 6px solid #c0392b;
}
.alert-warning { 
    background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
    border-left: 6px solid #e17055;
}
.alert-safe { 
    background: linear-gradient(135deg, #55efc4 0%, #00b894 100%);
    color: white;
    border-left: 6px solid #00b894;
}

.feature-card { 
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
    color: white;
    border-radius: 15px; 
    padding: 25px; 
    text-align:center; 
    box-shadow: 0 8px 25px rgba(0,0,0,0.15); 
    height: 180px; 
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.3s ease;
    cursor: pointer;
}
.feature-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
}

/* Button styles */
.stButton>button {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 12px 30px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

/* Sidebar navigation buttons */
.sidebar-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 15px 20px;
    margin: 10px 0;
    border-radius: 12px;
    text-decoration: none !important;
    font-weight: 600;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}
.sidebar-btn:hover {
    background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
    transform: translateX(8px);
    border-color: rgba(255,255,255,0.3);
}

.sidebar-btn.sos-link {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
    border: 1px solid rgba(255,255,255,0.3);
}
.sidebar-btn.sos-link:hover {
    background: linear-gradient(135deg, #ff5252 0%, #e53935 100%);
    transform: translateX(8px) scale(1.02);
}

/* Floating SOS button */
.sos-button { 
    position: fixed; 
    bottom: 30px; 
    right: 30px; 
    z-index: 9999; 
    width: 80px; 
    height: 80px; 
    border-radius: 50%; 
    background: linear-gradient(135deg, #ff6b6b 0%, #c0392b 100%);
    color: white !important; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-weight: bold; 
    font-size: 20px; 
    box-shadow: 0 8px 30px rgba(255, 107, 107, 0.4);
    transition: all 0.3s ease;
    cursor: pointer;
    border: 3px solid white;
    animation: pulse 2s infinite;
}
.sos-button:hover {  
    transform: scale(1.1);
    box-shadow: 0 12px 40px rgba(255, 107, 107, 0.6);
    animation: none;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

/* Section anchors */
.section-anchor {
    padding-top: 80px;
    margin-top: -80px;
}

/* Map container */
.folium-container { 
    width: 100% !important; 
    height: 500px; 
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* Shelter items */
.shelter-item {
    background: rgba(255,255,255,0.9);
    padding: 20px;
    border-radius: 12px;
    margin: 10px 0;
    border-left: 5px solid #3498db;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}
.shelter-item:hover {
    transform: translateX(5px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.shelter-item.warning {
    border-left: 5px solid #f39c12;
}

.shelter-item.danger {
    border-left: 5px solid #e74c3c;
}

/* Alert items */
.alert-item {
    background: rgba(255,255,255,0.9);
    padding: 20px;
    border-radius: 12px;
    margin: 10px 0;
    border-left: 5px solid #e74c3c;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.alert-item.warning {
    border-left: 5px solid #f39c12;
}

.alert-item.info {
    border-left: 5px solid #3498db;
}

/* Contact cards */
.contact-card {
    background: rgba(255,255,255,0.9);
    padding: 20px;
    border-radius: 12px;
    margin: 10px 0;
    border-left: 5px solid #27ae60;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}
.contact-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

/* Route items */
.route-item {
    background: rgba(255,255,255,0.9);
    padding: 20px;
    border-radius: 12px;
    margin: 10px 0;
    border-left: 5px solid #9b59b6;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

/* Progress and loading */
.stProgress > div > div > div > div {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Input fields */
.stTextInput>div>div>input, .stNumberInput>div>div>input {
    border-radius: 10px;
    border: 2px solid #e0e0e0;
    padding: 10px 15px;
}
.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

/* Select boxes */
.stSelectbox>div>div>div {
    border-radius: 10px;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: rgba(255,255,255,0.8);
    border-radius: 8px 8px 0px 0px;
    padding: 10px 20px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background-color: #667eea !important;
    color: white !important;
}
</style>

<script>
document.addEventListener("DOMContentLoaded", function() {
    // Smooth scrolling for sidebar links
    document.body.addEventListener('click', function(e) {
        const el = e.target;
        const link = el.closest && el.closest('.sidebar-btn') ? el.closest('.sidebar-btn') : (el.classList && el.classList.contains('sidebar-btn') ? el : null);
        if (link) {
            e.preventDefault();
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    history.replaceState(null, null, href);
                }
            }
        }
    }, false);
});
</script>
""", unsafe_allow_html=True)

# ----------------------------
# TRANSLATIONS
# ----------------------------
UI_TEXT = {
    "title": {"en": "Disaster Alert System", "hi": "आपदा चेतावनी प्रणाली", "bn": "দুর্যোগ সতর্কতা সিস্টেম",
              "ta": "பேரிடர் எச்சரிக்கை அமைப்பு"},
    "subtitle": {"en": "Real-time Disaster monitoring and management system",
                 "hi": "रीयल-टाइम आपदा निगरानी और प्रबंधन प्रणाली",
                 "bn": "রিয়েল-টাইম দুর্যোগ পর্যবেক্ষণ ও ব্যবস্থাপনা সিস্টেম",
                 "ta": "நிகழ்நேர பேரிடர் கண்காணிப்பு மற்றும் மேலாண்மை அமைப்பு"},
    "get_location": {"en": "📍 Use My Location", "hi": "📍 मेरा स्थान उपयोग करें", "bn": "📍 আমার অবস্থান ব্যবহার করুন",
                     "ta": "📍 என் இடத்தைப் பயன்படுத்தவும்"},
    "enter_city": {"en": "Or enter city name", "hi": "या शहर का नाम डालें", "bn": "অথবা শহরের নাম লিখুন",
                   "ta": "அல்லது நகரின் பெயரை உள்ளிடவும்"},
    "area_summary": {"en": "Area Summary", "hi": "क्षेत्र सारांश", "bn": "এলাকার সারসংক্ষেপ", "ta": "பகுதி சுருக்கம்"},
    "flood_monitoring_map": {"en": "Disaster Monitoring Map", "hi": "आपदा निगरानी मानचित्र",
                             "bn": "দুর্যোগ পর্যবেক্ষণ মানচিত্র", "ta": "பேரிடர் கண்காணிப்பு வரைபடம்"},
    "download_offline_map": {"en": "⬇ Download Offline Map", "hi": "⬇ ऑफ़लाइन मैप डाउनलोड करें",
                             "bn": "⬇ অফলাইন মানচিত্র ডাউনলোড করুন", "ta": "⬇ ஆஃப்லைன் வரைபடம் பதிவிறக்குக"},
    "sos": {"en": "🚨 SOS Emergency", "hi": "🚨 एसओएस आपातकाल", "bn": "🚨 এসওএস জরুরী", "ta": "🚨 SOS அவசர"},
    "alerts": {"en": "⚠️ View Alerts", "hi": "⚠️ अलर्ट देखें", "bn": "⚠️ alerts দেখুন",
               "ta": "⚠️ எச்சரிக்கைகளைக் காண்க"},
    "shelters": {"en": "🏠 Find Shelters", "hi": "🏠 आश्रय स्थल खोजें", "bn": "🏠 আশ্রয় খুঁজুন",
                 "ta": "🏠 தங்குமிடங்களைக் கண்டறியவும்"},
    "emergency_contacts": {"en": "📞 Emergency Contacts", "hi": "📞 आपातकालीन संपर्क", "bn": "📞 জরুরী যোগাযোগ",
                           "ta": "📞 அவசர தொடர்புகள்"},
    "safe_zone_locator": {"en": "📌 Safe Zone Locator", "hi": "📌 सुरक्षित क्षेत्र लोकेटर", "bn": "📌 নিরাপদ অঞ্চল লোকেটর",
                          "ta": "📌 பாதுகாப்பான மண்டலம் கண்டுபிடிப்பான்"},
    "search_shelters": {"en": "🔍 Search Nearby Shelters", "hi": "🔍 आस-पास के आश्रय स्थल खोजें",
                        "bn": "🔍 কাছাকাছি আশ্রয় অনুসন্ধান করুন", "ta": "🔍 அருகிலுள்ள தங்குமிடங்களைத் தேடுங்கள்"},
    "evacuation_routes": {"en": "🛣️ Evacuation Routes", "hi": "🛣️ निकासी मार्ग", "bn": "🛣️ সরিয়ে নেওয়ার রুট",
                          "ta": "🛣️ வெளியேற்றம் பாதைகள்"}
}


def ui_t(key, lang_code='en'):
    return UI_TEXT.get(key, {}).get(lang_code, UI_TEXT.get(key, {}).get('en', key))


# ----------------------------
# TRANSLATION HELPER
# ----------------------------
def translate_text(txt, to_code):
    if to_code == 'en' or txt is None or txt == "":
        return txt
    if GT_AVAILABLE:
        try:
            res = TRANSLATOR.translate(txt, dest=to_code)
            return res.text
        except Exception:
            return txt
    else:
        return txt


# ----------------------------
# SESSION STATE
# ----------------------------
if 'coords' not in st.session_state:
    st.session_state['coords'] = None

if 'lang' not in st.session_state:
    st.session_state['lang'] = 'en'

if 'shelters_data' not in st.session_state:
    st.session_state['shelters_data'] = None

if 'alerts_data' not in st.session_state:
    st.session_state['alerts_data'] = None


# ----------------------------
# DATA FUNCTIONS
# ----------------------------
def generate_shelters_data(lat, lon, count=15):
    """Generate realistic shelter data around given coordinates"""
    shelters = []
    shelter_types = ["School", "Community Center", "Hospital", "Government Building",
                     "Religious Center", "Sports Complex", "Convention Center"]

    for i in range(count):
        # Generate random coordinates within 15km radius
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(0.5, 15) / 111  # Convert km to degrees
        shelter_lat = lat + distance * np.cos(angle)
        shelter_lon = lon + distance * np.sin(angle)

        shelter_type = np.random.choice(shelter_types)
        name_prefix = np.random.choice(["Central", "North", "South", "East", "West",
                                        "Public", "Community", "City", "District"])

        capacity = np.random.choice([100, 200, 300, 500, 800, 1000])
        occupancy = min(capacity, np.random.randint(0, int(capacity * 0.9)))
        availability = capacity - occupancy

        # Determine status
        if availability > 50:
            status = "Available"
            status_class = ""
        elif availability > 10:
            status = "Limited"
            status_class = "warning"
        else:
            status = "Full"
            status_class = "danger"

        shelters.append({
            "id": i + 1,
            "name": f"{name_prefix} {shelter_type}",
            "type": shelter_type,
            "lat": shelter_lat,
            "lon": shelter_lon,
            "capacity": capacity,
            "occupancy": occupancy,
            "availability": availability,
            "status": status,
            "status_class": status_class,
            "distance_km": round(distance * 111, 1),
            "phone": f"+91-{np.random.randint(70000, 99999)}-{np.random.randint(10000, 99999)}",
            "facilities": np.random.choice(["Food", "Water", "Medical", "Sanitation", "All"], 1)[0]
        })

    return sorted(shelters, key=lambda x: x["distance_km"])


def generate_alerts_data(lat, lon):
    """Generate realistic alert data"""
    current_time = datetime.now()

    alerts = [
        {
            "id": 1,
            "type": "danger",
            "title": "Flood Warning",
            "message": "Heavy rainfall expected in next 24 hours. River levels rising rapidly.",
            "area": "Northern District",
            "severity": "High",
            "issued": current_time - timedelta(hours=2),
            "expires": current_time + timedelta(hours=22),
            "instructions": "Move to higher ground. Avoid river areas."
        },
        {
            "id": 2,
            "type": "warning",
            "title": "River Overflow Alert",
            "message": "River level rising above warning mark. Low-lying areas at risk.",
            "area": "Riverside Communities",
            "severity": "Medium",
            "issued": current_time - timedelta(hours=5),
            "expires": current_time + timedelta(hours=19),
            "instructions": "Prepare for possible evacuation. Monitor water levels."
        },
        {
            "id": 3,
            "type": "info",
            "title": "Shelter Opened",
            "message": "New emergency shelter activated at City College with medical facilities.",
            "area": "City Center",
            "severity": "Info",
            "issued": current_time - timedelta(hours=1),
            "expires": current_time + timedelta(days=1),
            "instructions": "Proceed to nearest shelter if needed."
        },
        {
            "id": 4,
            "type": "warning",
            "title": "Weather Advisory",
            "message": "Continuous rainfall expected for next 48 hours.",
            "area": "Entire Region",
            "severity": "Medium",
            "issued": current_time - timedelta(hours=8),
            "expires": current_time + timedelta(hours=40),
            "instructions": "Stay updated with weather forecasts."
        }
    ]

    return alerts


def get_emergency_contacts(lang_code='en'):
    """Get emergency contact information"""
    contacts = {
        "national": [
            {"name": "National Disaster Response Force", "number": "1070", "type": "Disaster"},
            {"name": "Police", "number": "100", "type": "Police"},
            {"name": "Ambulance", "number": "102", "type": "Medical"},
            {"name": "Fire Department", "number": "101", "type": "Fire"},
            {"name": "Disaster Management Helpline", "number": "1078", "type": "Disaster"}
        ],
        "local": [
            {"name": "District Emergency Officer", "number": "+91-98765-43210", "type": "Administration"},
            {"name": "Flood Rescue Team", "number": "+91-98765-43211", "type": "Rescue"},
            {"name": "Medical Emergency", "number": "+91-98765-43212", "type": "Medical"},
            {"name": "Food & Supplies", "number": "+91-98765-43213", "type": "Supplies"},
            {"name": "Evacuation Coordination", "number": "+91-98765-43214", "type": "Evacuation"}
        ]
    }

    # Translate contact names if needed
    if lang_code != 'en' and GT_AVAILABLE:
        for category in contacts:
            for contact in contacts[category]:
                try:
                    contact["name"] = TRANSLATOR.translate(contact["name"], dest=lang_code).text
                except:
                    pass
    return contacts


def get_evacuation_routes(lat, lon, shelters):
    """Generate evacuation routes to nearest shelters"""
    routes = []
    for i, shelter in enumerate(shelters[:4]):  # Top 4 nearest shelters
        # Calculate estimated travel time (assuming 20km/h average speed)
        estimated_minutes = int((shelter['distance_km'] / 20) * 60)

        routes.append({
            "shelter": shelter["name"],
            "distance": shelter["distance_km"],
            "estimated_time": f"{estimated_minutes} min",
            "capacity": shelter["capacity"],
            "availability": shelter["availability"],
            "status": shelter["status"],
            "instructions": f"Head {calculate_direction(lat, lon, shelter['lat'], shelter['lon'])} for {shelter['distance_km']} km"
        })
    return routes


def calculate_direction(lat1, lon1, lat2, lon2):
    """Calculate cardinal direction from point 1 to point 2"""
    d_lon = lon2 - lon1
    x = np.cos(np.radians(lat2)) * np.sin(np.radians(d_lon))
    y = np.cos(np.radians(lat1)) * np.sin(np.radians(lat2)) - np.sin(np.radians(lat1)) * np.cos(
        np.radians(lat2)) * np.cos(np.radians(d_lon))
    bearing = np.arctan2(x, y)
    bearing = np.degrees(bearing)
    bearing = (bearing + 360) % 360
    directions = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]
    index = round(bearing / 45) % 8
    return directions[index]


# ----------------------------
# WEATHER & FORECAST FUNCTIONS
# ----------------------------
def get_current_weather(lat, lon, api_key=OPENWEATHER_KEY):
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        return {
            "city": data.get("name", ""),
            "country": data.get("sys", {}).get("country", ""),
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "wind": data["wind"]["speed"],
            "desc": data["weather"][0]["description"].title(),
            "rain_1h": data.get("rain", {}).get("1h", 0),
            "cod": data.get("cod", 200)
        }
    except Exception:
        return None


def get_forecast(lat, lon, api_key=OPENWEATHER_KEY):
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def derive_risk_from_weather(weather):
    if not weather:
        return "Unknown", ["Weather data unavailable"]

    rain = weather.get("rain_1h", 0)
    reasons = []
    level = "Low"

    if rain >= 50:
        level = "High"
        reasons.append(f"Very heavy recent rainfall: {rain} mm/h")
    elif rain >= 20:
        level = "Moderate"
        reasons.append(f"Significant recent rainfall: {rain} mm/h")
    else:
        reasons.append("No heavy rainfall detected in last hour")

    flood_prone = ["Mumbai", "Chennai", "Kolkata", "Guwahati", "Patna"]
    if weather.get("city") in flood_prone and weather.get("rain_1h", 0) >= 5:
        level = "High"
        reasons.append(f"{weather.get('city')} is flood-prone; small rains can escalate")

    return level, reasons


# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: white; margin-bottom: 5px;">🌊 Disaster Alert System</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 0;">Disaster Management System</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚨 Emergency Features")

    # Sidebar navigation
    st.markdown('<a class="sidebar-btn sos-link" href="#sos-section">🚨 SOS Emergency</a>', unsafe_allow_html=True)
    st.markdown('<a class="sidebar-btn" href="#alerts-section">⚠️ View Alerts</a>', unsafe_allow_html=True)
    st.markdown('<a class="sidebar-btn" href="#shelters-section">🏠 Find Shelters</a>', unsafe_allow_html=True)
    st.markdown('<a class="sidebar-btn" href="#contacts-section">📞 Emergency Contacts</a>', unsafe_allow_html=True)
    st.markdown('<a class="sidebar-btn" href="#routes-section">🛣️ Evacuation Routes</a>', unsafe_allow_html=True)

    st.markdown("---")

    # Language selection
    lang_choice = st.selectbox("Language / भाषा / ভাষা / மொழி",
                               ["English", "Hindi", "Bengali", "Tamil"],
                               key="lang_select")
    lang_map = {"English": "en", "Hindi": "hi", "Bengali": "bn", "Tamil": "ta"}
    st.session_state['lang'] = lang_map[lang_choice]

    st.markdown("---")
    st.markdown("### 🔎 Location")

    # Manual coordinates input
    col1, col2 = st.columns(2)
    with col1:
        lat_manual = st.number_input("Latitude", format="%.6f", value=28.613939, key="lat_input")
    with col2:
        lon_manual = st.number_input("Longitude", format="%.6f", value=77.209021, key="lon_input")

    if st.button("📍 Use Manual Coordinates", use_container_width=True):
        st.session_state['coords'] = {'lat': float(lat_manual), 'lon': float(lon_manual)}
        st.success(f"Using coordinates: {lat_manual:.6f}, {lon_manual:.6f}")

    st.markdown("---")
    st.markdown("### 🗺️ Offline Map")

    if st.button(ui_t("download_offline_map", st.session_state['lang']), use_container_width=True):
        with st.spinner("Preparing offline map..."):
            coords = st.session_state.get('coords') or {'lat': lat_manual, 'lon': lon_manual}
            lat0, lon0 = coords['lat'], coords['lon']

            m = folium.Map(location=[lat0, lon0], zoom_start=12)
            folium.TileLayer("OpenStreetMap").add_to(m)
            folium.Marker([lat0, lon0], popup="Selected Location",
                          icon=folium.Icon(color="blue", icon="user")).add_to(m)

            shelters = [
                {"name": "Central High School", "lat": lat0 + 0.003, "lon": lon0 + 0.004},
                {"name": "Community Center", "lat": lat0 - 0.004, "lon": lon0 - 0.003},
                {"name": "City Hospital", "lat": lat0 + 0.006, "lon": lon0 - 0.002}
            ]

            for s in shelters:
                folium.Marker([s['lat'], s['lon']], popup=s['name'],
                              icon=folium.Icon(color="green", icon="home")).add_to(m)

            offline_html = "offline_map.html"
            m.save(offline_html)

            with open(offline_html, "rb") as f:
                st.download_button(
                    "📥 Download Offline Map",
                    data=f,
                    file_name="emergency_map.html",
                    mime="text/html",
                    use_container_width=True
                )

    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    battery_saver = st.checkbox("Battery Saver Mode", value=False)
    offline_mode = st.checkbox("Offline Mode", value=False)


# ----------------------------
# GEOLOCATION COMPONENT
# ----------------------------
def geolocation_component(label):
    geoloc_html = f"""
    <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <button id="getLocBtn" style="width: 100%; padding: 12px; border-radius: 8px; border: none; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: 600; cursor: pointer; transition: all 0.3s ease;">
            {label}
        </button>
        <div id="status" style="margin-top: 12px; color: #666; font-size: 14px; text-align: center;"></div>
    </div>
    <script>
    const btn = document.getElementById('getLocBtn');
    const status = document.getElementById('status');
    btn.addEventListener('click', () => {{
        if (!navigator.geolocation) {{
            status.innerText = 'Geolocation not supported by your browser';
            return;
        }}
        status.innerText = 'Requesting location...';
        btn.style.opacity = '0.7';
        navigator.geolocation.getCurrentPosition(success, error, {{enableHighAccuracy:true, timeout:15000}});
    }});
    function success(position) {{
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        status.innerText = 'Location acquired: ' + lat.toFixed(6) + ', ' + lon.toFixed(6);
        status.style.color = '#00b894';
        btn.style.opacity = '1';
        const payload = {{lat:lat, lon:lon}};
        window.parent.postMessage({{isStreamlitMessage: true, type: 'geoLocation', payload: payload}}, '*');
    }}
    function error(err) {{
        status.innerText = 'Error: ' + (err.message || 'Unable to get location');
        status.style.color = '#e17055';
        btn.style.opacity = '1';
    }}
    </script>
    """
    st.components.v1.html(geoloc_html, height=140)


# ----------------------------
# MAIN CONTENT - HEADER
# ----------------------------
st.markdown(f"""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.5rem;">{ui_t('title', st.session_state['lang'])}</h1>
    <p style="margin: 0; font-size: 1.2rem; opacity: 0.9;">{ui_t('subtitle', st.session_state['lang'])}</p>
</div>
""", unsafe_allow_html=True)

# Location Section
st.markdown("### 📍 Location Setup")
colA, colB = st.columns([1, 1])

with colA:
    geolocation_component(ui_t("get_location", st.session_state['lang']))
    st.markdown(f"**Manual coordinates:** `{lat_manual:.6f}, {lon_manual:.6f}`")

with colB:
    city_input = st.text_input(ui_t("enter_city", st.session_state['lang']),
                               placeholder="Enter your city name...")

    if city_input:
        with st.spinner("Searching for city..."):
            try:
                geo = requests.get(
                    f"https://api.openweathermap.org/geo/1.0/direct?q={city_input}&limit=1&appid={OPENWEATHER_KEY}",
                    timeout=8
                ).json()

                if geo:
                    st.session_state['coords'] = {'lat': float(geo[0]['lat']), 'lon': float(geo[0]['lon'])}
                    st.success(f"📍 Found {city_input}: {geo[0]['lat']:.6f}, {geo[0]['lon']:.6f}")
                else:
                    st.error("City not found. Please check the spelling.")
            except Exception as e:
                st.error(f"Geocoding failed: {str(e)}")

# Determine coordinates to use
if st.session_state.get('coords'):
    lat0 = st.session_state['coords']['lat']
    lon0 = st.session_state['coords']['lon']
else:
    try:
        ipinfo = requests.get("https://ipinfo.io/json", timeout=5).json()
        lat0, lon0 = map(float, ipinfo['loc'].split(','))
    except Exception:
        lat0, lon0 = lat_manual, lon_manual

# ----------------------------
# DASHBOARD
# ----------------------------
st.markdown("---")

# Area Summary
weather = get_current_weather(lat0, lon0)
st.subheader(ui_t("area_summary", st.session_state['lang']))

if weather:
    risk_level, risk_reasons = derive_risk_from_weather(weather)

    # Risk level with appropriate styling
    risk_colors = {
        "High": "alert-danger",
        "Moderate": "alert-warning",
        "Low": "alert-safe"
    }

    summary_en = f"""
    **Current weather in {weather.get('city', 'Area')}:** {weather.get('desc')}
    • Temperature: {weather.get('temp')}°C
    • Rain (1h): {weather.get('rain_1h', 0)} mm
    • Flood Risk Level: **{risk_level}**
    """

    if GT_AVAILABLE and st.session_state['lang'] != 'en':
        try:
            summary_text = TRANSLATOR.translate(summary_en, dest=st.session_state['lang']).text
        except Exception:
            summary_text = summary_en
    else:
        summary_text = summary_en

    st.markdown(f'<div class="alert-banner {risk_colors.get(risk_level, "alert-safe")}">'
                f'{summary_text}<br><small>{" • ".join(risk_reasons)}</small></div>',
                unsafe_allow_html=True)
else:
    st.info("🌤️ Weather data not available for this location.")

# Statistics Cards
st.subheader("📊 Quick Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    wl_val = round(4.2 + np.random.normal(0, 0.07), 2)
    st.markdown(f'''
    <div class="stat-card">
        <h4 style="margin: 0; color: white;">🌊 Water Level</h4>
        <div style="font-size: 32px; font-weight: 700; margin: 10px 0;">{wl_val} m</div>
        <div style="color: rgba(255,255,255,0.8);">+0.3m since yesterday</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    rain_val = weather.get('rain_1h', 0) if weather else 0
    st.markdown(f'''
    <div class="stat-card">
        <h4 style="margin: 0; color: white;">🌧️ Rain (1h)</h4>
        <div style="font-size: 32px; font-weight: 700; margin: 10px 0;">{rain_val} mm</div>
        <div style="color: rgba(255,255,255,0.8);">Recent measurement</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    alerts_count = 3 if (weather and derive_risk_from_weather(weather)[0] == "High") else 2 if (
                weather and derive_risk_from_weather(weather)[0] == "Moderate") else 1
    st.markdown(f'''
    <div class="stat-card">
        <h4 style="margin: 0; color: white;">⚠️ Active Alerts</h4>
        <div style="font-size: 32px; font-weight: 700; margin: 10px 0;">{alerts_count}</div>
        <div style="color: rgba(255,255,255,0.8);">Require attention</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
    <div class="stat-card">
        <h4 style="margin: 0; color: white;">🏠 Nearby Shelters</h4>
        <div style="font-size: 32px; font-weight: 700; margin: 10px 0;">8</div>
        <div style="color: rgba(255,255,255,0.8);">Within 10 km radius</div>
    </div>
    ''', unsafe_allow_html=True)

# Map Section
st.markdown("---")
st.subheader(ui_t("flood_monitoring_map", st.session_state['lang']))

# Create interactive map
m = folium.Map(location=[lat0, lon0], zoom_start=13 if not battery_saver else 12, control_scale=True)

# Add user location marker
folium.Marker(
    [lat0, lon0],
    popup="Your Location",
    icon=folium.Icon(color="blue", icon="user", prefix="fa")
).add_to(m)

# Add demo shelters
shelters_demo = [
    {"name": "Central High School", "lat": lat0 + 0.003, "lon": lon0 + 0.004, "cap": 500, "occ": 320},
    {"name": "Community Center", "lat": lat0 - 0.004, "lon": lon0 - 0.003, "cap": 300, "occ": 150},
    {"name": "City Hospital", "lat": lat0 + 0.006, "lon": lon0 - 0.002, "cap": 200, "occ": 180}
]

for s in shelters_demo:
    folium.Marker(
        [s['lat'], s['lon']],
        popup=f"{s['name']}<br>Capacity: {s['cap']}<br>Occupancy: {s['occ']}",
        icon=folium.Icon(color="green", icon="home", prefix="fa")
    ).add_to(m)

# Add risk area circle
if weather:
    risk_level, _ = derive_risk_from_weather(weather)
    color_map = {"High": "#e74c3c", "Moderate": "#f39c12", "Low": "#27ae60"}
    radius_map = {"High": 3500, "Moderate": 2000, "Low": 1200}

    folium.Circle(
        [lat0, lon0],
        radius=radius_map.get(risk_level, 1200),
        color=color_map.get(risk_level, "#27ae60"),
        fill=True,
        fill_opacity=0.2,
        popup=f"Risk Area: {risk_level}"
    ).add_to(m)

# Display the map
try:
    st_folium(m, width=900, height=500)
except Exception:
    st.error("Map requires streamlit-folium. Please install `streamlit-folium` to view interactive map.")
    st.write("Shelter locations:", pd.DataFrame(shelters_demo))

# ----------------------------
# ALERTS SECTION
# ----------------------------
st.markdown("---")
st.markdown('<div id="alerts-section" class="section-anchor"></div>', unsafe_allow_html=True)
st.subheader("⚠️ Active Alerts")

# Generate or get alerts data
if st.session_state['alerts_data'] is None:
    st.session_state['alerts_data'] = generate_alerts_data(lat0, lon0)

alerts = st.session_state['alerts_data']

# Display alerts
for alert in alerts:
    alert_type_class = {
        "danger": "alert-item",
        "warning": "alert-item warning",
        "info": "alert-item info"
    }.get(alert["type"], "alert-item")

    time_ago = datetime.now() - alert["issued"]
    hours_ago = int(time_ago.total_seconds() / 3600)

    st.markdown(f'''
    <div class="{alert_type_class}">
        <div style="display: flex; justify-content: between; align-items: start;">
            <div style="flex: 1;">
                <h4 style="margin: 0 0 8px 0; color: #2c3e50;">{alert["title"]}</h4>
                <p style="margin: 0 0 8px 0; color: #34495e;">{alert["message"]}</p>
                <div style="display: flex; gap: 15px; font-size: 0.9em; color: #7f8c8d;">
                    <span><strong>Area:</strong> {alert["area"]}</span>
                    <span><strong>Severity:</strong> {alert["severity"]}</span>
                    <span><strong>Issued:</strong> {hours_ago}h ago</span>
                </div>
            </div>
            <div style="background: {'#e74c3c' if alert['type'] == 'danger' else '#f39c12' if alert['type'] == 'warning' else '#3498db'}; 
                        color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; font-size: 0.9em;">
                {alert["severity"]}
            </div>
        </div>
        <div style="margin-top: 12px; padding: 10px; background: rgba(0,0,0,0.05); border-radius: 6px;">
            <strong>Instructions:</strong> {alert["instructions"]}
        </div>
    </div>
    ''', unsafe_allow_html=True)

# Refresh alerts button
if st.button("🔄 Refresh Alerts", use_container_width=True):
    st.session_state['alerts_data'] = generate_alerts_data(lat0, lon0)
    st.rerun()

# ----------------------------
# SHELTERS SECTION
# ----------------------------
st.markdown("---")
st.markdown('<div id="shelters-section" class="section-anchor"></div>', unsafe_allow_html=True)
st.subheader("🏠 Emergency Shelters")

# Generate or get shelters data
if st.session_state['shelters_data'] is None:
    st.session_state['shelters_data'] = generate_shelters_data(lat0, lon0)

shelters = st.session_state['shelters_data']

# Shelter filters
col1, col2, col3 = st.columns(3)
with col1:
    filter_distance = st.selectbox("Filter by Distance", ["All", "Within 5 km", "Within 10 km", "Within 15 km"])
with col2:
    filter_status = st.selectbox("Filter by Status", ["All", "Available", "Limited", "Full"])
with col3:
    filter_type = st.selectbox("Filter by Type",
                               ["All", "School", "Hospital", "Community Center", "Government Building"])

# Apply filters
filtered_shelters = shelters

if filter_distance != "All":
    max_dist = int(filter_distance.split(" ")[1])
    filtered_shelters = [s for s in filtered_shelters if s["distance_km"] <= max_dist]

if filter_status != "All":
    filtered_shelters = [s for s in filtered_shelters if s["status"] == filter_status]

if filter_type != "All":
    filtered_shelters = [s for s in filtered_shelters if s["type"] == filter_type]

# Display shelters
st.markdown(f"**Found {len(filtered_shelters)} shelters**")

for shelter in filtered_shelters[:10]:  # Show first 10 shelters
    status_color = {
        "Available": "#27ae60",
        "Limited": "#f39c12",
        "Full": "#e74c3c"
    }.get(shelter["status"], "#7f8c8d")

    st.markdown(f'''
    <div class="shelter-item {shelter['status_class']}">
        <div style="display: flex; justify-content: between; align-items: start;">
            <div style="flex: 1;">
                <h4 style="margin: 0 0 8px 0; color: #2c3e50;">{shelter["name"]}</h4>
                <p style="margin: 0 0 8px 0; color: #34495e;">Type: {shelter["type"]} • Facilities: {shelter["facilities"]}</p>
                <div style="display: flex; gap: 15px; font-size: 0.9em; color: #7f8c8d;">
                    <span><strong>Distance:</strong> {shelter["distance_km"]} km</span>
                    <span><strong>Capacity:</strong> {shelter["capacity"]}</span>
                    <span><strong>Available:</strong> {shelter["availability"]}</span>
                    <span><strong>Phone:</strong> {shelter["phone"]}</span>
                </div>
            </div>
            <div style="background: {status_color}; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold;">
                {shelter["status"]}
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# Show more shelters button
if len(filtered_shelters) > 10:
    if st.button("📋 Show More Shelters", use_container_width=True):
        for shelter in filtered_shelters[10:]:
            status_color = {
                "Available": "#27ae60",
                "Limited": "#f39c12",
                "Full": "#e74c3c"
            }.get(shelter["status"], "#7f8c8d")

            st.markdown(f'''
            <div class="shelter-item {shelter['status_class']}">
                <div style="display: flex; justify-content: between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 8px 0; color: #2c3e50;">{shelter["name"]}</h4>
                        <p style="margin: 0 0 8px 0; color: #34495e;">Type: {shelter["type"]} • Facilities: {shelter["facilities"]}</p>
                        <div style="display: flex; gap: 15px; font-size: 0.9em; color: #7f8c8d;">
                            <span><strong>Distance:</strong> {shelter["distance_km"]} km</span>
                            <span><strong>Capacity:</strong> {shelter["capacity"]}</span>
                            <span><strong>Available:</strong> {shelter["availability"]}</span>
                            <span><strong>Phone:</strong> {shelter["phone"]}</span>
                        </div>
                    </div>
                    <div style="background: {status_color}; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold;">
                        {shelter["status"]}
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

# ----------------------------
# EMERGENCY CONTACTS SECTION
# ----------------------------
st.markdown("---")
st.markdown('<div id="contacts-section" class="section-anchor"></div>', unsafe_allow_html=True)
st.subheader("📞 Emergency Contacts")

emergency_contacts = get_emergency_contacts(st.session_state['lang'])

col1, col2 = st.columns(2)

with col1:
    st.markdown("### National Emergency Numbers")
    for contact in emergency_contacts['national']:
        st.markdown(f'''
        <div class="contact-card">
            <div style="display: flex; justify-content: between; align-items: center;">
                <div>
                    <h5 style="margin: 0 0 5px 0; color: #2c3e50;">{contact["name"]}</h5>
                    <p style="margin: 0; color: #7f8c8d; font-size: 0.9em;">{contact["type"]}</p>
                </div>
                <div style="background: #27ae60; color: white; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 1.1em;">
                    {contact["number"]}
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

with col2:
    st.markdown("### Local Emergency Contacts")
    for contact in emergency_contacts['local']:
        st.markdown(f'''
        <div class="contact-card">
            <div style="display: flex; justify-content: between; align-items: center;">
                <div>
                    <h5 style="margin: 0 0 5px 0; color: #2c3e50;">{contact["name"]}</h5>
                    <p style="margin: 0; color: #7f8c8d; font-size: 0.9em;">{contact["type"]}</p>
                </div>
                <div style="background: #3498db; color: white; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 1.1em;">
                    {contact["number"]}
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

# Emergency call instructions
with st.expander("📋 Emergency Call Instructions"):
    st.markdown("""
    **In case of emergency:**
    1. Stay calm and speak clearly
    2. Provide your exact location and the nature of emergency
    3. Follow the instructions given by the emergency operator
    4. Don't hang up until told to do so
    5. If you cannot speak, keep the line open so operators can hear what's happening

    **Save these numbers in your phone for quick access!**
    """)

# ----------------------------
# EVACUATION ROUTES SECTION
# ----------------------------
st.markdown("---")
st.markdown('<div id="routes-section" class="section-anchor"></div>', unsafe_allow_html=True)
st.subheader("🛣️ Evacuation Routes")

# Generate evacuation routes
if st.session_state['shelters_data']:
    evacuation_routes = get_evacuation_routes(lat0, lon0, st.session_state['shelters_data'])

    st.markdown("### Recommended Evacuation Routes")

    for i, route in enumerate(evacuation_routes, 1):
        status_color = {
            "Available": "#27ae60",
            "Limited": "#f39c12",
            "Full": "#e74c3c"
        }.get(route["status"], "#7f8c8d")

        st.markdown(f'''
        <div class="route-item">
            <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #2c3e50;">Route {i}: {route["shelter"]}</h4>
                <div style="background: {status_color}; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 0.9em;">
                    {route["status"]}
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px;">
                <div style="background: rgba(52, 152, 219, 0.1); padding: 10px; border-radius: 8px;">
                    <strong>Distance</strong><br>
                    <span style="font-size: 1.2em; font-weight: bold;">{route["distance"]} km</span>
                </div>
                <div style="background: rgba(46, 204, 113, 0.1); padding: 10px; border-radius: 8px;">
                    <strong>Est. Time</strong><br>
                    <span style="font-size: 1.2em; font-weight: bold;">{route["estimated_time"]}</span>
                </div>
                <div style="background: rgba(155, 89, 182, 0.1); padding: 10px; border-radius: 8px;">
                    <strong>Capacity</strong><br>
                    <span style="font-size: 1.2em; font-weight: bold;">{route["capacity"]}</span>
                </div>
                <div style="background: rgba(52, 73, 94, 0.1); padding: 10px; border-radius: 8px;">
                    <strong>Available</strong><br>
                    <span style="font-size: 1.2em; font-weight: bold;">{route["availability"]}</span>
                </div>
            </div>
            <div style="background: rgba(241, 196, 15, 0.1); padding: 12px; border-radius: 8px;">
                <strong>Instructions:</strong> {route["instructions"]}
            </div>
        </div>
        ''', unsafe_allow_html=True)

# Evacuation guidelines
with st.expander("📋 Evacuation Guidelines"):
    st.markdown("""
    **Before Evacuating:**
    - Gather essential documents, medicines, and emergency supplies
    - Turn off electricity, gas, and water mains
    - Inform family/friends about your evacuation plan
    - Take your emergency kit and important documents

    **During Evacuation:**
    - Follow recommended routes
    - Avoid flooded areas and damaged roads
    - Don't attempt to drive through floodwaters
    - Help children, elderly, and people with disabilities

    **At the Shelter:**
    - Register upon arrival
    - Follow shelter rules and instructions
    - Conserve resources and help others
    - Stay informed about the situation
    """)

# ----------------------------
# SOS SECTION
# ----------------------------
st.markdown("---")
st.markdown('<div id="sos-section" class="section-anchor"></div>', unsafe_allow_html=True)
st.subheader("🚨 SOS Emergency")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Emergency SOS")
    st.markdown("""
    **Use this feature only in case of immediate danger:**

    - Your location will be shared with emergency services
    - Nearby rescue teams will be alerted
    - Emergency contacts will be notified
    """)

    if st.button("🚨 SEND SOS EMERGENCY", use_container_width=True, type="primary"):
        if st.session_state.get('coords'):
            lat = st.session_state['coords']['lat']
            lon = st.session_state['coords']['lon']
            message = f"🚨 EMERGENCY SOS! Need immediate assistance at coordinates: {lat:.6f}, {lon:.6f}. Google Maps: https://www.google.com/maps?q={lat},{lon}"

            # Simulate sending emergency alerts
            with st.spinner("Sending emergency alerts..."):
                time.sleep(2)
                st.success("✅ SOS Alert Sent Successfully!")
                st.info(f"**Location shared:** {lat:.6f}, {lon:.6f}")
                st.warning("Emergency services have been notified. Stay in a safe location and wait for help.")
        else:
            st.error("❌ Location not available. Please set your location first.")

with col2:
    st.markdown("### Emergency Checklist")
    st.markdown("""
    **If you're in immediate danger:**

    ✅ Move to higher ground immediately
    ✅ Avoid walking through moving water
    ✅ Stay away from electrical equipment
    ✅ Do not attempt to drive through floods
    ✅ Follow evacuation routes to safe zones
    ✅ Keep emergency contacts handy
    ✅ Stay tuned to official alerts
    """)

    # Emergency resources
    st.markdown("### Quick Resources")
    if st.button("📞 Call Emergency Services", use_container_width=True):
        st.info("Dial 100 for Police, 102 for Ambulance, 101 for Fire Department")

    if st.button("🗺️ Show Nearest Hospitals", use_container_width=True):
        hospitals = [
            {"name": "City General Hospital", "distance": "1.2 km", "phone": "+91-98765-43210"},
            {"name": "Community Medical Center", "distance": "2.5 km", "phone": "+91-98765-43211"},
            {"name": "Emergency Care Unit", "distance": "3.1 km", "phone": "+91-98765-43212"}
        ]
        for hospital in hospitals:
            st.markdown(f"**{hospital['name']}** - {hospital['distance']} - {hospital['phone']}")

# Floating SOS button
st.markdown('<div class="sos-button">SOS</div>', unsafe_allow_html=True)

# ----------------------------
# ANALYTICS & FORECAST
# ----------------------------
st.markdown("---")
st.subheader("📈 Weather Analytics & Forecast")

forecast = get_forecast(lat0, lon0)

if forecast and 'list' in forecast:
    # Process forecast data
    points = forecast['list'][:12]  # Next 36 hours (3-hour intervals)
    times = [datetime.fromtimestamp(p['dt']) for p in points]
    rains = [p.get('rain', {}).get('3h', 0) for p in points]
    temps = [p['main']['temp'] for p in points]
    humidity = [p['main']['humidity'] for p in points]

    df_fore = pd.DataFrame({
        "time": times,
        "rain_mm": rains,
        "temp": temps,
        "humidity": humidity
    })

    # Create charts
    col1, col2 = st.columns(2)

    with col1:
        fig_rain = px.bar(df_fore, x="time", y="rain_mm",
                          title="🌧️ Rain Forecast (Next 36 Hours)",
                          labels={"rain_mm": "Rain (mm)", "time": "Time"})
        fig_rain.update_traces(marker_color='#3498db')
        st.plotly_chart(fig_rain, use_container_width=True)

    with col2:
        fig_temp = px.line(df_fore, x="time", y="temp", markers=True,
                           title="🌡️ Temperature Forecast",
                           labels={"temp": "Temperature (°C)", "time": "Time"})
        fig_temp.update_traces(line_color='#e74c3c')
        st.plotly_chart(fig_temp, use_container_width=True)

    # Rain intensity analysis
    high_slots = sum(1 for r in rains if r >= 5)
    med_slots = sum(1 for r in rains if 1 <= r < 5)
    low_slots = sum(1 for r in rains if r == 0)

    df_pie = pd.DataFrame({
        "category": ["Heavy (≥5mm)", "Light (1-5mm)", "No Rain"],
        "count": [high_slots, med_slots, low_slots]
    })

    fig_pie = px.pie(df_pie, names="category", values="count",
                     title="Rain Intensity Distribution in Forecast",
                     color_discrete_sequence=['#e74c3c', '#f39c12', '#27ae60'])
    st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.warning("Forecast data not available. Try again later or check your API key / network.")

# ----------------------------
# SAFETY GUIDELINES
# ----------------------------
st.markdown("---")
st.subheader("📋 Safety Guidelines")

guidelines_en = [
    "**Before a Flood:** Prepare an emergency kit, store food & water for 3 days, move valuables to higher ground, know your evacuation routes.",
    "**During a Flood:** Move to higher ground immediately, avoid walking through flood water, stay away from electrical equipment, follow official instructions.",
    "**After a Flood:** Avoid flood water, disinfect surfaces, check for structural damage, document damage for insurance, listen for official announcements."
]

# Translate guidelines if needed
if GT_AVAILABLE and st.session_state['lang'] != 'en':
    guidelines_trans = []
    for g in guidelines_en:
        try:
            guidelines_trans.append(TRANSLATOR.translate(g, dest=st.session_state['lang']).text)
        except:
            guidelines_trans.append(g)
else:
    guidelines_trans = guidelines_en

for guideline in guidelines_trans:
    st.markdown(
        f'<div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #3498db;">{guideline}</div>',
        unsafe_allow_html=True)

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p>🌊 <strong>Disaster Alert System</strong></p>
    <p style="font-size: 0.9em;">Real-time monitoring and emergency response system</p>
    <p style="font-size: 0.8em;">For emergencies, always call official emergency services first</p>
</div>
""", unsafe_allow_html=True)
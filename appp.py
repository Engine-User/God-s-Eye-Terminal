import streamlit as st
import streamlit_authenticator as stauth
import json
import requests
import random
import math
import yfinance as yf
import io
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from datetime import datetime, timezone, timedelta

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="God's Eye",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session State Defaults ───────────────────────────────────────────────────
FILTER_DEFAULTS = {
    "show_seismic": True,
    "show_weather": False,
    "show_satellites": True,
    "show_flights": True,
    "show_shipping": False,
    "show_cyber": True,
    "show_emergencies": True,
    "show_conflicts": True,
    "show_fires": True,
    "show_volcanoes": True,
    "show_disasters": True,
    "show_population": False,
}
for k, v in FILTER_DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

:root {
    --cyan: #00f0ff;
    --neon-blue: #0080ff;
    --neon-green: #00ff88;
    --neon-orange: #ff6600;
    --neon-red: #ff3355;
    --neon-purple: #bf00ff;
    --neon-yellow: #ffee00;
    --bg-dark: #000000;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    background: radial-gradient(ellipse at 50% 50%, #020c1b 0%, #000000 70%) !important;
    color: #e0f7ff;
    font-family: 'Rajdhani', sans-serif;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
}

.block-container {
    padding: 0.15rem 0.5rem 0.3rem !important;
    max-width: 100% !important;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,240,255,0.3); border-radius: 2px; }

/* ── Login Form ── */
[data-testid="stForm"] {
    background: linear-gradient(145deg, rgba(2,15,35,0.95), rgba(0,5,15,0.98));
    border: 1px solid rgba(0,240,255,0.25);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    box-shadow: 0 0 60px rgba(0,240,255,0.08), inset 0 1px 0 rgba(0,240,255,0.1);
    max-width: 440px;
    margin: 4vh auto 0;
    backdrop-filter: blur(20px);
}
input[type="text"], input[type="password"] {
    background: rgba(0,10,25,0.8) !important;
    border: 1px solid rgba(0,240,255,0.3) !important;
    color: #e0f7ff !important;
    border-radius: 10px !important;
    letter-spacing: 1px !important;
}
input[type="text"]:focus, input[type="password"]:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 15px rgba(0,240,255,0.3) !important;
}
[data-testid="stFormSubmitButton"] > button,
.stButton > button {
    background: linear-gradient(135deg, rgba(0,240,255,0.15), rgba(0,128,255,0.2)) !important;
    border: 1px solid var(--cyan) !important;
    color: var(--cyan) !important;
    border-radius: 10px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    transition: all 0.3s ease !important;
}
[data-testid="stFormSubmitButton"] > button:hover,
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,240,255,0.3), rgba(0,128,255,0.4)) !important;
    box-shadow: 0 0 30px rgba(0,240,255,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Panel Card (Unified for both sides) ── */
.panel-card {
    background: linear-gradient(145deg, rgba(0,25,60,0.45), rgba(0,12,35,0.65));
    border: 1px solid rgba(0,240,255,0.1);
    border-radius: 12px;
    padding: 10px 12px;
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(0,240,255,0.08), inset 0 -1px 0 rgba(0,0,0,0.2);
    margin-bottom: 5px;
    transition: all 0.35s cubic-bezier(0.25,0.8,0.25,1);
    position: relative;
    overflow: hidden;
}
.panel-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,240,255,0.2), transparent);
}
.panel-card:hover {
    border-color: rgba(0,240,255,0.25);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 20px rgba(0,240,255,0.08), inset 0 1px 0 rgba(0,240,255,0.15);
}
.panel-card-red { border-left: 3px solid rgba(255,51,85,0.6); }
.panel-card-orange { border-left: 3px solid rgba(255,102,0,0.6); }
.panel-card-green { border-left: 3px solid rgba(0,255,136,0.6); }
.panel-card-cyan { border-left: 3px solid rgba(0,240,255,0.6); }
.panel-card-purple { border-left: 3px solid rgba(191,0,255,0.6); }
.panel-card-yellow { border-left: 3px solid rgba(255,238,0,0.6); }

/* ── Panel Titles ── */
.panel-title {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.6rem;
    font-weight: 700;
    color: var(--cyan);
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
    padding-bottom: 5px;
    border-bottom: 1px solid rgba(0,240,255,0.08);
    text-shadow: 0 0 10px rgba(0,240,255,0.3);
}

/* ── Native Checkbox Wrapper (Matches glass-tile) ── */
div.element-container:has(> .stCheckbox),
div.stCheckbox {
    width: 100% !important;
    display: block !important;
}
.stCheckbox > label,
div[data-testid="stCheckbox"] > label {
    display: flex !important;
    width: 100% !important;
}
div[data-baseweb="checkbox"] {
    display: flex !important;
    width: 100% !important;
}
[data-testid="stCheckbox"] {
    background: linear-gradient(145deg, rgba(0,20,50,0.5), rgba(0,8,25,0.7));
    border: 1px solid rgba(0,240,255,0.06);
    border-radius: 8px;
    padding: 6px 8px;
    margin-bottom: 4px;
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    width: 100% !important;
    display: flex !important;
    align-items: center;
    box-sizing: border-box;
}
[data-testid="stCheckbox"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,240,255,0.1), transparent);
}
[data-testid="stCheckbox"]:hover {
    border-color: rgba(0,240,255,0.2);
    box-shadow: 0 2px 15px rgba(0,240,255,0.08);
    transform: translateX(2px);
}

/* Style the checkmark box to be neon green when checked */
[data-testid="stCheckbox"] input[type="checkbox"]:checked + div:not([data-testid="stMarkdownContainer"]):not(:has(p)),
[data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] {
    background-color: var(--neon-green) !important;
    border-color: var(--neon-green) !important;
    box-shadow: 0 0 10px rgba(0,255,136,0.6) !important;
}
[data-testid="stCheckbox"] input[type="checkbox"]:checked + div:not([data-testid="stMarkdownContainer"]):not(:has(p)) svg,
[data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] svg {
    color: #000 !important;
    fill: #000 !important;
    stroke: #000 !important;
}

/* Font inside checkbox */
[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    display: flex;
    align-items: center;
    background: transparent !important;
    box-shadow: none !important;
    border-color: transparent !important;
}
[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] p {
    color: rgba(0,240,255,0.85) !important;
    font-size: 0.6rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.2px !important;
    font-family: 'Share Tech Mono', monospace !important;
    width: 100% !important;
    margin-bottom: 0 !important;
}

/* ── Intel Items (Right Panel - matching style) ── */
.intel-item {
    background: linear-gradient(145deg, rgba(0,20,50,0.5), rgba(0,8,25,0.7));
    border: 1px solid rgba(0,240,255,0.06);
    border-radius: 8px;
    padding: 5px 8px;
    margin-bottom: 4px;
    font-size: 0.58rem;
    letter-spacing: 0.2px;
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.intel-item::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,240,255,0.1), transparent);
}
.intel-item:hover {
    border-color: rgba(0,240,255,0.2);
    box-shadow: 0 2px 15px rgba(0,240,255,0.08);
    transform: translateX(2px);
}

/* ── Status Bar ── */
.status-bar {
    background: linear-gradient(90deg, rgba(0,240,255,0.02), rgba(0,240,255,0.06), rgba(0,240,255,0.02));
    border: 1px solid rgba(0,240,255,0.1);
    border-radius: 10px;
    padding: 5px 14px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 4px;
    backdrop-filter: blur(15px);
}
.status-item {
    display: flex; align-items: center; gap: 4px;
    font-size: 0.6rem; letter-spacing: 0.8px;
    color: rgba(0,240,255,0.65);
}
.status-label { color: rgba(0,240,255,0.3); }
.status-value { color: var(--cyan); font-weight: 600; }
.status-dot {
    width: 5px; height: 5px; border-radius: 50%;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%,100% { opacity:0.4; } 50% { opacity:1; box-shadow: 0 0 6px currentColor; }
}

/* ── Header ── */
.cmd-header { text-align: center; padding: 2px 0 1px; }
.cmd-header h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.1rem; font-weight: 800;
    color: var(--cyan); letter-spacing: 5px;
    text-shadow: 0 0 25px rgba(0,240,255,0.5), 0 0 50px rgba(0,240,255,0.2);
    margin: 0; text-transform: uppercase;
}
.cmd-header .subtitle {
    color: rgba(0,240,255,0.25); font-size: 0.55rem;
    letter-spacing: 2.5px; margin-top: 0px;
}

/* ── Stats Bar ── */
.stats-bar {
    background: linear-gradient(90deg, rgba(0,240,255,0.01), rgba(0,240,255,0.05), rgba(0,240,255,0.01));
    border: 1px solid rgba(0,240,255,0.08);
    border-radius: 10px;
    padding: 5px 12px;
    margin-top: 4px;
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 1px;
    backdrop-filter: blur(10px);
}
.stat-item { text-align: center; padding: 2px 6px; }
.stat-value {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.8rem; font-weight: 700;
    letter-spacing: 1px;
    text-shadow: 0 0 10px currentColor;
}
.stat-label {
    font-size: 0.48rem;
    color: rgba(0,240,255,0.3);
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

[data-testid="stHorizontalBlock"] { gap: 0.3rem !important; }

div[data-testid="stVerticalBlock"] > div:has(> .element-container:empty) { display: none; }
iframe { border: none !important; display: block; }

/* ── Login Splash ── */
.login-splash { text-align: center; margin-top: 4vh; margin-bottom: 2vh; }
.login-splash h2 {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 2rem; font-weight: 900;
    color: var(--cyan); letter-spacing: 8px;
    text-shadow: 0 0 40px rgba(0,240,255,0.6), 0 0 80px rgba(0,240,255,0.3);
    margin-bottom: 8px;
}
.login-splash p {
    color: rgba(0,240,255,0.3); font-size: 0.75rem; letter-spacing: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
MAJOR_CITIES = [
    ("New York", 40.7128, -74.0060), ("London", 51.5074, -0.1278),
    ("Tokyo", 35.6762, 139.6503), ("Paris", 48.8566, 2.3522),
    ("Sydney", -33.8688, 151.2093), ("Moscow", 55.7558, 37.6176),
    ("Dubai", 25.2048, 55.2708), ("Singapore", 1.3521, 103.8198),
    ("Mumbai", 19.0760, 72.8777), ("São Paulo", -23.5505, -46.6333),
    ("Cairo", 30.0444, 31.2357), ("Beijing", 39.9042, 116.4074),
    ("Seoul", 37.5665, 126.9780), ("Mexico City", 19.4326, -99.1332),
    ("Lagos", 6.5244, 3.3792), ("Istanbul", 41.0082, 28.9784),
    ("Buenos Aires", -34.6037, -58.3816), ("Johannesburg", -26.2041, 28.0473),
    ("Bangkok", 13.7563, 100.5018), ("Jakarta", -6.2088, 106.8456),
    ("Lima", -12.0464, -77.0428), ("Berlin", 52.5200, 13.4050),
    ("Madrid", 40.4168, -3.7038), ("Rome", 41.9028, 12.4964),
    ("Nairobi", -1.2921, 36.8219), ("Riyadh", 24.7136, 46.6753),
    ("Tehran", 35.6892, 51.3890), ("Karachi", 24.8607, 67.0011),
    ("Dhaka", 23.8103, 90.4125), ("Manila", 14.5995, 120.9842),
    ("Bogotá", 4.7110, -74.0721), ("Santiago", -33.4489, -70.6693),
    ("Kuala Lumpur", 3.1390, 101.6869), ("Hanoi", 21.0285, 105.8542),
    ("Ankara", 39.9334, 32.8597), ("Warsaw", 52.2297, 21.0122),
    ("Kyiv", 50.4501, 30.5234), ("Addis Ababa", 9.0250, 38.7469),
    ("Casablanca", 33.5731, -7.5898), ("Athens", 37.9838, 23.7275),
    ("Oslo", 59.9139, 10.7522), ("Stockholm", 59.3293, 18.0686),
    ("Helsinki", 60.1699, 24.9384), ("Lisbon", 38.7223, -9.1393),
    ("Vienna", 48.2082, 16.3738), ("Zurich", 47.3769, 8.5417),
    ("Dublin", 53.3498, -6.2603), ("Copenhagen", 55.6761, 12.5683),
    ("Prague", 50.0755, 14.4378), ("Havana", 23.1136, -82.3666),
]

FLIGHT_ROUTES = [
    (40.6413,-73.7781,51.4700,-0.4543,"JFK-LHR"),
    (33.9425,-118.4081,35.5494,139.7798,"LAX-NRT"),
    (25.2532,55.3657,1.3644,103.9915,"DXB-SIN"),
    (51.4700,-0.4543,25.2532,55.3657,"LHR-DXB"),
    (22.3080,113.9185,37.4602,126.4407,"HKG-ICN"),
    (48.1103,11.5528,40.0801,116.5844,"MUC-PEK"),
    (-33.9461,151.1772,1.3644,103.9915,"SYD-SIN"),
    (40.6413,-73.7781,48.8566,2.3522,"JFK-CDG"),
    (51.4700,-0.4543,40.6413,-73.7781,"LHR-JFK"),
    (35.6762,139.6503,-33.8688,151.2093,"TYO-SYD"),
    (39.9042,116.4074,33.9425,-118.4081,"PEK-LAX"),
    (-23.5505,-46.6333,40.6413,-73.7781,"GRU-JFK"),
    (55.7558,37.6176,25.2532,55.3657,"SVO-DXB"),
    (19.0760,72.8777,51.4700,-0.4543,"BOM-LHR"),
    (28.5383,77.3897,25.2532,55.3657,"DEL-DXB"),
    (-26.2041,28.0473,51.4700,-0.4543,"JNB-LHR"),
    (1.3644,103.9915,51.4700,-0.4543,"SIN-LHR"),
    (41.0082,28.9784,40.6413,-73.7781,"IST-JFK"),
    (50.0379,8.5622,48.8566,2.3522,"FRA-CDG"),
    (14.5995,120.9842,33.9425,-118.4081,"MNL-LAX"),
    (52.3676,4.9041,-34.6037,-58.3816,"AMS-EZE"),
    (25.7617,-80.1918,4.7110,-74.0721,"MIA-BOG"),
    (37.5665,126.9780,49.2827,-123.1207,"ICN-YVR"),
    (-12.0464,-77.0428,25.7617,-80.1918,"LIM-MIA"),
    (35.3980,139.7714,1.3644,103.9915,"HND-SIN"),
    (41.9028,12.4964,40.6413,-73.7781,"FCO-JFK"),
    (-1.2921,36.8219,25.2532,55.3657,"NBO-DXB"),
    (9.0250,38.7469,25.2532,55.3657,"ADD-DXB"),
    (13.7563,100.5018,51.4700,-0.4543,"BKK-LHR"),
    (6.5244,3.3792,51.4700,-0.4543,"LOS-LHR"),
]

SHIPPING_ROUTES = [
    (31.2304,121.4737,51.9244,4.4777,"Shanghai-Rotterdam"),
    (1.3521,103.8198,30.0444,31.2357,"Singapore-Suez"),
    (22.3080,113.9185,33.7490,-118.2426,"HK-LA"),
    (35.4437,139.6380,47.6062,-122.3321,"Yokohama-Seattle"),
    (22.3080,113.9185,1.3521,103.8198,"HK-Singapore"),
    (25.2048,55.2708,19.0760,72.8777,"Dubai-Mumbai"),
    (51.9244,4.4777,40.6413,-73.7781,"Rotterdam-NY"),
    (1.3521,103.8198,-33.8688,151.2093,"Singapore-Sydney"),
    (-23.5505,-46.6333,6.5244,3.3792,"Santos-Lagos"),
    (30.0444,31.2357,19.0760,72.8777,"Suez-Mumbai"),
    (1.2983,103.7775,22.5726,114.2088,"Singapore-Shenzhen"),
    (9.3499,-79.9070,33.7490,-118.2426,"Panama-LA"),
    (35.4437,139.6380,-33.8688,151.2093,"Yokohama-Sydney"),
    (51.9244,4.4777,30.0444,31.2357,"Rotterdam-Suez"),
    (-1.2921,36.8219,19.0760,72.8777,"Nairobi-Mumbai"),
    (40.6413,-73.7781,-34.6037,-58.3816,"NY-Buenos Aires"),
    (25.2048,55.2708,-26.2041,28.0473,"Dubai-Johannesburg"),
    (53.5488,9.9872,31.2304,121.4737,"Hamburg-Shanghai"),
    (34.0522,-118.2437,-12.0464,-77.0428,"LA-Lima"),
    (-37.8136,144.9631,25.2048,55.2708,"Melbourne-Dubai"),
]

EMERGENCY_ZONES = [
    {"lat":33.3152,"lng":44.3661,"name":"Baghdad - Conflict Zone","severity":"high"},
    {"lat":15.3694,"lng":44.1910,"name":"Yemen - Humanitarian Crisis","severity":"high"},
    {"lat":36.2021,"lng":36.1605,"name":"Syria - NW Conflict","severity":"high"},
    {"lat":48.3794,"lng":31.1656,"name":"Ukraine - Conflict","severity":"high"},
    {"lat":31.7683,"lng":35.2137,"name":"Israel-Palestine","severity":"high"},
    {"lat":34.0522,"lng":43.1590,"name":"Iraq - Western Instability","severity":"medium"},
    {"lat":12.8628,"lng":30.2176,"name":"Sudan - Conflict","severity":"high"},
    {"lat":2.0469,"lng":45.3182,"name":"Somalia - Instability","severity":"high"},
    {"lat":19.7633,"lng":96.0785,"name":"Myanmar - Civil Conflict","severity":"high"},
    {"lat":14.6928,"lng":-17.4467,"name":"Sahel - Regional Instability","severity":"medium"},
    {"lat":4.5353,"lng":11.4850,"name":"Cameroon - Regional Crisis","severity":"medium"},
    {"lat":18.5204,"lng":-72.3314,"name":"Haiti - Gang Violence & Crisis","severity":"high"},
    {"lat":6.5244,"lng":3.3792,"name":"Nigeria - Security Incidents","severity":"medium"},
    {"lat":34.5553,"lng":69.2075,"name":"Afghanistan - Humanitarian Need","severity":"high"},
    {"lat":14.0583,"lng":108.2772,"name":"South China Sea - Tensions","severity":"medium"},
    {"lat":5.1521,"lng":46.1996,"name":"Horn of Africa - Piracy Risk","severity":"medium"},
    {"lat":51.5,"lng":30.0,"name":"Eastern Europe - Security Posture","severity":"medium"},
    {"lat":7.3697,"lng":12.3547,"name":"Central African Republic - Crisis","severity":"high"},
    {"lat":-4.4419,"lng":15.2663,"name":"DRC - Eastern Conflict","severity":"high"},
    {"lat":10.4806,"lng":-66.9036,"name":"Venezuela - Instability","severity":"medium"},
    {"lat":43.3283,"lng":42.2708,"name":"Caucasus - Tensions","severity":"medium"},
    {"lat":33.8547,"lng":35.8623,"name":"Lebanon - Economic Crisis","severity":"high"},
    {"lat":11.8251,"lng":42.5903,"name":"Djibouti - Critical Chokepoint","severity":"medium"},
    {"lat":23.6345,"lng":-102.5528,"name":"Mexico - Cartel Zones","severity":"medium"},
    {"lat":42.0000,"lng":133.0000,"name":"Sea of Japan - Tensions","severity":"high"},
]

# ── Data Fetching Functions ──────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_financials():
    """Fetch live financial data from Yahoo Finance"""
    symbols = {
        "NASDAQ": "^IXIC",
        "DOW JONES": "^DJI",
        "LSE (UK)": "^FTSE",
        "CRUDE OIL": "CL=F",
        "GOLD": "GC=F",
        "NSE (INDIA)": "^NSEI",
        "SSE (CHINA)": "000001.SS"
    }
    data = []
    for name, sym in symbols.items():
        try:
            hist = yf.Ticker(sym).history(period="5d")
            if not hist.empty and len(hist) >= 2:
                last = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                diff = last - prev
                pct = (diff / prev) * 100
                data.append({"name": name, "price": last, "change": diff, "pct": pct})
            elif not hist.empty and len(hist) == 1:
                last = float(hist['Close'].iloc[-1])
                data.append({"name": name, "price": last, "change": 0.0, "pct": 0.0})
        except Exception:
            pass
    return data

@st.cache_data(ttl=300)
def fetch_global_news():
    """Fetch live global news from RSS and parse tags"""
    try:
        url = "http://feeds.bbci.co.uk/news/world/rss.xml"
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.text)
        
        news_items = []
        bad_kws = ["dead", "kill", "attack", "strike", "war", "crash", "casualt", "conflict", "bomb", "invade", "invasion", "missile", "terror"]
        good_kws = ["peace", "breakthrough", "recover", "grow", "truce", "rescue", "deal", "agreement", "success", "cure"]
        black_swan_kws = ["pandemic", "unprecedented", "massive scale", "global crisis", "shock", "collapse", "outbreak"]
        
        # Simple country list for location tag
        countries = ["Israel", "Lebanon", "Russia", "Ukraine", "USA", "China", "Iran", "Taiwan", "Gaza", "UK", "France", "Germany", "Yemen", "Syria"]
        
        for item in root.findall('.//item'):
            if len(news_items) >= 7:
                break
            title_elem = item.find('title')
            title = title_elem.text if title_elem is not None and title_elem.text else ""
            desc_elem = item.find('description')
            desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
            
            text_to_check = (title + " " + desc).lower()
            
            locs = [c for c in countries if c.lower() in text_to_check]
            loc_tag = locs[0] if locs else "GLOBAL"
            if loc_tag.lower() == "us": loc_tag = "USA"
            
            tag = "NEUTRAL UPDATE"
            color = "#00f0ff" # cyan
            
            if any(k in text_to_check for k in black_swan_kws):
                tag = "BLACK SWAN Event"
                color = "#bf00ff" # purple
            elif any(k in text_to_check for k in bad_kws):
                tag = "CRITICAL"
                color = "#ff3355" # red
            elif "warn" in text_to_check or "tension" in text_to_check or "threat" in text_to_check:
                tag = "HIGH TENSION"
                color = "#ff6600" # orange
            elif any(k in text_to_check for k in good_kws):
                tag = "POSITIVE"
                color = "#00ff88" # green
            
            news_items.append({
                "title": title,
                "location": loc_tag.upper(),
                "tag": tag,
                "color": color
            })
            
        return news_items
    except Exception as e:
        print("News Error:", e)
        return []

@st.cache_data(ttl=180)
def fetch_gdelt_events():
    """Fetch live GDELT events with tone/conflict data"""
    try:
        master = requests.get("http://data.gdeltproject.org/gdeltv2/masterfilelist.txt", timeout=30).text
        latest_files = [line.split()[-1] for line in master.splitlines() if '.export.CSV.zip' in line]
        if not latest_files:
            return []
        latest = latest_files[-1]
        r = requests.get(latest, timeout=60)
        events = []
        with ZipFile(io.BytesIO(r.content)) as z:
            for name in z.namelist()[:1]:
                with z.open(name) as f:
                    for i, line in enumerate(f):
                        if i > 5000:
                            break
                        try:
                            cols = line.decode('utf-8', errors='ignore').strip().split('\t')
                            if len(cols) < 58:
                                continue
                            lat = cols[48] if len(cols) > 48 else None
                            lon = cols[49] if len(cols) > 49 else None
                            if lat and lon:
                                try:
                                    lat_f = float(lat)
                                    lon_f = float(lon)
                                    if -90 <= lat_f <= 90 and -180 <= lon_f <= 180:
                                        tone = float(cols[34]) if cols[34] else 0
                                        mentions = int(cols[56]) if len(cols) > 56 and cols[56] else 1
                                        actor1 = cols[6][:30] if len(cols) > 6 and cols[6] else "Unknown"
                                        actor2 = cols[7][:30] if len(cols) > 7 and cols[7] else "Unknown"
                                        event_code = cols[26] if len(cols) > 26 else "000"
                                        
                                        if tone < -2:
                                            color = "#ff0033"
                                        elif tone < 0:
                                            color = "#ff6600"
                                        elif tone < 2:
                                            color = "#ffcc00"
                                        else:
                                            color = "#00ff66"
                                        
                                        events.append({
                                            "lat": lat_f,
                                            "lng": lon_f,
                                            "tone": tone,
                                            "mentions": mentions,
                                            "actor1": actor1,
                                            "actor2": actor2,
                                            "event_code": event_code,
                                            "color": color,
                                        })
                                except:
                                    pass
                        except:
                            continue
        return events[:150]
    except Exception as e:
        return []

@st.cache_data(ttl=300)
def fetch_acled_data():
    """Fetch ACLED conflict data - simulated with real regions"""
    # ACLED API requires registration, using curated high-conflict zones
    acled_zones = [
        {"lat": 48.3794, "lng": 31.1656, "name": "Ukraine - Active Conflict", "fatalities": 127, "type": "Battles", "color": "#ff0000"},
        {"lat": 33.3152, "lng": 44.3661, "name": "Iraq - Security Events", "fatalities": 23, "type": "Violence against civilians", "color": "#ff2200"},
        {"lat": 34.5553, "lng": 69.2075, "name": "Afghanistan - Conflict", "fatalities": 45, "type": "Armed Clash", "color": "#ff0033"},
        {"lat": 12.8628, "lng": 30.2176, "name": "Sudan - Civil War", "fatalities": 89, "type": "Battles", "color": "#ff0000"},
        #{"lat": 19.7633, "lng": 96.0785, "name": "Myanmar - Civil War", "fatalities": 67, "type": "Armed Clash", "color": "#ff2200"},
        {"lat": 15.3694, "lng": 44.1910, "name": "Yemen - War Zone", "fatalities": 34, "type": "Airstrike", "color": "#ff0033"},
        {"lat": 36.2021, "lng": 36.1610, "name": "Syria - NW Instability", "fatalities": 12, "type": "Battles", "color": "#ff4400"},
        #{"lat": -4.4419, "lng": 15.2663, "name": "DRC - Eastern Conflict", "fatalities": 56, "type": "Violence", "color": "#ff2200"},
        #{"lat": 7.3697, "lng": 12.3547, "name": "CAR - Crisis", "fatalities": 28, "type": "Battles", "color": "#ff4400"},
        #{"lat": 2.0469, "lng": 45.3182, "name": "Somalia - Al-Shabaab", "fatalities": 19, "type": "Attacks", "color": "#ff3300"},
        {"lat": 18.5204, "lng": -72.3314, "name": "Haiti - Gang Violence", "fatalities": 234, "type": "Violence", "color": "#ff0000"},
        {"lat": 10.4806, "lng": -66.9036, "name": "Venezuela - Unrest", "fatalities": 8, "type": "Protests", "color": "#ff5500"},
        {"lat": 23.6345, "lng": -102.5528, "name": "Mexico - Cartel Activity", "fatalities": 156, "type": "Violence", "color": "#ff2200"},
        {"lat": 14.0583, "lng": 108.2772, "name": "South China Sea - Tensions", "fatalities": 0, "type": "Maritime", "color": "#ff6600"},
        {"lat": 31.7683, "lng": 35.2137, "name": "Israel-Palestine", "fatalities": 78, "type": "Conflict", "color": "#ff0000"},
        {"lat": 33.8547, "lng": 35.8623, "name": "Lebanon - Crisis", "fatalities": 5, "type": "Conflict", "color": "#ff4400"},
    ]
    return acled_zones

@st.cache_data(ttl=600)
def fetch_ucdp_conflicts():
    """Fetch UCDP organized conflict data"""
    ucdp_data = [
        {"lat": 48.3794, "lng": 31.1656, "name": "Russia-Ukraine War", "intensity": "high", "type": "Internationalized Internal"},
        {"lat": 34.5553, "lng": 69.2075, "name": "Afghanistan Conflict", "intensity": "high", "type": "Non-State"},
        {"lat": 15.3694, "lng": 44.1910, "name": "Yemen Civil War", "intensity": "high", "type": "Internationalized Internal"},
        {"lat": 12.8628, "lng": 30.2176, "name": "Sudan RSF-FSAF War", "intensity": "high", "type": "Internal"},
        {"lat": 19.7633, "lng": 96.0785, "name": "Myanmar Civil War", "intensity": "high", "type": "Internal"},
        #{"lat": -4.4419, "lng": 15.2663, "name": "DRC M23 Rebellion", "intensity": "medium", "type": "Non-State"},
        {"lat": 33.3152, "lng": 44.3661, "name": "Iraq Insurgency", "intensity": "medium", "type": "Non-State"},
        #{"lat": 7.3697, "lng": 12.3547, "name": "CAR Conflict", "intensity": "medium", "type": "Non-State"},
        #{"lat": 9.3499, "lng": 42.5903, "name": "Ethiopia-Tigray", "intensity": "medium", "type": "Internal"},
    ]
    return ucdp_data

@st.cache_data(ttl=600)
def fetch_volcanoes():
    """Fetch active volcanoes from USGS"""
    try:
        url = "https://volcanoes.usgs.gov/hvp/earthquake_interactive_maps/volcanoes.json"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            volcanoes = []
            for v in data.get('features', [])[:60]:
                props = v.get('properties', {})
                geom = v.get('geometry', {})
                if geom.get('type') == 'Point':
                    coords = geom['coordinates']
                    volcanoes.append({
                        "lat": coords[1],
                        "lng": coords[0],
                        "name": props.get('name', 'Unknown Volcano'),
                        "status": props.get('activity', 'Normal'),
                        "color": "#ff4400" if 'eruption' in str(props.get('activity', '')).lower() else "#ff8800",
                    })
            return volcanoes
    except:
        pass
    
    # Fallback curated volcano data
    return [
        {"lat": 64.2491, "lng": -19.5145, "name": "Iceland - Fagradalsfjall", "status": "Erupting", "color": "#ff0000"},
        {"lat": 19.4062, "lng": -155.2834, "name": "Hawaii - Kilauea", "status": "Erupting", "color": "#ff0000"},
        {"lat": -0.3488, "lng": -78.5808, "name": "Ecuador - Cotopaxi", "status": "Restless", "color": "#ff6600"},
        {"lat": 35.2925, "lng": 138.7273, "name": "Japan - Mt Fuji", "status": "Normal", "color": "#ff8800"},
        {"lat": 37.7295, "lng": 38.5006, "name": "Turkey - Mt Hasan", "status": "Active", "color": "#ff5500"},
        {"lat": 13.2571, "lng": 41.5883, "name": "Ethiopia - Erta Ale", "status": "Erupting", "color": "#ff0000"},
        {"lat": 11.4125, "lng": 162.2361, "name": "Marshall Islands - KB", "status": "Active", "color": "#ff6600"},
        {"lat": -6.1639, "lng": 155.1983, "name": "Papua New Guinea - Bagana", "status": "Erupting", "color": "#ff0000"},
        {"lat": 37.47, "lng": -113.78, "name": "USA - Kilauea", "status": "Erupting", "color": "#ff0000"},
        {"lat": 38.7833, "lng": -27.3167, "name": "Azores - São Miguel", "status": "Active", "color": "#ff6600"},
        {"lat": 14.27, "lng": 120.98, "name": "Philippines - Taal", "status": "Alert", "color": "#ff4400"},
        {"lat": 13.3231, "lng": 123.6200, "name": "Philippines - Mayon", "status": "Alert", "color": "#ff4400"},
        {"lat": 6.15, "lng": 124.23, "name": "Philippines - Matutum", "status": "Active", "color": "#ff6600"},
        {"lat": -8.4095, "lng": 115.5089, "name": "Indonesia - Agung", "status": "Active", "color": "#ff6600"},
        {"lat": -0.27, "lng": 100.473, "name": "Indonesia - Marapi", "status": "Erupting", "color": "#ff0000"},
        {"lat": 37.293, "lng": -113.027, "name": "USA - St Helens", "status": "Active", "color": "#ff6600"},
        {"lat": 60.0233, "lng": 152.8894, "name": "Alaska - Redoubt", "status": "Restless", "color": "#ff8800"},
        {"lat": 46.1914, "lng": 122.0883, "name": "Russia - Bezymianny", "status": "Erupting", "color": "#ff0000"},
        {"lat": 58.54, "lng": 161.36, "name": "Russia - Shiveluch", "status": "Erupting", "color": "#ff0000"},
    ]

@st.cache_data(ttl=300)
def fetch_fires():
    """Fetch active fire hotspots from NASA FIRMS"""
    try:
        # Using EONET fires as primary source
        eonet = requests.get("https://eonet.gsfc.nasa.gov/api/v3/events?category=wildfires&status=open", timeout=15).json()
        fires = []
        for ev in eonet.get('events', [])[:50]:
            for geom in ev.get('geometry', []):
                if geom.get('type') == 'Point':
                    coords = geom['coordinates']
                    fires.append({
                        "lat": coords[1],
                        "lng": coords[0],
                        "name": ev.get('title', 'Wildfire'),
                        "date": geom.get('date', '')[:10],
                        "color": "#ff2200",
                    })
        return fires
    except:
        pass
    
    # Curated fire data
    return [
        {"lat": 38.4088, "lng": -122.4124, "name": "California - Napa Fire", "date": "2024-01-15", "color": "#ff0000"},
        {"lat": -33.8688, "lng": 151.2093, "name": "Australia - NSW Fires", "date": "2024-01-14", "color": "#ff2200"},
        {"lat": 37.0902, "lng": -95.7129, "name": "USA - Texas Panhandle", "date": "2024-01-13", "color": "#ff1100"},
        {"lat": -15.7833, "lng": -47.8667, "name": "Brazil - Amazon Fires", "date": "2024-01-12", "color": "#ff2200"},
        {"lat": 51.1784, "lng": -115.5708, "name": "Canada - Alberta Fires", "date": "2024-01-14", "color": "#ff0000"},
        {"lat": 36.2071, "lng": 138.7306, "name": "Japan - Nagano Fire", "date": "2024-01-11", "color": "#ff3300"},
        {"lat": 56.4774, "lng": -132.3563, "name": "Alaska - Southeast Fires", "date": "2024-01-13", "color": "#ff1100"},
        {"lat": -35.2809, "lng": 149.1300, "name": "Australia - Victoria", "date": "2024-01-12", "color": "#ff2200"},
        {"lat": 39.0111, "lng": -9.1393, "name": "Portugal - Lisbon Area", "date": "2024-01-10", "color": "#ff3300"},
        {"lat": 41.3851, "lng": 2.1734, "name": "Spain - Catalonia", "date": "2024-01-09", "color": "#ff2200"},
    ]

@st.cache_data(ttl=600)
def fetch_nasa_disasters():
    """Fetch NASA EONET natural disasters"""
    try:
        url = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=100"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        disasters = []
        category_colors = {
            "wildfires": "#ff2200",
            "volcanoes": "#ff6600",
            "seaLakeIce": "#00ccff",
            "severeStorms": "#ffcc00",
            "floods": "#0066ff",
            "earthquakes": "#ff1133",
            "landslides": "#8b4513",
            "tsunamis": "#0066ff",
            "snow": "#ffffff",
            "drought": "#cc9900",
            "tornado": "#ff8800",
        }
        for ev in data.get('events', []):
            cat = ev.get('categories', [{}])[0].get('id', 'default')
            for geom in ev.get('geometry', []):
                if geom.get('type') == 'Point':
                    coords = geom['coordinates']
                    color = category_colors.get(cat, "#ff6600")
                    disasters.append({
                        "lat": coords[1],
                        "lng": coords[0],
                        "name": ev.get('title', 'Event'),
                        "category": cat,
                        "date": geom.get('date', '')[:10],
                        "color": color,
                    })
        return disasters[:80]
    except:
        return []

@st.cache_data(ttl=300)
def fetch_severe_weather():
    """Fetch NOAA severe weather alerts"""
    try:
        url = "https://alerts.weather.gov/atom.php?zone=sea"
        # Using global significant weather instead
        return []
    except:
        return []

@st.cache_data(ttl=600)
def fetch_global_events():
    """Fetch all GDELT/ACLED/UCDP combined radar points"""
    points = []
    
    # GDELT Events
    gdelt_events = fetch_gdelt_events()
    for ev in gdelt_events:
        size = 0.1 + min(ev.get('mentions', 1) / 500, 0.4)
        points.append({
            "lat": ev["lat"],
            "lng": ev["lng"],
            "color": ev["color"],
            "size": size,
            "alt": 0.01,
            "type": "conflict",
            "label": f"{ev['actor1'][:25]} vs {ev['actor2'][:25]}",
            "detail": f"Tone: {ev['tone']:.1f} | Mentions: {ev['mentions']}",
            "category": "gdelt"
        })
    
    # ACLED Zones
    acled_data = fetch_acled_data()
    for zone in acled_data:
        points.append({
            "lat": zone["lat"],
            "lng": zone["lng"],
            "color": zone["color"],
            "size": 0.35 + min(zone.get('fatalities', 0) / 100, 0.4),
            "alt": 0.015,
            "type": "conflict",
            "label": zone["name"],
            "detail": f"Fatalities: {zone.get('fatalities', 0)} | Type: {zone.get('type', 'N/A')}",
            "category": "acled"
        })
    
    # UCDP Conflicts
    ucdp_data = fetch_ucdp_conflicts()
    for conflict in ucdp_data:
        color = "#ff0000" if conflict["intensity"] == "high" else "#ff6600"
        points.append({
            "lat": conflict["lat"],
            "lng": conflict["lng"],
            "color": color,
            "size": 0.4,
            "alt": 0.012,
            "type": "conflict",
            "label": conflict["name"],
            "detail": f"Type: {conflict['type']} | Intensity: {conflict['intensity']}",
            "category": "ucdp"
        })
    
    return points

@st.cache_data(ttl=600)
def fetch_ais_ships():
    """Fetch live ship positions (simulated from real shipping lanes)"""
    # Real AIS data requires subscription, using major shipping chokepoints
    ship_locations = [
        # Strait of Hormuz
        {"lat": 26.5, "lng": 56.5, "name": "Tanker - Strait of Hormuz", "type": "Tanker", "color": "#00ccdd"},
        {"lat": 26.8, "lng": 56.3, "name": "Cargo - Persian Gulf", "type": "Cargo", "color": "#00aacc"},
        {"lat": 26.3, "lng": 56.6, "name": "Tanker - Hormuz Transit", "type": "Tanker", "color": "#00ccdd"},
        # Strait of Malacca
        {"lat": 2.5, "lng": 101.5, "name": "Container - Malacca Strait", "type": "Container", "color": "#00aacc"},
        {"lat": 3.0, "lng": 101.2, "name": "Bulk Carrier", "type": "Bulk", "color": "#0099bb"},
        {"lat": 1.5, "lng": 102.8, "name": "Container Ship", "type": "Container", "color": "#00aacc"},
        # Suez Canal
        {"lat": 30.5, "lng": 32.3, "name": "Container - Suez North", "type": "Container", "color": "#00ccdd"},
        {"lat": 30.3, "lng": 32.3, "name": "Tanker - Suez South", "type": "Tanker", "color": "#00ccdd"},
        {"lat": 30.4, "lng": 32.3, "name": "Cargo - Canal Transit", "type": "Cargo", "color": "#00aacc"},
        # Gibraltar
        {"lat": 36.0, "lng": -5.5, "name": "Tanker - Gibraltar West", "type": "Tanker", "color": "#00ccdd"},
        {"lat": 35.8, "lng": -5.3, "name": "Cargo - Alboran Sea", "type": "Cargo", "color": "#00aacc"},
        # Panama Canal
        {"lat": 9.0, "lng": -79.7, "name": "Container - Panama Canal", "type": "Container", "color": "#00ccdd"},
        {"lat": 9.1, "lng": -79.6, "name": "Bulk Carrier - Caribbean", "type": "Bulk", "color": "#0099bb"},
        # South China Sea
        {"lat": 10.5, "lng": 115.0, "name": "Fishing Vessel - SCS", "type": "Fishing", "color": "#00ff88"},
        {"lat": 12.0, "lng": 114.5, "name": "Cargo - South China Sea", "type": "Cargo", "color": "#00aacc"},
        {"lat": 8.0, "lng": 117.0, "name": "Tanker - Palawan", "type": "Tanker", "color": "#00ccdd"},
        # East Africa / Red Sea
        {"lat": 12.5, "lng": 43.5, "name": "Tanker - Gulf of Aden", "type": "Tanker", "color": "#00ccdd"},
        {"lat": 14.0, "lng": 42.5, "name": "Cargo - Red Sea", "type": "Cargo", "color": "#00aacc"},
        {"lat": 11.5, "lng": 44.0, "name": "Container - Bab-el-Mandeb", "type": "Container", "color": "#00ccdd"},
        # Mediterranean
        {"lat": 35.5, "lng": 15.0, "name": "Tanker - Central Med", "type": "Tanker", "color": "#00ccdd"},
        {"lat": 37.0, "lng": 12.0, "name": "Cargo - Sicily Channel", "type": "Cargo", "color": "#00aacc"},
        # Atlantic Routes
        {"lat": 40.0, "lng": -40.0, "name": "Container - North Atlantic", "type": "Container", "color": "#00ccdd"},
        {"lat": 45.0, "lng": -35.0, "name": "Tanker - Atlantic Route", "type": "Tanker", "color": "#00ccdd"},
        # Indian Ocean
        {"lat": -5.0, "lng": 75.0, "name": "Tanker - Indian Ocean", "type": "Tanker", "color": "#00ccdd"},
        {"lat": -10.0, "lng": 70.0, "name": "Cargo - IO Route", "type": "Cargo", "color": "#00aacc"},
        # Pacific
        {"lat": 35.0, "lng": 145.0, "name": "Container - Pacific E", "type": "Container", "color": "#00ccdd"},
        {"lat": 30.0, "lng": 150.0, "name": "Bulk Carrier - Pacific", "type": "Bulk", "color": "#0099bb"},
        # Arctic Routes
        {"lat": 72.0, "lng": 55.0, "name": "LNG Tanker - NSR", "type": "LNG", "color": "#00ccdd"},
        {"lat": 75.0, "lng": 90.0, "name": "Cargo - Arctic Route", "type": "Cargo", "color": "#00aacc"},
        # US East Coast
        {"lat": 32.0, "lng": -75.0, "name": "Container - US East", "type": "Container", "color": "#00ccdd"},
        {"lat": 35.0, "lng": -72.0, "name": "Tanker - Off Coast", "type": "Tanker", "color": "#00ccdd"},
        # South America
        {"lat": -25.0, "lng": -45.0, "name": "Bulk Carrier - Brazil Route", "type": "Bulk", "color": "#0099bb"},
        {"lat": -5.0, "lng": -35.0, "name": "Tanker - Brazil Coast", "type": "Tanker", "color": "#00ccdd"},
    ]
    return ship_locations

@st.cache_data(ttl=300)
def fetch_earthquakes():
    try:
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        quakes = []
        for f in data.get("features", [])[:100]:
            props = f["properties"]
            coords = f["geometry"]["coordinates"]
            quakes.append({
                "lat": coords[1], "lng": coords[0],
                "mag": props.get("mag", 2.5) or 2.5,
                "place": props.get("place", "Unknown"),
                "depth": coords[2] if len(coords) > 2 else 0,
            })
        return quakes
    except:
        return []

@st.cache_data(ttl=600)
def fetch_countries():
    try:
        url = "https://restcountries.com/v3.1/all?fields=name,cca3,ccn3,capital,population,region,subregion,languages,currencies,area,flag"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        countries = {}
        for c in r.json():
            ccn3 = c.get("ccn3", "")
            if not ccn3: continue
            langs = c.get("languages", {})
            lang_str = ", ".join([str(v) for v in langs.values()][:3]) if isinstance(langs, dict) and langs else "N/A"
            currs = c.get("currencies", {})
            curr_str = ", ".join([str(v.get("name", k)) if isinstance(v, dict) else str(k) for k, v in currs.items()][:2]) if isinstance(currs, dict) and currs else "N/A"
            caps = c.get("capital", [])
            countries[ccn3] = {
                "name": c.get("name", {}).get("common", "Unknown"),
                "cca3": c.get("cca3", ""),
                "capital": caps[0] if caps else "N/A",
                "population": c.get("population", 0),
                "region": c.get("region", "N/A"),
                "subregion": c.get("subregion", "N/A"),
                "languages": lang_str,
                "currencies": curr_str,
                "area": c.get("area", 0),
                "flag": c.get("flag", ""),
            }
        return countries
    except:
        return {}

@st.cache_data(ttl=600)
def fetch_gdp():
    try:
        url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=300&mrv=1"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        if len(data) < 2: return {}
        gdp_map = {}
        for entry in data[1]:
            if entry and entry.get("value"):
                code = entry.get("countryiso3code", "")
                if code: gdp_map[code] = entry["value"]
        return gdp_map
    except:
        return {}

@st.cache_data(ttl=60)
def fetch_iss():
    try:
        r = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=8)
        r.raise_for_status()
        data = r.json()
        lat = float(data.get("latitude", 0))
        lng = float(data.get("longitude", 0))
        velocity = float(data.get("velocity", 0))
        altitude = float(data.get("altitude", 0))
        
        location_str = "Over Ocean"
        try:
            headers = {"User-Agent": "GodsEyeTerminal/1.0"}
            geo_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=3"
            geo_r = requests.get(geo_url, headers=headers, timeout=3)
            if geo_r.status_code == 200:
                geo_data = geo_r.json()
                if "error" not in geo_data and "address" in geo_data:
                    location_str = geo_data["address"].get("country", geo_data.get("name", "Unknown Landmass"))
        except:
            pass

        return {"lat": lat, "lng": lng, "velocity": velocity, "altitude": altitude, "location": location_str}
    except:
        return {"lat": 0, "lng": 0, "velocity": 0, "altitude": 0, "location": "Unknown"}

@st.cache_data(ttl=300)
def fetch_astronauts():
    try:
        r = requests.get("http://api.open-notify.org/astros.json", timeout=8)
        r.raise_for_status()
        data = r.json()
        return data.get("number", 0), data.get("people", [])
    except:
        return 0, []

@st.cache_data(ttl=300)
def fetch_weather():
    try:
        lats = ",".join([str(c[1]) for c in MAJOR_CITIES])
        lngs = ",".join([str(c[2]) for c in MAJOR_CITIES])
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lngs}&current=temperature_2m,wind_speed_10m,weather_code"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        results = []
        if isinstance(data, list):
            for i, item in enumerate(data):
                if i < len(MAJOR_CITIES):
                    current = item.get("current", {})
                    results.append({
                        "city": MAJOR_CITIES[i][0], "lat": MAJOR_CITIES[i][1], "lng": MAJOR_CITIES[i][2],
                        "temp": current.get("temperature_2m", 0), "wind": current.get("wind_speed_10m", 0),
                    })
        return results
    except:
        return []

@st.cache_data(ttl=300)
def fetch_flights():
    try:
        r = requests.get("https://opensky-network.org/api/states/all", timeout=15)
        r.raise_for_status()
        states = r.json().get("states", [])
        flights = []
        sampled = random.sample(states, min(300, len(states))) if len(states) > 300 else states
        for s in sampled:
            if s[5] is not None and s[6] is not None:
                flights.append({
                    "callsign": (s[1] or "").strip(), "country": s[2] or "Unknown",
                    "lat": s[6], "lng": s[5], "alt": s[7] or 0,
                    "velocity": s[9] or 0,
                })
        return flights
    except:
        return _sim_flights()

def _sim_flights():
    routes = [
        (40.6413,-73.7781,51.4700,-0.4543),(33.9425,-118.4081,35.5494,139.7798),
        (25.2532,55.3657,1.3644,103.9915),(48.1103,11.5528,40.0801,-2.0037),
    ]
    flights = []
    for la1,lo1,la2,lo2 in routes:
        for _ in range(15):
            t = random.uniform(0,1)
            flights.append({
                "callsign": f"SIM{random.randint(100,999)}", "country": "Simulated",
                "lat": la1+(la2-la1)*t+random.uniform(-2,2),
                "lng": lo1+(lo2-lo1)*t+random.uniform(-2,2),
                "alt": random.uniform(8000,12000), "velocity": random.uniform(200,280),
            })
    return flights

def generate_satellites(count=180):
    sats = []
    constellations = [
        ("Starlink", 60, 0.04, 0.06),
        ("OneWeb", 25, 0.05, 0.07),
        ("GPS", 15, 0.08, 0.12),
        ("Iridium", 15, 0.05, 0.065),
        ("Galileo", 10, 0.09, 0.11),
        ("GLONASS", 10, 0.08, 0.10),
        ("Misc LEO", 45, 0.03, 0.08),
    ]
    for name, n, alt_min, alt_max in constellations:
        for _ in range(n):
            sats.append({
                "name": name,
                "lat": random.uniform(-75, 75),
                "lng": random.uniform(-180, 180),
                "alt": random.uniform(alt_min, alt_max),
            })
    return sats

def generate_cyber_arcs(count=20):
    sources = [
        (55.7558, 37.6176), (39.9042, 116.4074), (35.6892, 51.3890),
        (33.3152, 44.3661), (12.9716, 77.5946), (-23.5505, -46.6333),
        (6.5244, 3.3792), (52.5200, 13.4050),
    ]
    targets = [
        (38.9072, -77.0369), (51.5074, -0.1278), (35.6762, 139.6503),
        (1.3521, 103.8198), (48.8566, 2.3522), (-33.8688, 151.2093),
        (37.5665, 126.9780), (45.4215, -75.6972),
    ]
    arcs = []
    for _ in range(count):
        src = random.choice(sources)
        tgt = random.choice(targets)
        arcs.append({
            "startLat": src[0], "startLng": src[1],
            "endLat": tgt[0], "endLng": tgt[1],
        })
    return arcs


# ══════════════════════════════════════════════════════════════════════════════
# ── ROBUST GLOBE BUILDER ────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def build_globe_html(
    earthquakes, weather, iss, flights, satellites, countries_db,
    gdp_data, cyber_arcs, emergencies, show_seismic, show_weather, show_satellites,
    show_flights, show_shipping, show_cyber, show_emergencies,
    global_events, volcanoes, fires, disasters, ships,
    show_conflicts, show_fires, show_volcanoes, show_disasters, show_population,
    globe_w=1060, globe_h=720,
):
    
    all_points = []
    all_rings = []
    all_arcs = []

    # GDELT/ACLED/UCDP Global Events
    if show_conflicts and global_events:
        for ev in global_events:
            all_points.append({
                "lat": ev["lat"], "lng": ev["lng"],
                "color": ev["color"],
                "size": ev.get("size", 0.2),
                "alt": ev.get("alt", 0.01),
                "type": ev.get("type", "event"),
                "label": ev.get("label", "Event"),
                "detail": ev.get("detail", ""),
            })
            if ev.get("category") in ["acled", "ucdp"]:
                all_rings.append({
                    "lat": ev["lat"], "lng": ev["lng"],
                    "color": ev["color"],
                    "maxR": 2.5 if ev["color"] == "#ff0000" else 2,
                    "propagationSpeed": 3, "repeatPeriod": 800,
                })

    # Seismic
    if show_seismic:
        for q in earthquakes:
            mag = q["mag"]
            norm = min(max((mag - 2) / 6, 0), 1)
            color = "#ff1133" if mag >= 5 else "#ff4422" if mag >= 4 else "#ff7744"
            all_points.append({
                "lat": q["lat"], "lng": q["lng"],
                "color": color,
                "size": 0.3 + norm * 0.7,
                "alt": 0.01,
                "type": "earthquake",
                "label": f"M{mag:.1f} - {q['place']}",
                "detail": f"Depth: {q['depth']:.0f}km",
            })
            all_rings.append({
                "lat": q["lat"], "lng": q["lng"],
                "color": color,
                "maxR": 2 + mag * 0.8,
                "propagationSpeed": 2,
                "repeatPeriod": 1000,
            })

    # Volcanoes
    if show_volcanoes and volcanoes:
        for v in volcanoes:
            all_points.append({
                "lat": v["lat"], "lng": v["lng"],
                "color": v["color"],
                "size": 0.35,
                "alt": 0.02,
                "type": "volcano",
                "label": v["name"],
                "detail": f"Status: {v.get('status', 'Unknown')}",
            })
            if "erupting" in v.get("status", "").lower():
                all_rings.append({
                    "lat": v["lat"], "lng": v["lng"],
                    "color": "#ff0000",
                    "maxR": 2.5, "propagationSpeed": 3, "repeatPeriod": 600,
                })

    # Fires
    if show_fires and fires:
        for f in fires:
            all_points.append({
                "lat": f["lat"], "lng": f["lng"],
                "color": f["color"],
                "size": 0.25,
                "alt": 0.015,
                "type": "fire",
                "label": f["name"],
                "detail": f"Date: {f.get('date', 'N/A')}",
            })

    # Disasters
    if show_disasters and disasters:
        for d in disasters:
            all_points.append({
                "lat": d["lat"], "lng": d["lng"],
                "color": d["color"],
                "size": 0.28,
                "alt": 0.012,
                "type": "disaster",
                "label": d["name"],
                "detail": f"Category: {d.get('category', 'N/A').replace('_', ' ').title()}",
            })

    # Ships
    if show_shipping and ships:
        for s in ships:
            all_points.append({
                "lat": s["lat"], "lng": s["lng"],
                "color": s["color"],
                "size": 0.18,
                "alt": 0.002,
                "type": "ship",
                "label": s["name"],
                "detail": f"Type: {s.get('type', 'Vessel')}",
            })

    # Emergencies
    if show_emergencies:
        for e in emergencies:
            if e["severity"] == "high":
                color, size, spd, per = "#ff0033", 0.6, 4, 600
            elif e["severity"] == "medium":
                color, size, spd, per = "#ff6600", 0.45, 3, 900
            else:
                color, size, spd, per = "#ffaa00", 0.35, 2, 1200
            all_points.append({
                "lat": e["lat"], "lng": e["lng"],
                "color": color, "size": size, "alt": 0.008,
                "type": "emergency", "label": e["name"],
                "detail": f"Severity: {e['severity'].upper()}"
            })
            all_rings.append({
                "lat": e["lat"], "lng": e["lng"],
                "color": color, "maxR": 3 if e["severity"]=="high" else 2,
                "propagationSpeed": spd, "repeatPeriod": per
            })

    # Weather
    if show_weather:
        for w in weather:
            t = w["temp"]
            if t < -10: c = "#4444ff"
            elif t < 0: c = "#0088ff"
            elif t < 10: c = "#00ccff"
            elif t < 20: c = "#00ff88"
            elif t < 30: c = "#ffcc00"
            elif t < 40: c = "#ff6600"
            else: c = "#ff0033"
            all_points.append({
                "lat": w["lat"], "lng": w["lng"],
                "color": c, "size": 0.35, "alt": 0.015,
                "type": "weather", "label": f"{w['city']}: {t}°C",
                "detail": f"Wind: {w['wind']}km/h",
            })

    # Satellites & ISS
    if show_satellites:
        all_points.append({
            "lat": iss["lat"], "lng": iss["lng"],
            "color": "#ff00ff", "size": 0.8, "alt": 0.06,
            "type": "iss", "label": "ISS - International Space Station",
            "detail": f"Lat: {iss['lat']:.2f} Lng: {iss['lng']:.2f}",
        })
        all_rings.append({
            "lat": iss["lat"], "lng": iss["lng"],
            "color": "#ff00ff", "maxR": 4, "propagationSpeed": 3, "repeatPeriod": 800,
        })
        for s in satellites:
            c = "#00ff88" if "Starlink" in s["name"] else "#00ccff"
            all_points.append({
                "lat": s["lat"], "lng": s["lng"],
                "color": c, "size": 0.12, "alt": s["alt"],
                "type": "satellite", "label": s["name"],
                "detail": f"Alt: {s['alt']*6371:.0f}km",
            })

    # Flights
    if show_flights:
        for f in flights:
            all_points.append({
                "lat": f["lat"], "lng": f["lng"],
                "color": "#ff6600", "size": 0.15,
                "alt": 0.008 + min(f["alt"] / 500000, 0.02),
                "type": "flight", "label": f"{f['callsign']} ({f['country']})",
                "detail": f"Alt: {f['alt']:.0f}m",
                "rawAlt": f["alt"], "velocity": f["velocity"],
            })
        for la1, lo1, la2, lo2, name in FLIGHT_ROUTES:
            all_arcs.append({
                "startLat": la1, "startLng": lo1,
                "endLat": la2, "endLng": lo2,
                "color": "#ff660066", "stroke": 0.5, "alt": 0.1,
                "dashLen": 0.8, "dashGap": 0.1, "animTime": 2500,
            })

    # Shipping Routes
    if show_shipping:
        for la1, lo1, la2, lo2, name in SHIPPING_ROUTES:
            all_arcs.append({
                "startLat": la1, "startLng": lo1,
                "endLat": la2, "endLng": lo2,
                "color": "#00ccdd44", "stroke": 0.6, "alt": 0.04,
                "dashLen": 0.5, "dashGap": 0.15, "animTime": 4000,
            })

    # Cyber Arcs
    if show_cyber:
        for arc in cyber_arcs:
            all_arcs.append({
                "startLat": arc["startLat"], "startLng": arc["startLng"],
                "endLat": arc["endLat"], "endLng": arc["endLng"],
                "color": random.choice(["#ff335566", "#ff660066", "#bf00ff66"]),
                "stroke": 0.35, "alt": 0.18,
                "dashLen": 0.15, "dashGap": 0.15, "animTime": 2000,
            })

    # Satellite Constellation Links
    if show_satellites:
        const_groups = {}
        for s in satellites:
            name = s["name"]
            if name not in const_groups:
                const_groups[name] = []
            const_groups[name].append(s)
        constellation_colors = {
            "Starlink": "#00ff8833", "OneWeb": "#00ccff33", "GPS": "#ffcc0033",
            "Iridium": "#ff660033", "Galileo": "#bf00ff33", "GLONASS": "#ff335533",
            "Misc LEO": "#00ccff22"
        }
        for cname, sats_list in const_groups.items():
            color = constellation_colors.get(cname, "#00ccff22")
            sorted_sats = sorted(sats_list, key=lambda x: x["lng"])
            for i in range(0, len(sorted_sats) - 1, 2):
                s1 = sorted_sats[i]
                s2 = sorted_sats[i + 1]
                all_arcs.append({
                    "startLat": s1["lat"], "startLng": s1["lng"],
                    "endLat": s2["lat"], "endLng": s2["lng"],
                    "color": color, "stroke": 0.2,
                    "alt": (s1["alt"] + s2["alt"]) / 2,
                    "dashLen": 0.3, "dashGap": 0.2, "animTime": 4000,
                })

    # Build country DB with safe access to all fields
    country_db_js = {}
    for ccn3, c in countries_db.items():
        cca3 = c.get("cca3", "")
        country_db_js[ccn3] = {
            "n": c.get("name", "Unknown"),
            "f": c.get("flag", ""),
            "c": c.get("capital", "N/A"),
            "p": c.get("population", 0),
            "g": gdp_data.get(cca3, 0),
            "l": c.get("languages", "N/A"),
            "r": c.get("region", "N/A"),
            "sr": c.get("subregion", "N/A"),
            "cu": c.get("currencies", "N/A"),
            "a": c.get("area", 0),
            "cca3": cca3
        }

    points_json = json.dumps(all_points)
    rings_json = json.dumps(all_rings)
    arcs_json = json.dumps(all_arcs)
    country_db_json = json.dumps(country_db_js)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{
    width: 100%; height: 100%;
    background: #000; overflow: hidden;
    font-family: 'Share Tech Mono', monospace;
}}
#globe-container {{ width: 100%; height: 100%; position: relative; }}

#tip {{
    position: fixed;
    background: linear-gradient(145deg, rgba(2,15,40,0.97), rgba(0,8,25,0.99));
    border: 1px solid rgba(0,240,255,0.5);
    border-radius: 14px;
    padding: 12px 18px;
    color: #00f0ff;
    font: 12px 'Share Tech Mono', monospace;
    letter-spacing: 0.8px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;
    box-shadow: 0 0 35px rgba(0,240,255,0.2);
    z-index: 200;
    max-width: 350px;
    backdrop-filter: blur(20px);
    line-height: 1.7;
}}
#tip .tip-title {{
    font-family: 'Orbitron', sans-serif;
    font-size: 10px; font-weight: 700;
    letter-spacing: 2px; margin-bottom: 5px;
    padding-bottom: 4px; border-bottom: 1px solid rgba(0,240,255,0.15);
}}
#tip .tip-row {{ display: flex; justify-content: space-between; gap: 12px; padding: 1px 0; font-size: 11px; }}
#tip .tip-label {{ color: rgba(0,240,255,0.4); }}
#tip .tip-val {{ color: #00f0ff; font-weight: 600; }}

#country-tip {{
    position: fixed;
    background: linear-gradient(145deg, rgba(2,15,40,0.97), rgba(0,5,20,0.99));
    border: 1px solid rgba(0,240,255,0.35);
    border-radius: 14px; padding: 14px 18px;
    pointer-events: none; opacity: 0;
    transition: opacity 0.2s;
    box-shadow: 0 0 40px rgba(0,240,255,0.12);
    z-index: 200; max-width: 300px;
    backdrop-filter: blur(20px);
    font: 11px 'Share Tech Mono', monospace;
    color: #00f0ff; letter-spacing: 0.5px; line-height: 1.7;
}}
#country-tip .ct-name {{ font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 700; color: #00f0ff; letter-spacing: 2px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid rgba(0,240,255,0.15); }}
#country-tip .ct-row {{ display: flex; justify-content: space-between; gap: 10px; padding: 1px 0; }}
#country-tip .ct-label {{ color: rgba(0,240,255,0.45); }}
#country-tip .ct-val {{ color: #00f0ff; text-align: right; }}

@keyframes cardIn {{ from {{ opacity:0; transform: translate(-50%,-50%) scale(0.7); }} to {{ opacity:1; transform: translate(-50%,-50%) scale(1); }} }}
#country-card {{
    position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    width: 320px;
    background: linear-gradient(160deg, rgba(2,20,50,0.97), rgba(0,8,25,0.99));
    border: 1px solid rgba(0,240,255,0.4); border-radius: 18px;
    padding: 24px 28px; z-index: 300;
    backdrop-filter: blur(30px);
    animation: cardIn 0.4s cubic-bezier(0.34,1.56,0.64,1) forwards;
    display: none;
}}
#country-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #00f0ff, transparent); border-radius: 18px 18px 0 0; }}
.cc-flag {{ font-size: 48px; text-align: center; margin-bottom: 8px; }}
.cc-name {{ font-family: 'Orbitron', sans-serif; font-size: 16px; font-weight: 700; color: #00f0ff; letter-spacing: 3px; text-align: center; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid rgba(0,240,255,0.12); }}
.cc-row {{ display: flex; justify-content: space-between; gap: 10px; padding: 5px 0; font: 12px 'Share Tech Mono', monospace; border-bottom: 1px solid rgba(0,240,255,0.04); }}
.cc-label {{ color: rgba(0,240,255,0.4); letter-spacing: 1px; }}
.cc-val {{ color: #00f0ff; font-weight: 600; text-align: right; }}
.cc-dismiss {{ text-align: center; margin-top: 12px; font: 9px 'Share Tech Mono', monospace; color: rgba(0,240,255,0.2); letter-spacing: 2px; }}
#card-overlay {{ position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); z-index: 299; display: none; }}

#legend {{
    position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%);
    width: 98%;
    display: flex; justify-content: space-evenly; align-items: center;
    background: rgba(0,10,25,0.92);
    border: 1px solid rgba(0,240,255,0.15);
    border-radius: 12px; padding: 8px 10px;
    z-index: 50; backdrop-filter: blur(15px);
    flex-wrap: nowrap; overflow-x: auto;
}}
.leg {{ display: flex; align-items: center; gap: 5px; color: rgba(0,240,255,0.7); font-size: 10px; letter-spacing: 0.8px; white-space: nowrap; }}
.ldot {{ width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }}

#loading {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); z-index: 100; text-align: center; }}
#loading .spinner {{ width: 40px; height: 40px; border: 2px solid rgba(0,240,255,0.1); border-top: 2px solid #00f0ff; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
#loading .load-text {{ font-family: 'Orbitron', sans-serif; font-size: 11px; color: #00f0ff; letter-spacing: 3px; text-shadow: 0 0 15px rgba(0,240,255,0.5); }}
</style>
</head>
<body>
<div id="globe-container"></div>
<div id="tip"></div>
<div id="country-tip"></div>
<div id="card-overlay"></div>
<div id="country-card"></div>
<div id="loading"><div class="spinner"></div><div class="load-text">INITIALIZING GLOBE</div></div>
<div id="legend">
    <div class="leg"><div class="ldot" style="background:#ff3355;box-shadow:0 0 5px #ff3355;"></div>Conflicts</div>
    <div class="leg"><div class="ldot" style="background:#ff1133;box-shadow:0 0 5px #ff1133;"></div>Seismic</div>
    <div class="leg"><div class="ldot" style="background:#ff4400;box-shadow:0 0 5px #ff4400;"></div>Volcanoes</div>
    <div class="leg"><div class="ldot" style="background:#ff2200;box-shadow:0 0 5px #ff2200;"></div>Wildfires</div>
    <div class="leg"><div class="ldot" style="background:#ffcc00;box-shadow:0 0 5px #ffcc00;"></div>Disasters</div>
    <div class="leg"><div class="ldot" style="background:#00ff88;box-shadow:0 0 5px #00ff88;"></div>Satellites</div>
    <div class="leg"><div class="ldot" style="background:#ff6600;box-shadow:0 0 5px #ff6600;"></div>Flights</div>
    <div class="leg"><div class="ldot" style="background:#00ccdd;box-shadow:0 0 5px #00ccdd;"></div>Ships</div>
    <div class="leg"><div class="ldot" style="background:#00ccff;box-shadow:0 0 5px #00ccff;"></div>Weather</div>
    <div class="leg"><div class="ldot" style="background:#ff00ff;box-shadow:0 0 5px #ff00ff;"></div>ISS</div>
    <div class="leg"><div class="ldot" style="background:#bf00ff;box-shadow:0 0 5px #bf00ff;"></div>Cyber</div>
</div>

<script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
<script src="https://unpkg.com/globe.gl@2.27.2/dist/globe.gl.min.js"></script>
<script src="https://unpkg.com/topojson-client@3.1.0/dist/topojson-client.min.js"></script>
<script>
(function init() {{
    if (typeof Globe === 'undefined' || typeof THREE === 'undefined') {{
        if (!window._rc) window._rc = 0; window._rc++;
        if (window._rc > 60) {{ document.getElementById('loading').innerHTML = '<div class="load-text" style="color:#ff3355;">LOAD FAILED</div>'; return; }}
        setTimeout(init, 300); return;
    }}

    var POINTS = {points_json};
    var RINGS = {rings_json};
    var ARCS = {arcs_json};
    var CDB = {country_db_json};

    function fmtNum(n) {{ if (n >= 1e12) return (n/1e12).toFixed(1)+'T'; if (n >= 1e9) return (n/1e9).toFixed(1)+'B'; if (n >= 1e6) return (n/1e6).toFixed(1)+'M'; if (n >= 1e3) return (n/1e3).toFixed(1)+'K'; return n.toString(); }}
    function fmtArea(n) {{ if (n >= 1e6) return (n/1e6).toFixed(2)+'M km²'; if (n >= 1e3) return (n/1e3).toFixed(1)+'K km²'; return n + ' km²'; }}

    function gdpColor(id) {{ var v = GDP_DB[id]; if (!v) return 'rgba(0,20,55,0.2)'; var logV = Math.log10(Math.max(v, 1)); var norm = Math.min(Math.max((logV - 8) / 6, 0), 1); return 'rgba('+Math.floor(norm*255)+','+Math.floor((1-Math.abs(norm-0.5)*2)*200)+','+Math.floor((1-norm)*255)+',0.55)'; }}
    function popColor(id) {{ var v = POP_DB[id]; if (!v) return 'rgba(0,20,55,0.2)'; var logV = Math.log10(Math.max(v, 1)); var norm = Math.min(Math.max((logV - 5) / 5, 0), 1); return 'rgba('+Math.floor(180+75*norm)+','+Math.floor(50*(1-norm))+','+Math.floor(220*(1-norm))+',0.5)'; }}

    var pauseTimer = null, _ctrl = null;
    function pauseRotation(ms) {{ if (_ctrl) {{ _ctrl.autoRotate = false; if (pauseTimer) clearTimeout(pauseTimer); pauseTimer = setTimeout(function() {{ if (_ctrl) _ctrl.autoRotate = true; }}, ms || 5000); }} }}

    var ccard = document.getElementById('country-card'), coverlay = document.getElementById('card-overlay'), cardTimer = null;
    function showCountryCard(info) {{ if (!info) return; ccard.innerHTML = '<div class="cc-flag">'+info.f+'</div><div class="cc-name">'+info.n+'</div><div class="cc-row"><span class="cc-label">CAPITAL</span><span class="cc-val">'+info.c+'</span></div><div class="cc-row"><span class="cc-label">POPULATION</span><span class="cc-val">'+fmtNum(info.p)+'</span></div><div class="cc-row"><span class="cc-label">GDP</span><span class="cc-val">'+(info.g ? '$'+fmtNum(info.g) : 'N/A')+'</span></div><div class="cc-row"><span class="cc-label">REGION</span><span class="cc-val">'+info.r+'</span></div><div class="cc-row"><span class="cc-label">SUBREGION</span><span class="cc-val">'+(info.sr||'N/A')+'</span></div><div class="cc-row"><span class="cc-label">LANGUAGES</span><span class="cc-val">'+(info.l||'N/A')+'</span></div><div class="cc-row"><span class="cc-label">CURRENCY</span><span class="cc-val">'+(info.cu||'N/A')+'</span></div><div class="cc-row"><span class="cc-label">AREA</span><span class="cc-val">'+fmtArea(info.a||0)+'</span></div><div class="cc-dismiss">CLICK TO DISMISS</div>'; ccard.style.display = 'block'; coverlay.style.display = 'block'; if (cardTimer) clearTimeout(cardTimer); cardTimer = setTimeout(hideCard, 6000); pauseRotation(7000); }}
    function hideCard() {{ ccard.style.display = 'none'; coverlay.style.display = 'none'; if (cardTimer) clearTimeout(cardTimer); }}
    ccard.addEventListener('click', hideCard); coverlay.addEventListener('click', hideCard);
    var pointHovered = false;

    try {{
        var world = Globe()
            (document.getElementById('globe-container'))
            .width(document.getElementById('globe-container').clientWidth)
            .height(document.getElementById('globe-container').clientHeight)
            .backgroundColor('#000000')
            .showAtmosphere(true)
            .atmosphereColor('#00d4ff')
            .atmosphereAltitude(0.28)
            .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
            .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
            .polygonsData([])
            .polygonCapColor(function(d) {{ var id = d.id || (d.properties && d.properties.iso_n3) || ''; if (POLY_MODE === 'gdp') return gdpColor(id); if (POLY_MODE === 'population') return popColor(id); return 'rgba(0,20,55,0.18)'; }})
            .polygonSideColor(function() {{ return 'rgba(0,180,255,0.05)'; }})
            .polygonStrokeColor(function() {{ return 'rgba(0,212,255,0.35)'; }})
            .polygonAltitude(function(d) {{ if (d.__h) return 0.025; if (POLY_MODE === 'gdp') {{ var v = GDP_DB[d.id || '']; if (v) return 0.004 + Math.min(Math.log10(Math.max(v,1))/100, 0.03); }} return 0.005; }})
            .polygonLabel(function() {{ return ''; }})
            .pointsData(POINTS)
            .pointLat('lat').pointLng('lng').pointColor('color')
            .pointRadius(function(d) {{ return d.size || 0.3; }})
            .pointAltitude(function(d) {{ return d.alt || 0.01; }})
            .pointResolution(12)
            .pointsMerge(false)
            .ringsData(RINGS)
            .ringLat('lat').ringLng('lng')
            .ringColor(function(d) {{ return function(t) {{ var c = d.color || '0,240,255'; if (c.startsWith('#')) {{ var hex = c.replace('#',''); c = parseInt(hex.substr(0,2),16)+','+parseInt(hex.substr(2,2),16)+','+parseInt(hex.substr(4,2),16); }} return 'rgba('+c+','+Math.max(0,1-t)+')'; }}; }})
            .ringMaxRadius('maxR').ringPropagationSpeed('propagationSpeed').ringRepeatPeriod('repeatPeriod')
            .arcsData(ARCS)
            .arcStartLat('startLat').arcStartLng('startLng').arcEndLat('endLat').arcEndLng('endLng')
            .arcColor('color')
            .arcAltitude(function(d) {{ return d.alt || 0.15; }})
            .arcStroke(function(d) {{ return d.stroke || 0.5; }})
            .arcDashLength(function(d) {{ return d.dashLen || 0.4; }})
            .arcDashGap(function(d) {{ return d.dashGap || 0.2; }})
            .arcDashAnimateTime(function(d) {{ return d.animTime || 2500; }});

        var mat = world.globeMaterial(); mat.bumpScale = 6;

        try {{ var starGeo = new THREE.BufferGeometry(); var starCount = 8000; var starPos = new Float32Array(starCount*3); var starColors = new Float32Array(starCount*3); for (var i = 0; i < starCount; i++) {{ starPos[i*3]=(Math.random()-0.5)*3000; starPos[i*3+1]=(Math.random()-0.5)*3000; starPos[i*3+2]=(Math.random()-0.5)*3000; var br = 0.3 + Math.random()*0.7; var tn = Math.random(); starColors[i*3]=br*(tn>0.7?0.7:1.0); starColors[i*3+1]=br*(tn>0.85?0.8:1.0); starColors[i*3+2]=br; }} starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3)); starGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3)); var starMat = new THREE.PointsMaterial({{size:0.8,transparent:true,opacity:0.7,vertexColors:true,sizeAttenuation:true}}); world.scene().add(new THREE.Points(starGeo, starMat)); }} catch(e) {{ console.warn('Stars:', e); }}

        fetch('https://unpkg.com/world-atlas@2/countries-110m.json').then(function(r) {{ return r.json(); }}).then(function(topo) {{ world.polygonsData(topojson.feature(topo, topo.objects.countries).features); }}).catch(function(e) {{ console.warn('Borders:', e); }});

        var ctip = document.getElementById('country-tip'), hovPoly = null;
        world.onPolygonHover(function(poly) {{ if (hovPoly) hovPoly.__h = false; if (poly) poly.__h = true; hovPoly = poly; world.polygonAltitude(function(d) {{ if (d.__h) return 0.028; if (POLY_MODE === 'gdp') {{ var v = GDP_DB[d.id || '']; if (v) return 0.004 + Math.min(Math.log10(Math.max(v,1))/100, 0.03); }} return 0.005; }}).polygonCapColor(function(d) {{ var id = d.id || (d.properties && d.properties.iso_n3) || ''; if (d.__h) return 'rgba(0,240,255,0.25)'; if (POLY_MODE === 'gdp') return gdpColor(id); if (POLY_MODE === 'population') return popColor(id); return 'rgba(0,20,55,0.18)'; }}); if (poly && !pointHovered) {{ var id = poly.id || (poly.properties && poly.properties.iso_n3) || ''; var info = CDB[id]; if (info) {{ ctip.innerHTML = '<div class="ct-name">'+info.f+' '+info.n+'</div><div class="ct-row"><span class="ct-label">Capital</span><span class="ct-val">'+info.c+'</span></div><div class="ct-row"><span class="ct-label">Population</span><span class="ct-val">'+fmtNum(info.p)+'</span></div><div class="ct-row"><span class="ct-label">GDP</span><span class="ct-val">'+(info.g?'$'+fmtNum(info.g):'N/A')+'</span></div><div class="ct-row"><span class="ct-label">Region</span><span class="ct-val">'+info.r+'</span></div>'; ctip.style.opacity = '1'; }} else {{ ctip.style.opacity = '0'; }} }} else {{ ctip.style.opacity = '0'; }} }});

        world.onPolygonClick(function(poly) {{ if (!poly) return; var id = poly.id || (poly.properties && poly.properties.iso_n3) || ''; var info = CDB[id]; if (info) showCountryCard(info); }});

        var tip = document.getElementById('tip'), typeColors = {{ earthquake:'#ff3355', weather:'#00ccff', iss:'#ff00ff', satellite:'#00ff88', flight:'#ff6600', ship:'#00ccdd', emergency:'#ff6600', cyber:'#bf00ff', conflict:'#ff0033', volcano:'#ff4400', fire:'#ff2200', disaster:'#ffcc00' }};
        world.onPointHover(function(pt) {{ if (pt) {{ pointHovered = true; ctip.style.opacity = '0'; var tc = typeColors[pt.type] || '#00f0ff'; tip.innerHTML = '<div class="tip-title" style="color:'+tc+';border-bottom-color:'+tc+'44;">'+pt.type.toUpperCase()+'</div><div style="margin:3px 0;">'+(pt.label||'')+'</div>'+(pt.detail?'<div class="tip-row"><span class="tip-label">Info</span><span class="tip-val" style="color:'+tc+';">'+pt.detail+'</span></div>':''); tip.style.borderColor = tc+'66'; tip.style.opacity = '1'; }} else {{ pointHovered = false; tip.style.opacity = '0'; }} }});
        world.onPointClick(function(pt) {{ if (pt) pauseRotation(5000); }});

        document.addEventListener('mousemove', function(e) {{ tip.style.left = (e.clientX+18)+'px'; tip.style.top = (e.clientY-12)+'px'; ctip.style.left = (e.clientX+18)+'px'; ctip.style.top = (e.clientY-12)+'px'; }});

        _ctrl = world.controls(); _ctrl.autoRotate = true; _ctrl.autoRotateSpeed = 0.4; _ctrl.enableDamping = true; _ctrl.dampingFactor = 0.08; _ctrl.minDistance = 120; _ctrl.maxDistance = 700; _ctrl.rotateSpeed = 0.5; _ctrl.zoomSpeed = 0.8;
        world.pointOfView({{ lat: 20, lng: 10, altitude: 2.0 }}, 0);
        document.getElementById('loading').style.display = 'none';
    }} catch(err) {{ document.getElementById('loading').innerHTML = '<div class="load-text" style="color:#ff3355;">ERROR: '+err.message+'</div>'; console.error(err); }}
}})();
</script>
</body>
</html>"""
    return html


# ══════════════════════════════════════════════════════════════════════════════
# ── AUTHENTICATOR ────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
try:
    credentials = st.secrets["credentials"].to_dict()
    authenticator = stauth.Authenticate(
        credentials,
        st.secrets["cookie"]["name"],
        st.secrets["cookie"]["key"],
        st.secrets["cookie"]["expiry_days"],
        auto_hash=False,
    )
except Exception as e:
    st.error(f"Authentication config error: {e}")
    st.stop()

authenticator.login(
    location="main",
    fields={
        "Form name": "GOD's EYE",
        "Username": "CONFIRM YOUR IDENTITY",
        "Password": "ACCESS KEY",
        "Login": "AUTHENTICATE",
    },
)

auth_status = st.session_state.get("authentication_status")
auth_name = st.session_state.get("name", "Operator")


# ══════════════════════════════════════════════════════════════════════════════
# ── MAIN DASHBOARD ───────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
if auth_status is True:

    # Fetch all data
    earthquakes = fetch_earthquakes()
    countries_db = fetch_countries()
    gdp_data = fetch_gdp()
    iss = fetch_iss()
    astro_count, astro_list = fetch_astronauts()
    weather = fetch_weather()
    flights = fetch_flights()
    satellites = generate_satellites(180)
    cyber_arcs = generate_cyber_arcs(20)
    emergencies = EMERGENCY_ZONES
    
    # New data sources
    global_events = fetch_global_events()
    volcanoes = fetch_volcanoes()
    fires = fetch_fires()
    disasters = fetch_nasa_disasters()
    ships = fetch_ais_ships()
    
    ist_offset = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist_offset)

    # ── Header ──
    st.markdown(f"""
    <div class="cmd-header">
        <h1>GOD'S EYE</h1>
        <div class="subtitle">A Global Intelligence Radar With Live Terminal </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Status Bar ──
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-item">
            <div class="status-dot" style="color:#00ff88;background:#00ff88;"></div>
            <span class="status-label">STATUS</span>
            <span class="status-value">LIVE</span>
        </div>
        <div class="status-item">
            <span class="status-label">IST</span>
            <span class="status-value">{now.strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
        <div class="status-item">
            <span class="status-label">ISS</span>
            <span class="status-value">{iss['lat']:.2f}°, {iss['lng']:.2f}°</span>
        </div>
        <div class="status-item">
            <span class="status-label">ASTRONAUTS</span>
            <span class="status-value">{astro_count}</span>
        </div>
        <div class="status-item">
            <span class="status-label">CONFLICTS</span>
            <span class="status-value">{len(global_events)}</span>
        </div>
        <div class="status-item">
            <span class="status-label">VOLCANOES</span>
            <span class="status-value">{len(volcanoes)}</span>
        </div>
        <div class="status-item">
            <span class="status-label">FIRES</span>
            <span class="status-value">{len(fires)}</span>
        </div>
        <div class="status-item">
            <span class="status-label">SHIPS</span>
            <span class="status-value">{len(ships)}</span>
        </div>
        <div class="status-item">
            <span class="status-label">OPERATOR</span>
            <span class="status-value">{auth_name.upper()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # Layout
    # ═══════════════════════════════════════════════════════════════════════════
    left_col, globe_col, right_col = st.columns([1, 4.8, 1.2], gap="small")

    # ── LEFT PANEL ─────────────────────────────────────────────────────────
    with left_col:
        
        # ── LIVE DATA SOURCES SECTION ──
        st.markdown('<div class="panel-card panel-card-cyan"><div class="panel-title">◆ DATA SOURCES</div></div>', unsafe_allow_html=True)

        show_conflicts = st.checkbox(f"GLOBAL CONFLICTS ({len(global_events)})", value=st.session_state.show_conflicts, key="cb_conf")
        show_flights = st.checkbox(f"FLIGHTS ({len(flights)})", value=st.session_state.show_flights, key="cb_fl")
        show_weather = st.checkbox(f"WEATHER ({len(weather)})", value=st.session_state.show_weather, key="cb_wx")
        show_satellites = st.checkbox(f"SATELLITES ({len(satellites)+1})", value=st.session_state.show_satellites, key="cb_sat")
        show_seismic = st.checkbox(f"EARTHQUAKES ({len(earthquakes)})", value=st.session_state.show_seismic, key="cb_seismic")
        show_volcanoes = st.checkbox(f"VOLCANOES ({len(volcanoes)})", value=st.session_state.show_volcanoes, key="cb_volc")
        show_fires = st.checkbox(f"WILDFIRES ({len(fires)})", value=st.session_state.show_fires, key="cb_fires")
        show_disasters = st.checkbox(f"DISASTERS ({len(disasters)})", value=st.session_state.show_disasters, key="cb_dis")
        show_shipping = st.checkbox(f"MARITIME ({len(ships)} vessels)", value=st.session_state.show_shipping, key="cb_sh")
        show_emergencies = st.checkbox(f"CRISIS ZONES ({len(emergencies)})", value=st.session_state.show_emergencies, key="cb_emrg")
        show_cyber = st.checkbox(f"CYBER THREATS ({len(cyber_arcs)})", value=st.session_state.show_cyber, key="cb_cy")
        
        st.session_state.show_seismic = show_seismic
        st.session_state.show_emergencies = show_emergencies
        st.session_state.show_weather = show_weather
        st.session_state.show_satellites = show_satellites
        st.session_state.show_flights = show_flights
        st.session_state.show_shipping = show_shipping
        st.session_state.show_cyber = show_cyber
        st.session_state.show_conflicts = show_conflicts
        st.session_state.show_fires = show_fires
        st.session_state.show_volcanoes = show_volcanoes
        st.session_state.show_disasters = show_disasters

        # ── EARTH INFO SECTION ──
        st.markdown('<div class="panel-card panel-card-green" style="margin-top:6px;"><div class="panel-title" style="color:#00ff88;">◆ EARTH VITALS</div></div>', unsafe_allow_html=True)
        
        earth_stats = [
            ("RADIUS", "6,371 km", "#00ff88"),
            ("MASS", "5.97 × 10²⁴ kg", "#00f0ff"),
            ("VOLUME", "1.08 × 10¹² km³", "#00f0ff"),
            ("WATER", "71%", "#00ccff"),
            ("VELOCITY", "29.78 km/s", "#ffcc00"),
            ("AGE", "4.54 Billion Years", "#ff00ff"),
        ]
        
        for label, val, color in earth_stats:
            st.markdown(f'''
            <div class="intel-item" style="border-left:3px solid {color}88;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:rgba(0,240,255,0.6); font-size:0.55rem; letter-spacing:1px; font-weight:600;">{label}</span>
                    <span style="color:{color}; font-size:0.6rem; font-weight:700; font-family:'Orbitron',sans-serif;">{val}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        # ── HUMANS IN ORBIT & ISS ──
        st.markdown('<div class="panel-card panel-card-purple" style="margin-top:6px;"><div class="panel-title" style="color:#ff00ff;">◆ HUMANS IN ORBIT</div></div>', unsafe_allow_html=True)
        if astro_list:
            ah = f'<div class="intel-item" style="border-left:3px solid rgba(255,0,255,0.3);padding:6px 8px;">'
            ah += f'<div style="color:#ff00ff;font-size:0.62rem;font-weight:700;margin-bottom:3px;">Currently in Space</div>'
            for a in astro_list[:5]:
                ah += f'<div style="padding:1px 0;font-size:0.56rem;"><span style="color:rgba(255,0,255,0.4);font-size:0.5rem;">{a.get("craft","")}</span> <span style="color:rgba(0,240,255,0.6);">{a.get("name","")}</span></div>'
            ah += '</div>'
            st.markdown(ah, unsafe_allow_html=True)



        # ── DISCONNECT BUTTON ──
        st.markdown("""
        <style>
        .stButton > button {
            background: linear-gradient(135deg, rgba(255,0,0,0.15), rgba(200,0,0,0.3)) !important;
            border: 1px solid #ff3355 !important;
            color: #ff3355 !important;
            box-shadow: 0 0 15px rgba(255,51,85,0.2) !important;
            width: 100% !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, rgba(255,0,0,0.3), rgba(255,51,85,0.5)) !important;
            box-shadow: 0 0 30px rgba(255,51,85,0.5) !important;
            border-color: #ff0000 !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
        }
        </style>
        <div style='margin-top:15px;'></div>
        """, unsafe_allow_html=True)
        
        _, btn_col, _ = st.columns([1, 1.5, 1])
        with btn_col:
            authenticator.logout("⏻   ABORT", "main")

    # ── CENTER: GLOBE ──────────────────────────────────────────────────────
    with globe_col:
        globe_html = build_globe_html(
            earthquakes=earthquakes, weather=weather, iss=iss,
            flights=flights, satellites=satellites, countries_db=countries_db,
            gdp_data=gdp_data, cyber_arcs=cyber_arcs, emergencies=emergencies,
            show_seismic=show_seismic, show_weather=show_weather,
            show_satellites=show_satellites, show_flights=show_flights,
            show_shipping=show_shipping, 
            show_cyber=show_cyber,
            show_emergencies=show_emergencies,
            global_events=global_events,
            volcanoes=volcanoes,
            fires=fires,
            disasters=disasters,
            ships=ships,
            show_conflicts=show_conflicts,
            show_fires=show_fires,
            show_volcanoes=show_volcanoes,
            show_disasters=show_disasters,
            show_population=True,
            globe_w=1000, globe_h=780,
        )
        st.components.v1.html(globe_html, height=800, scrolling=False)

        # ── FINANCIAL DATA CONTROLS ──
        financial_data = fetch_financials()
        if financial_data:
            st.markdown('<div class="panel-card panel-card-cyan" style="margin-top: 15px; margin-bottom: 10px; width: 100%; padding: 4px 10px;"><div class="panel-title" style="color:#00f0ff; font-size: 0.75rem; text-align: center;">◆ GLOBAL MARKETS & COMMODITIES</div></div>', unsafe_allow_html=True)
            cols = st.columns(len(financial_data))
            for i, item in enumerate(financial_data):
                with cols[i]:
                    up = item['change'] >= 0
                    color = "#00ff88" if up else "#ff3355"
                    sign = "+" if up else ""
                    arrow = "▲" if up else "▼"
                    
                    st.markdown(f'''
                    <div class="intel-item" style="border-left:3px solid {color}88; text-align: center; padding: 12px 6px; background: linear-gradient(145deg, rgba(0,20,50,0.6), rgba(0,8,25,0.85)); border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5), inset 0 1px 0 rgba(0,240,255,0.1);">
                        <div style="color:rgba(0,240,255,0.7); font-size:0.55rem; letter-spacing:1px; font-weight:700; margin-bottom: 6px; text-transform: uppercase;">{item["name"]}</div>
                        <div style="color:#e0f7ff; font-size:0.85rem; font-weight:800; font-family:'Orbitron',sans-serif; text-shadow: 0 0 12px {color}44; margin-bottom: 2px;">{item["price"]:,.2f}</div>
                        <div style="color:{color}; font-size:0.6rem; font-weight:700; letter-spacing: 0.5px;">{arrow} {sign}{item["change"]:,.2f} ({sign}{item["pct"]:.2f}%)</div>
                    </div>
                    ''', unsafe_allow_html=True)

        # ── GLOBAL NEWS FEED ──
        news_data = fetch_global_news()
        if news_data:
            st.markdown('<div class="panel-card panel-card-orange" style="margin-top: 15px; margin-bottom: 10px; width: 100%; padding: 4px 10px;"><div class="panel-title" style="color:#ff6600; font-size: 0.75rem; text-align: center;">◆ LiVE NEWS FEED</div></div>', unsafe_allow_html=True)
            news_cols = st.columns(len(news_data))
            for i, item in enumerate(news_data):
                with news_cols[i]:
                    c = item['color']
                    st.markdown(f'''
                    <div class="intel-item" style="border-left:3px solid {c}88; padding: 8px 8px; background: linear-gradient(145deg, rgba(0,8,25,0.7), rgba(0,4,15,0.9)); border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.6), inset 0 1px 0 {c}33; height: 120px; overflow: hidden; display: flex; flex-direction: column;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px; border-bottom: 1px solid {c}33; padding-bottom: 4px; flex-shrink: 0;">
                            <span style="color:rgba(0,240,255,0.8); font-size: 0.55rem; font-weight: 700; letter-spacing: 1px;">{item["location"]}</span>
                            <span style="color:{c}; font-size: 0.5rem; font-weight: 800; letter-spacing: 0.5px; text-shadow: 0 0 5px {c}88;">{item["tag"]}</span>
                        </div>
                        <div style="color:#e0f7ff; font-size: 0.65rem; font-weight: 500; line-height: 1.35; font-family: 'Rajdhani', sans-serif; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical;">{item["title"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)

    # ── RIGHT PANEL: Intelligence Feed ─────────────────────────────────────
    with right_col:

        # Global Conflicts
        st.markdown('<div class="panel-card panel-card-red"><div class="panel-title" style="color:#ff3355;">◆ LIVE CONFLICTS</div></div>', unsafe_allow_html=True)
        if global_events:
            # Filter high-severity conflicts
            high_conflicts = [e for e in global_events if e.get("category") in ["acled", "ucdp"] or e.get("color") == "#ff0000"][:5]
            for ev in high_conflicts:
                severity = "CRITICAL" if ev.get("color") == "#ff0000" else "HIGH"
                sev_color = "#ff0000" if severity == "CRITICAL" else "#ff4400"
                st.markdown(f'<div class="intel-item" style="border-left:3px solid {sev_color}44;"><span style="color:{sev_color};font-weight:700;font-family:\'Orbitron\',sans-serif;font-size:0.6rem;">● {severity}</span><span style="color:rgba(0,240,255,0.55);"> {ev.get("label","Event")[:28]}</span></div>', unsafe_allow_html=True)

        # Volcanoes
        st.markdown('<div class="panel-card panel-card-orange"><div class="panel-title" style="color:#ff6600;">◆ ACTIVE VOLCANOES</div></div>', unsafe_allow_html=True)
        erupting = [v for v in volcanoes if "erupt" in v.get("status", "").lower()]
        others = [x for x in volcanoes if "erupt" not in x.get("status", "").lower()]
        combined_volcanoes = (erupting + others)[:5]
        for v in combined_volcanoes:
            if "erupt" in v.get("status", "").lower():
                st.markdown(f'<div class="intel-item" style="border-left:3px solid rgba(255,68,0,0.5);"><span style="color:#ff4400;font-weight:700;">🔴 ERUPTING</span><span style="color:rgba(0,240,255,0.55);"> {v["name"][:25]}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="intel-item" style="border-left:3px solid rgba(255,136,0,0.4);"><span style="color:#ff8800;font-weight:600;">🟠 {v.get("status","Active")}</span><span style="color:rgba(0,240,255,0.55);"> {v["name"][:22]}</span></div>', unsafe_allow_html=True)

        # Seismic
        st.markdown('<div class="panel-card panel-card-orange"><div class="panel-title" style="color:#ff3355;">◆ SEISMIC INFORMATION</div></div>', unsafe_allow_html=True)
        if earthquakes:
            top_q = sorted(earthquakes, key=lambda x: x["mag"], reverse=True)[:5]
            for q in top_q:
                mc = "#ff1133" if q["mag"]>=5 else "#ff6600" if q["mag"]>=4 else "#ffcc00"
                st.markdown(f'<div class="intel-item" style="border-left:3px solid {mc}44;"><span style="color:{mc};font-weight:700;font-family:\'Orbitron\',sans-serif;font-size:0.6rem;">M{q["mag"]:.1f}</span><span style="color:rgba(0,240,255,0.55);"> {q["place"][:28]}</span></div>', unsafe_allow_html=True)

        # Wildfires
        st.markdown('<div class="panel-card panel-card-red"><div class="panel-title" style="color:#ff2200;">◆ ACTIVE WILDFIRES</div></div>', unsafe_allow_html=True)
        for f in fires[:5]:
            st.markdown(f'<div class="intel-item" style="border-left:3px solid rgba(255,34,0,0.5);"><span style="color:#ff2200;font-weight:600;">🔥</span><span style="color:rgba(0,240,255,0.55);"> {f["name"][:28]}</span></div>', unsafe_allow_html=True)

        # Emergency Alerts
        st.markdown('<div class="panel-card panel-card-red"><div class="panel-title" style="color:#ff6600;">◆ EMERGENCY ALERTS</div></div>', unsafe_allow_html=True)
        for e in [x for x in emergencies if x["severity"]=="high"][:4]:
            st.markdown(f'<div class="intel-item" style="border-left:3px solid rgba(255,51,0,0.4);"><span style="color:#ff3300;font-weight:700;font-size:0.58rem;">● HIGH</span><span style="color:rgba(0,240,255,0.55);font-size:0.58rem;"> {e["name"][:28]}</span></div>', unsafe_allow_html=True)

        v = iss.get("velocity", 27600)
        a = iss.get("altitude", 420)
        loc = iss.get("location", "Over Ocean")
        st.markdown(f"""
        <div class="panel-card panel-card-purple" style="margin-top:10px; padding-bottom: 25px; padding-top: 15px;">
            <div class="panel-title" style="color:#ff00ff; font-size: 0.65rem; margin-bottom: 12px; letter-spacing: 3px;">◆ ISS COORDINATES</div>
            <div style="font-size:0.6rem;color:rgba(0,240,255,0.7);margin-top:5px;">
                <div style="display:flex;justify-content:space-between; padding: 4px 0; border-bottom: 1px solid rgba(191,0,255,0.2);"><span>Latitude</span><span style="color:#ff00ff;font-weight:600;">{iss['lat']:.4f}°</span></div>
                <div style="display:flex;justify-content:space-between; padding: 4px 0; border-bottom: 1px solid rgba(191,0,255,0.2);"><span>Longitude</span><span style="color:#ff00ff;font-weight:600;">{iss['lng']:.4f}°</span></div>
                <div style="display:flex;justify-content:space-between; padding: 4px 0; border-bottom: 1px solid rgba(191,0,255,0.2);"><span>Orbital Velocity</span><span style="color:#00ff88;font-weight:600;">{v:,.0f} km/h</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    # ═══════════════════════════════════════════════════════════════════════════
    # Bottom Stats Bar
    # ═══════════════════════════════════════════════════════════════════════════
    total_pop = sum(c["population"] for c in countries_db.values())
    total_gdp = sum(gdp_data.values())
    avg_temp = sum(w["temp"] for w in weather) / len(weather) if weather else 0
    max_quake = max((q["mag"] for q in earthquakes), default=0)

    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value" style="color:#ff0033;">{len(global_events)}</div>
            <div class="stat-label">LIVE EVENTS</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:#ff3355;">{len(earthquakes)}</div>
            <div class="stat-label">SEISMIC EVENTS</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:#ff4400;">{len(volcanoes)}</div>
            <div class="stat-label">LIVE VOLCANOES</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:#ff2200;">{len(fires)}</div>
            <div class="stat-label">ACTIVE WILDFIRES</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:#ff6600;">{len(flights)}</div>
            <div class="stat-label">FLIGHTS</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:#00ccdd;">{len(ships)}</div>
            <div class="stat-label">ON-ROUTE VESSELS</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:#00ff88;">{len(satellites)+1}</div>
            <div class="stat-label">ORBITAL OBJECTS</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:#ff00ff;">{astro_count}</div>
            <div class="stat-label">IN SPACE</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:#00ccff;">{avg_temp:.1f}°C</div>
            <div class="stat-label">AVG TEMP</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:#bf00ff;">${total_gdp/1e12:.1f}T</div>
            <div class="stat-label">WORLD GDP</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;padding:4px 0 2px;font-family:'Share Tech Mono',monospace;font-size:0.48rem;color:rgba(0,240,255,0.1);letter-spacing:2.5px;">
        God's Eye View · {now.strftime('%Y')} · CANT FEAR YOUR OWN WORLD ·
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ── LOGIN FAILED ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
elif auth_status is False:
    st.markdown("""
    <div class="login-splash">
        <h2>God's Eye View</h2>
        <p>Welcome to the terminal</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-top:1.2rem;">
        <span style="color:#ff3355;font-family:'Orbitron',sans-serif;font-size:0.85rem;letter-spacing:2px;text-shadow:0 0 15px rgba(255,51,85,0.4);">
            ⚠ ACCESS DENIED — INVALID CREDENTIALS
        </span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ── LOGIN SCREEN ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div class="login-splash">
        <h2>God's Eye View</h2>
        <p>Welcome to the terminal</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-top:1rem;margin-bottom:0.5rem;">
        <span style="color:rgba(0,240,255,0.25);font-family:'Share Tech Mono',monospace;font-size:0.7rem;letter-spacing:3px;">
            SECURE ACCESS · ENTER CREDENTIALS
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="position:fixed;bottom:20px;left:0;width:100%;text-align:center;font-family:'Share Tech Mono',monospace;font-size:0.55rem;color:rgba(0,240,255,0.12);letter-spacing:4px;">
        UNAUTHORIZED ACCESS IS STRICTLY PROHIBITED
    </div>
    <style>
        @keyframes scanline { 0% { top: -5%; } 100% { top: 105%; } }
        .scanline { position: fixed; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, rgba(0,240,255,0.06), transparent); animation: scanline 8s linear infinite; pointer-events: none; z-index: 9999; }
    </style>
    <div class="scanline"></div>
    """, unsafe_allow_html=True)

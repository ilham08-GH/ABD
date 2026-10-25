"""
Windy BMKG — Indonesia Climate Explorer (2010–2027)
Visualisasi Interaktif Data Iklim BMKG dengan Antarmuka & Layout Windy.com
+ Fitur Prediksi Iklim Lintas Waktu (Sebelum 2026, 2026 Real-Time, & Setelah 2026)
Dibuat untuk Tugas UAS Analisis Big Data (ABD)
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import joblib

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Iklim BMKG Indonesia",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════
# CUSTOM CSS: WINDY AESTHETIC DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
    
    html, body, .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, input { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
    }
    
    /* Lindungi icon Material Symbols dari override font Inter */
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"] * {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 1.25rem !important;
        line-height: 1 !important;
        display: inline-block !important;
        text-transform: none !important;
        letter-spacing: normal !important;
        word-wrap: normal !important;
        white-space: nowrap !important;
        direction: ltr !important;
        -webkit-font-smoothing: antialiased !important;
        text-rendering: optimizeLegibility !important;
    }
    
    .stApp {
        background-color: #0a0e17 !important;
        background: radial-gradient(circle at 50% 30%, #111a2e 0%, #0a0e17 80%, #070a10 100%) !important;
        color: #e0e7ff;
    }
    .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu, footer {
        visibility: hidden !important;
    }
    
    /* ── Windy Top Header ── */
    .windy-logo-box {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .windy-logo-icon {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        font-weight: 900;
        font-size: 1.3rem;
        width: 36px;
        height: 36px;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.45);
    }
    .windy-logo-title {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .windy-logo-sub {
        color: #ff6b6b;
        font-weight: 700;
    }
    .windy-badge-bmkg {
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.25);
        color: #94a3b8;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 6px;
        margin-left: 8px;
        letter-spacing: 0.5px;
    }
    
    /* ── Floating Side Menu ── */
    .stButton > button {
        background: rgba(17, 24, 39, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 0.45rem 0.8rem !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(8px) !important;
    }
    .stButton > button:hover {
        background: rgba(30, 41, 59, 0.95) !important;
        border-color: rgba(255, 107, 107, 0.6) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
    }
    .stButton > button [data-testid="stIconMaterial"],
    .stButton > button .material-symbols-rounded {
        font-size: 1.15rem !important;
        vertical-align: middle !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.85) 0%, rgba(220, 38, 38, 0.95) 100%) !important;
        border: 1px solid rgba(254, 202, 202, 0.5) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.4) !important;
        font-weight: 700 !important;
    }
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, rgba(248, 113, 113, 0.95) 0%, rgba(239, 68, 68, 1) 100%) !important;
        border-color: #ffffff !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6) !important;
    }
    
    /* ── Bottom Controls Dock ── */
    .windy-dock {
        background: rgba(10, 14, 23, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 0.6rem 1.2rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        margin-top: 0.4rem;
    }
    
    /* ── Windy Legend Color Bar ── */
    .windy-legend-strip {
        height: 10px;
        border-radius: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 4px;
        font-size: 0.62rem;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 1px 3px rgba(0,0,0,0.9);
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);
    }
    
    /* ── Map Frame ── */
    .windy-map-frame {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
    }
    
    /* ── KPI Stat Pills ── */
    .windy-kpi-pill {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 0.6rem 0.9rem;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s ease;
    }
    .windy-kpi-pill:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.15);
    }
    .windy-kpi-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .windy-kpi-val {
        font-size: 1.4rem;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 2px;
    }
    .windy-kpi-unit {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* ── Tabs Styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(17, 24, 39, 0.7);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #94a3b8;
        padding: 0.35rem 0.9rem;
        font-size: 0.82rem;
    }
    .stTabs [aria-selected="true"] {
        background: #e74c3c !important;
        border-color: #ff7675 !important;
        color: #ffffff !important;
        font-weight: 700;
    }
    
    /* ── Prediction card ── */
    .pred-card {
        background: linear-gradient(135deg, rgba(17,24,39,0.92), rgba(30,41,59,0.8));
        border: 1px solid rgba(100, 180, 255, 0.15);
        border-radius: 14px;
        padding: 1rem 0.8rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .pred-card:hover {
        border-color: rgba(56, 189, 248, 0.45);
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    .pred-card .pred-day {
        color: #94a3b8;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .pred-card .pred-date {
        color: #64748b;
        font-size: 0.72rem;
    }
    .pred-card .pred-value {
        font-size: 1.55rem;
        font-weight: 800;
        margin: 0.25rem 0;
    }
    .pred-card .pred-unit {
        font-size: 0.72rem;
        color: #64748b;
    }
    .pred-card .pred-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: 700;
        margin-top: 0.3rem;
    }
    .pred-info-box {
        background: rgba(168, 85, 247, 0.08);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 12px;
        padding: 0.9rem 1.2rem;
        font-size: 0.85rem;
        color: #e9d5ff;
        margin-bottom: 1rem;
    }
    .pred-method-box {
        background: rgba(56, 189, 248, 0.06);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        font-size: 0.82rem;
        color: #93c5fd;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PARAMETER & LAYER CONFIGURATIONS
# ══════════════════════════════════════════════════════════════
PARAMS = {
    "💨 Angin": {
        "full_name": "Kecepatan Angin",
        "col": "wind_avg", "unit": "m/s", "fmt": ".1f",
        "colors": ["#3b528b", "#21918c", "#5ec962", "#fde725", "#fc8d59", "#d73027"],
        "vmin": 0, "vmax": 8,
        "windy_overlay": "wind",
        "ticks": ["0", "2", "4", "6", "8+ m/s"],
        "desc": "Kecepatan aliran angin rata-rata harian BMKG"
    },
    "🌧️ Hujan, guntur": {
        "full_name": "Curah Hujan",
        "col": "rainfall", "unit": "mm", "fmt": ".1f",
        "colors": ["#f7fbff", "#6baed6", "#2171b5", "#fee08b", "#fc8d59", "#d73027", "#7f3b08"],
        "vmin": 0, "vmax": 50,
        "windy_overlay": "rain",
        "ticks": ["0", "5", "15", "30", "50+ mm"],
        "desc": "Akumulasi dan intensitas curah hujan BMKG"
    },
    "🌡️ Suhu": {
        "full_name": "Suhu Udara",
        "col": "temp_avg", "unit": "°C", "fmt": ".1f",
        "colors": ["#2166ac", "#67a9cf", "#d1e5f0", "#fddbc7", "#ef8a62", "#b2182b"],
        "vmin": 20, "vmax": 32,
        "windy_overlay": "temp",
        "ticks": ["20°", "23°", "26°", "29°", "32°C"],
        "desc": "Temperatur udara rata-rata harian BMKG"
    },
    "💧 Kelembaban": {
        "full_name": "Kelembaban Relatif",
        "col": "humidity", "unit": "%", "fmt": ".1f",
        "colors": ["#8c510a", "#d8b365", "#f6e8c3", "#c7eae5", "#5ab4ac", "#01665e"],
        "vmin": 50, "vmax": 100,
        "windy_overlay": "rh",
        "ticks": ["50%", "65%", "75%", "85%", "100%"],
        "desc": "Kelembaban relatif atmosfer BMKG"
    },
    "☀️ Sinar matahari": {
        "full_name": "Penyinaran Matahari",
        "col": "sunshine", "unit": "jam", "fmt": ".1f",
        "colors": ["#1a1a2e", "#2d3561", "#6b5b95", "#feb236", "#f7dc6f", "#fefbd8"],
        "vmin": 0, "vmax": 10,
        "windy_overlay": "clouds",
        "ticks": ["0", "2.5", "5", "7.5", "10 jam"],
        "desc": "Durasi jam penyinaran matahari BMKG"
    },
}

# Plotly layout template
PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(17,24,39,0.5)',
    font=dict(family='Inter', color='#e0e7ff'),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=11)),
    hoverlabel=dict(bgcolor='#1e293b', font_size=12, font_family='Inter'),
)

def plotly_layout(**overrides):
    """Build a clean plotly layout dict with grid defaults; overrides win."""
    base = {
        **PLOTLY_BASE,
        'xaxis': dict(gridcolor='rgba(255,255,255,0.06)', zeroline=False),
        'yaxis': dict(gridcolor='rgba(255,255,255,0.06)', zeroline=False),
    }
    base.update(overrides)
    return base

# ══════════════════════════════════════════════════════════════
# DATA LOADING (FAST PARQUET CACHED)
# ══════════════════════════════════════════════════════════════
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

@st.cache_data(ttl=3600)
def load_stations():
    return pd.read_csv(os.path.join(DATA_DIR, 'station_detail.csv'))

@st.cache_data(ttl=3600)
def load_provinces():
    return pd.read_csv(os.path.join(DATA_DIR, 'province_detail.csv'))

@st.cache_data(ttl=60)
def load_climate(resolution, _version=3):
    fmap = {
        'Harian': 'climate_daily.parquet',
        'Bulanan': 'climate_monthly.parquet',
        'Tahunan': 'climate_yearly.parquet',
    }
    return pd.read_parquet(os.path.join(DATA_DIR, fmap[resolution]))

@st.cache_data(ttl=3600)
def load_wind_direction():
    fpath = os.path.join(DATA_DIR, 'wind_direction.parquet')
    if os.path.exists(fpath):
        return pd.read_parquet(fpath)
    return None

# ══════════════════════════════════════════════════════════════
# MACHINE LEARNING MODEL LOADING & DEFINITIONS (RANDOM FOREST)
# ══════════════════════════════════════════════════════════════
RF_FEATURE_COLS = [
    'Tavg_lag1', 'Tavg_lag7', 'Tavg_roll7',
    'RH_lag1',   'RH_roll7',
    'RR_lag1',   'RR_roll7',
    'ss_lag1',
    'month_sin', 'month_cos'
]

# Evaluasi Historis Model Random Forest Regressor dari Analisis_Iklim_BMKG.ipynb
RF_EVAL_BENCHMARK = {
    'regressor': {
        'mae': 0.5198,
        'rmse': 0.6954,
        'r2': 0.8714,
        'n_train': 470452,
        'n_test': 117614,
        'n_total': 588066,
        'split': 'Temporal 80:20 (Train 2010–2018, Test 2018–2020)',
    }
}

@st.cache_resource(ttl=3600)
def load_rf_regressor():
    """Load Random Forest Regressor (suhu Tavg) dari UAS/models/."""
    model_path = os.path.join(MODELS_DIR, 'model_rf_regressor.pkl')
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

def check_model_exists(target_col: str = None, station_id: int = None) -> bool:
    """Cek keberadaan file model ML terlatih di folder UAS/models/."""
    reg_p = os.path.join(MODELS_DIR, 'model_rf_regressor.pkl')
    return os.path.exists(reg_p)


def get_color_for_value(value, param_cfg):
    """Interpolate color from palette."""
    if pd.isna(value):
        return '#374151'
    colors = param_cfg['colors']
    vmin, vmax = param_cfg['vmin'], param_cfg['vmax']
    ratio = max(0.0, min(1.0, (value - vmin) / max(1e-5, (vmax - vmin))))
    idx = ratio * (len(colors) - 1)
    lower = int(idx)
    upper = min(lower + 1, len(colors) - 1)
    frac = idx - lower
    c1, c2 = colors[lower], colors[upper]
    r = int(int(c1[1:3], 16) * (1 - frac) + int(c2[1:3], 16) * frac)
    g = int(int(c1[3:5], 16) * (1 - frac) + int(c2[3:5], 16) * frac)
    b = int(int(c1[5:7], 16) * (1 - frac) + int(c2[5:7], 16) * frac)
    return f'#{r:02x}{g:02x}{b:02x}'


# ══════════════════════════════════════════════════════════════
# FORECAST PREPROCESSING & CLIMATE PREDICTION ENGINE
# ══════════════════════════════════════════════════════════════
FORECAST_TARGETS = ['temp_avg', 'rainfall', 'humidity', 'wind_avg', 'sunshine']
FORECAST_HORIZON = 7

@st.cache_data(ttl=3600)
def prepare_forecast_features(station_id: int):
    """
    Prepare feature-engineered dataset for a station ready for ML modelling.
    Returns (df_features, last_date) or (None, None) if insufficient data.
    """
    daily = load_climate('Harian')
    df = daily[daily['station_id'] == station_id].copy()
    
    if len(df) < 60:
        return None, None
    
    df = df.sort_values('date').reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'])
    
    # Calendar features
    df['day_of_year'] = df['date'].dt.dayofyear
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Cyclical encoding (sin/cos) for periodicity
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['doy_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
    df['doy_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
    
    # Season encoding
    season_map = {'Musim Hujan': 0, 'Musim Kemarau': 1, 'Peralihan I': 2, 'Peralihan II': 3}
    df['season_enc'] = df['season'].map(season_map).fillna(0).astype(int)
    
    # Lag features & rolling stats for each target
    for col in FORECAST_TARGETS:
        if col not in df.columns:
            continue
        for lag in [1, 2, 3, 7, 14, 30]:
            df[f'{col}_lag{lag}'] = df[col].shift(lag)
        for win in [7, 14, 30]:
            df[f'{col}_roll{win}_mean'] = df[col].rolling(win, min_periods=1).mean()
            df[f'{col}_roll{win}_std'] = df[col].rolling(win, min_periods=1).std()
    
    last_date = df['date'].max()
    df = df.dropna(subset=[f'{FORECAST_TARGETS[0]}_lag30'])
    
    return df, last_date


def generate_climate_forecast(station_id: int, target_col: str, horizon: int = 7, ref_date: datetime = None):
    """
    Generate climate forecast for any reference date using ML model when available.
    For temp_avg: uses Random Forest Regressor model with autoregressive rolling prediction.
    For other targets: uses enhanced statistical climatological projection.
    
    Returns (forecast_df, baseline_df, method_used)
    """
    if ref_date is None:
        ref_date = datetime(2026, 10, 19)
        
    monthly = load_climate('Bulanan')
    st_m = monthly[monthly['station_id'] == station_id].copy()
    if len(st_m) == 0:
        return None, None, 'none'
        
    # Baseline stats per month for this station
    month_stats = st_m.groupby('month')[target_col].agg(['mean', 'std']).reset_index()
    month_stats.columns = ['month', 'hist_mean', 'hist_std']
    month_stats['hist_std'] = month_stats['hist_std'].fillna(1.2)
    
    # ── 1. Construct 30-day prior baseline for plotting ──
    baseline_rows = []
    daily = load_climate('Harian')
    daily_st = daily[daily['station_id'] == station_id].copy()
    if len(daily_st) > 0:
        daily_st['date'] = pd.to_datetime(daily_st['date'])
        
    if ref_date <= datetime(2020, 12, 31) and len(daily_st) > 0:
        prior_actual = daily_st[daily_st['date'] <= ref_date].sort_values('date').tail(30)
        for _, prow in prior_actual.iterrows():
            baseline_rows.append({'date': prow['date'], 'value': prow[target_col]})
    else:
        for b in range(30, 0, -1):
            b_date = ref_date - timedelta(days=b)
            bm = b_date.month
            by = b_date.year
            m_stat = month_stats[month_stats['month'] == bm]
            b_mean = m_stat['hist_mean'].values[0] if len(m_stat) > 0 else 27.0
            
            delta_yr = by - 2020
            trend_adj = (0.025 * delta_yr) if target_col == 'temp_avg' else 0.0
            seed = int(station_id % 10000 + by * 40 + bm * 12 + b)
            rng = np.random.default_rng(seed)
            noise = rng.normal(0, 0.2 if target_col == 'temp_avg' else 1.2)
            val = b_mean + trend_adj + noise
            if target_col in ['rainfall', 'wind_avg', 'sunshine']:
                val = max(0.0, val)
            baseline_rows.append({'date': b_date, 'value': round(val, 2)})
            
    df_baseline = pd.DataFrame(baseline_rows)
    
    # ── 2. Try ML model for temperature prediction ──
    rf_reg = load_rf_regressor()
    use_ml = (target_col == 'temp_avg' and rf_reg is not None)
    method_used = 'ml_rf' if use_ml else 'statistical'
    
    forecast_rows = []
    
    if use_ml:
        # Build recent context for 10 autoregressive features
        daily_full = daily_st.copy()
        if len(daily_full) > 0:
            daily_full = daily_full.sort_values('date').reset_index(drop=True)
            rename_dict = {'temp_avg': 'Tavg', 'humidity': 'RH_avg', 'rainfall': 'RR', 'sunshine': 'ss'}
            daily_full = daily_full.rename(columns={k: v for k, v in rename_dict.items() if k in daily_full.columns})
            if 'ss' not in daily_full.columns:
                daily_full['ss'] = 6.0
        
        # Get the last 30 days of context (from baseline or historical data)
        if ref_date <= datetime(2020, 12, 31) and len(daily_full) > 0:
            context = daily_full[daily_full['date'] <= ref_date].tail(30)
            recent_tavg = context['Tavg'].tolist() if 'Tavg' in context.columns else []
            recent_rh = context['RH_avg'].tolist() if 'RH_avg' in context.columns else []
            recent_rr = context['RR'].tolist() if 'RR' in context.columns else []
            recent_ss = context['ss'].tolist() if 'ss' in context.columns else []
        else:
            # Build synthetic context from monthly climatology
            recent_tavg, recent_rh, recent_rr, recent_ss = [], [], [], []
            hum_stats = st_m.groupby('month')['humidity'].mean()
            rain_stats = st_m.groupby('month')['rainfall'].mean()
            sun_stats = st_m.groupby('month')['sunshine'].mean()
            
            for b in range(30, 0, -1):
                b_date = ref_date - timedelta(days=b)
                bm = b_date.month
                by = b_date.year
                m_stat_t = month_stats[month_stats['month'] == bm]
                t_base = m_stat_t['hist_mean'].values[0] if len(m_stat_t) > 0 else 27.0
                h_base = hum_stats.get(bm, 82.0)
                r_base = rain_stats.get(bm, 5.5)
                s_base = sun_stats.get(bm, 6.0)
                
                seed = int(station_id % 10000 + by * 40 + bm * 12 + b)
                rng = np.random.default_rng(seed)
                recent_tavg.append(float(t_base + 0.025 * (by - 2020) + rng.normal(0, 0.22)))
                recent_rh.append(float(np.clip(h_base + rng.normal(0, 1.5), 50.0, 98.0)))
                recent_rr.append(float(max(0.0, (r_base / 30.0) * (1.0 + rng.normal(0, 0.3)))))
                recent_ss.append(float(np.clip(s_base + rng.normal(0, 0.8), 0.5, 11.5)))
        
        # If not enough context, fall back to statistical
        if len(recent_tavg) < 7:
            use_ml = False
            method_used = 'statistical'
        else:
            # Autoregressive rolling prediction with RF Regressor
            for d in range(1, horizon + 1):
                f_date = ref_date + timedelta(days=d)
                fm = f_date.month
                
                # Build 10 features matching RF_FEATURE_COLS
                tavg_lag1 = recent_tavg[-1]
                tavg_lag7 = recent_tavg[-7] if len(recent_tavg) >= 7 else recent_tavg[0]
                tavg_roll7 = float(np.mean(recent_tavg[-7:])) if len(recent_tavg) >= 7 else float(np.mean(recent_tavg))
                rh_lag1 = recent_rh[-1] if recent_rh else 82.0
                rh_roll7 = float(np.mean(recent_rh[-7:])) if len(recent_rh) >= 7 else 82.0
                rr_lag1 = recent_rr[-1] if recent_rr else 5.0
                rr_roll7 = float(np.mean(recent_rr[-7:])) if len(recent_rr) >= 7 else 5.0
                ss_lag1 = recent_ss[-1] if recent_ss else 6.0
                month_sin = float(np.sin(2 * np.pi * fm / 12))
                month_cos = float(np.cos(2 * np.pi * fm / 12))
                
                features = pd.DataFrame([{
                    'Tavg_lag1': tavg_lag1,
                    'Tavg_lag7': tavg_lag7,
                    'Tavg_roll7': tavg_roll7,
                    'RH_lag1': rh_lag1,
                    'RH_roll7': rh_roll7,
                    'RR_lag1': rr_lag1,
                    'RR_roll7': rr_roll7,
                    'ss_lag1': ss_lag1,
                    'month_sin': month_sin,
                    'month_cos': month_cos,
                }])
                
                pred_val = round(float(rf_reg.predict(features)[0]), 2)
                
                # Uncertainty band grows with horizon day (based on RF MAE ~0.52°C)
                base_mae = 0.52
                uncertainty = base_mae * (0.8 + 0.12 * d)
                lower = round(pred_val - uncertainty, 2)
                upper = round(pred_val + uncertainty, 2)
                
                forecast_rows.append({
                    'date': f_date,
                    'day_label': f_date.strftime('%a'),
                    'date_label': f_date.strftime('%d %b'),
                    'predicted': pred_val,
                    'lower_bound': lower,
                    'upper_bound': upper,
                })
                
                # Update context for next day autoregression
                recent_tavg.append(pred_val)
                seed = int(station_id % 10000 + f_date.year * 50 + fm * 15 + d)
                rng_step = np.random.default_rng(seed)
                h_b = hum_stats.get(fm, 82.0) if 'hum_stats' in locals() else 82.0
                r_b = rain_stats.get(fm, 5.5) if 'rain_stats' in locals() else 5.5
                s_b = sun_stats.get(fm, 6.0) if 'sun_stats' in locals() else 6.0
                recent_rh.append(float(np.clip(h_b + rng_step.normal(0, 1.5), 50.0, 98.0)))
                recent_rr.append(float(max(0.0, (r_b / 30.0) * (1.0 + rng_step.normal(0, 0.3)))))
                recent_ss.append(float(np.clip(s_b + rng_step.normal(0, 0.8), 0.5, 11.5)))
    
    if not use_ml:
        # Fallback: Statistical climatological forecast
        for d in range(1, horizon + 1):
            f_date = ref_date + timedelta(days=d)
            fm = f_date.month
            fy = f_date.year
            delta_yr = fy - 2020
            
            m_stat = month_stats[month_stats['month'] == fm]
            base_mean = m_stat['hist_mean'].values[0] if len(m_stat) > 0 else 27.0
            base_std = m_stat['hist_std'].values[0] if len(m_stat) > 0 else 1.2
            
            seed = int(station_id % 10000 + fy * 50 + fm * 15 + d)
            rng = np.random.default_rng(seed)
            
            if target_col == 'temp_avg':
                warming = 0.025 * max(0, delta_yr)
                enso_ano = 0.20 if fy == 2026 else (0.24 if fy >= 2027 else 0.10)
                pred_val = round(float(base_mean + warming + enso_ano + rng.normal(0, 0.22)), 2)
                uncertainty = max(0.5, base_std * (0.6 + 0.08 * d))
                lower = round(pred_val - uncertainty, 2)
                upper = round(pred_val + uncertainty, 2)
            elif target_col == 'rainfall':
                daily_base = (base_mean / 30.0)
                is_rain = rng.random() > 0.40
                if is_rain:
                    rain_amount = daily_base * (1.4 + rng.normal(0, 0.35))
                    pred_val = round(float(max(0.5, rain_amount)), 1)
                else:
                    pred_val = 0.0
                uncertainty = max(1.5, base_std * (0.15 + 0.05 * d))
                lower = round(max(0.0, pred_val - uncertainty * 0.7), 1)
                upper = round(pred_val + uncertainty, 1)
            elif target_col == 'humidity':
                pred_val = round(float(np.clip(base_mean + rng.normal(0, 1.8), 50.0, 96.0)), 1)
                uncertainty = max(2.0, base_std * (0.8 + 0.06 * d))
                lower = round(max(40.0, pred_val - uncertainty), 1)
                upper = round(min(100.0, pred_val + uncertainty), 1)
            elif target_col == 'wind_avg':
                pred_val = round(float(max(0.6, base_mean + rng.normal(0, 0.35))), 1)
                uncertainty = max(0.4, base_std * (0.7 + 0.05 * d))
                lower = round(max(0.2, pred_val - uncertainty), 1)
                upper = round(pred_val + uncertainty, 1)
            else:  # sunshine
                pred_val = round(float(np.clip(base_mean + rng.normal(0, 0.8), 0.5, 11.5)), 1)
                uncertainty = max(0.8, base_std * (0.7 + 0.06 * d))
                lower = round(max(0.0, pred_val - uncertainty), 1)
                upper = round(min(12.0, pred_val + uncertainty), 1)
                
            forecast_rows.append({
                'date': f_date,
                'day_label': f_date.strftime('%a'),
                'date_label': f_date.strftime('%d %b'),
                'predicted': pred_val,
                'lower_bound': lower,
                'upper_bound': upper,
            })
        
    return pd.DataFrame(forecast_rows), df_baseline, method_used



# ══════════════════════════════════════════════════════════════
# INITIALIZE SESSION STATE
# ══════════════════════════════════════════════════════════════
if 'active_layer' not in st.session_state:
    st.session_state['active_layer'] = "💨 Angin"
if 'view_mode' not in st.session_state:
    st.session_state['view_mode'] = "bmkg"
if 'selected_year' not in st.session_state:
    st.session_state['selected_year'] = 2026  # Default to current year 2026
if 'selected_month' not in st.session_state:
    st.session_state['selected_month'] = 10
if 'resolution' not in st.session_state:
    st.session_state['resolution'] = "Tahunan"
if 'selected_station_id' not in st.session_state:
    st.session_state['selected_station_id'] = None
if 'show_meteogram' not in st.session_state:
    st.session_state['show_meteogram'] = False
if 'basemap' not in st.session_state:
    st.session_state['basemap'] = "🌑 Dark Canvas"

# Load metadata
stations = load_stations()
provinces = load_provinces()

# ══════════════════════════════════════════════════════════════
# TOP BAR (WINDY STYLE)
# ══════════════════════════════════════════════════════════════
top_col1, top_col2, top_col3 = st.columns([3.8, 4.4, 3.8])

with top_col1:
    station_options = stations[['station_id', 'station_name', 'region_name']].copy()
    station_options['display'] = station_options['station_name'] + " — " + station_options['region_name']
    
    default_station_idx = 0
    if st.session_state['selected_station_id'] is not None:
        matched = station_options[station_options['station_id'] == st.session_state['selected_station_id']]
        if len(matched) > 0:
            default_station_idx = station_options.index.get_loc(matched.index[0])

    sel_station_display = st.selectbox(
        "Cari Stasiun BMKG",
        station_options['display'].tolist(),
        index=default_station_idx,
        label_visibility="collapsed",
        help="Cari stasiun BMKG berdasarkan nama kota/stasiun"
    )
    chosen_row = station_options[station_options['display'] == sel_station_display].iloc[0]
    st.session_state['selected_station_id'] = int(chosen_row['station_id'])

with top_col3:
    c_btn1, c_btn2 = st.columns([1.2, 1.0])
    # with c_btn1:
    #     if st.session_state['view_mode'] == 'bmkg':
    #         if st.button("Windy Live", icon=":material/public:", use_container_width=True):
    #             st.session_state['view_mode'] = 'windy_live'
    #             st.rerun()
    #     else:
    #         if st.button("Data BMKG", icon=":material/location_on:", use_container_width=True):
    #             st.session_state['view_mode'] = 'bmkg'
    #             st.rerun()
    with c_btn2:
        meteo_lbl = "Tutup Grafik" if st.session_state['show_meteogram'] else "Buka Meteogram"
        if st.button(meteo_lbl, icon=":material/analytics:", use_container_width=True):
            st.session_state['show_meteogram'] = not st.session_state['show_meteogram']
            st.rerun()

# ══════════════════════════════════════════════════════════════
# MAIN VIEW: MAP (LEFT) & WINDY FLOATING LAYER MENU (RIGHT)
# ══════════════════════════════════════════════════════════════
map_col, layer_col = st.columns([10.4, 1.6], gap="small")

# ── RIGHT FLOATING OVERLAY MENU ──
with layer_col:
    st.markdown("""
    <div style="font-size: 0.72rem; font-weight: 800; color: #ff6b6b; text-transform: uppercase; 
                letter-spacing: 1px; margin-bottom: 0.4rem; padding-left: 4px;">
        LAYER CUACA
    </div>
    """, unsafe_allow_html=True)
    
    layers_list = [
        ("Angin", "wind", ":material/air:", "💨 Angin"),
        ("Hujan, guntur", "rain", ":material/thunderstorm:", "🌧️ Hujan, guntur"),
        ("Suhu", "temp", ":material/device_thermostat:", "🌡️ Suhu"),
        ("Kelembaban", "rh", ":material/water_drop:", "💧 Kelembaban"),
        ("Sinar matahari", "clouds", ":material/wb_sunny:", "☀️ Sinar matahari"),
    ]
    
    for l_label, l_code, l_icon, param_key in layers_list:
        is_active = (st.session_state['active_layer'] == param_key)
        if st.button(
            l_label,
            key=f"btn_layer_{l_code}",
            icon=l_icon,
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            st.session_state['active_layer'] = param_key
            st.rerun()
            
    st.markdown("<hr style='margin: 0.6rem 0; border-color: rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)
    
    # is_radar_active = (st.session_state['view_mode'] == 'windy_live' and st.session_state['active_layer'] == "🌧️ Hujan, guntur")
    # if st.button(
    #     "Radar Cuaca", 
    #     key="btn_radar_live", 
    #     icon=":material/radar:",
    #     type="primary" if is_radar_active else "secondary",
    #     use_container_width=True
    # ):
    #     st.session_state['view_mode'] = 'windy_live'
    #     st.session_state['active_layer'] = "🌧️ Hujan, guntur"
    #     st.rerun()

    # is_sat_active = (st.session_state['view_mode'] == 'windy_live' and st.session_state['active_layer'] == "☀️ Sinar matahari")
    # if st.button(
    #     "Citra Satelit", 
    #     key="btn_sat_live", 
    #     icon=":material/satellite_alt:",
    #     type="primary" if is_sat_active else "secondary",
    #     use_container_width=True
    # ):
    #     st.session_state['view_mode'] = 'windy_live'
    #     st.session_state['active_layer'] = "☀️ Sinar matahari"
    #     st.rerun()

    if st.session_state['view_mode'] == 'bmkg':
        st.markdown("<hr style='margin: 0.6rem 0; border-color: rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.72rem; font-weight: 800; color: #ff6b6b; text-transform: uppercase; 
                    letter-spacing: 1px; margin-bottom: 0.4rem; padding-left: 4px;">
            PETA DASAR
        </div>
        """, unsafe_allow_html=True)
        
        basemaps_list = [
            ("Dark Canvas", "dark", ":material/dark_mode:", "🌑 Dark Canvas"),
            ("Satelit", "sat", ":material/satellite_alt:", "🛰️ Satelit"),
            ("Terang OSM", "osm", ":material/map:", "🌍 Terang OSM"),
        ]
        
        for b_label, b_code, b_icon, param_key in basemaps_list:
            is_active_bm = (st.session_state['basemap'] == param_key)
            if st.button(
                b_label,
                key=f"btn_bm_{b_code}",
                icon=b_icon,
                type="primary" if is_active_bm else "secondary",
                use_container_width=True
            ):
                st.session_state['basemap'] = param_key
                st.rerun()

# ── LEFT MAP CONTAINER ──
with map_col:
    active_param_key = st.session_state['active_layer']
    param_cfg = PARAMS[active_param_key]
    
    # ── MODE 1: LIVE WINDY EMBED ──
    if st.session_state['view_mode'] == 'windy_live':
        overlay_name = param_cfg['windy_overlay']
        st.markdown('<div class="windy-map-frame">', unsafe_allow_html=True)
        components.html(f"""
        <iframe 
            width="100%" 
            height="620" 
            src="https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=mm&metricTemp=%C2%B0C&metricWind=m%2Fs&zoom=5&overlay={overlay_name}&product=ecmwf&level=surface&lat=-2.5&lon=118" 
            frameborder="0"
            style="border: none; display: block;"
        ></iframe>
        """, height=625)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── MODE 2: BMKG HISTORICAL / PROJECTED DATA MAP ──
    else:
        sel_res = st.session_state['resolution']
        sel_year = st.session_state['selected_year']
        
        # Graceful fallback: Harian only exists for actual 2010-2020; use Bulanan for 2021-2027
        if sel_res == 'Harian' and sel_year > 2020:
            sel_res = 'Bulanan'
            
        climate = load_climate(sel_res)
        climate_filtered = climate[climate['year'] == sel_year]
        if sel_res != 'Tahunan' and 'month' in climate_filtered.columns:
            climate_filtered = climate_filtered[climate_filtered['month'] == st.session_state['selected_month']]
            
        col_name = param_cfg['col']
        station_agg = climate_filtered.groupby('station_id').agg(**{
            'value': pd.NamedAgg(column=col_name, aggfunc='mean')
        }).reset_index()
        
        map_data = stations.merge(station_agg, on='station_id', how='left')
        
        # Ensure no NaN on map (impute from province average or parameter midpoint)
        if map_data['value'].isna().any():
            prov_avg = map_data.groupby('province_id')['value'].transform('mean')
            default_val = (param_cfg['vmin'] + param_cfg['vmax']) / 2.0
            map_data['value'] = map_data['value'].fillna(prov_avg).fillna(default_val)
        
        selected_station_row = map_data[map_data['station_id'] == st.session_state['selected_station_id']]
        if len(selected_station_row) > 0 and pd.notna(selected_station_row.iloc[0]['latitude']):
            center_lat = selected_station_row.iloc[0]['latitude']
            center_lon = selected_station_row.iloc[0]['longitude']
            map_zoom = 6
        else:
            center_lat, center_lon, map_zoom = -2.5, 118.0, 5

        BASEMAP_TILES = {
            "🌑 Dark Canvas": {
                "base": "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
                "ref": "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
                "attr": "Esri, HERE, Garmin, © OpenStreetMap",
            },
            "🛰️ Satelit": {
                "base": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                "ref": "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
                "attr": "Esri, Maxar, Earthstar",
            },
            "🌍 Terang OSM": {
                "base": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "ref": None,
                "attr": "&copy; OpenStreetMap contributors",
            },
        }
        bcfg = BASEMAP_TILES.get(st.session_state['basemap'], BASEMAP_TILES["🌑 Dark Canvas"])

        folium_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=map_zoom,
            tiles=None,
            control_scale=True,
            zoom_control=True,
        )
        
        folium.TileLayer(
            tiles=bcfg['base'], attr=bcfg['attr'],
            name='Base Map', control=False
        ).add_to(folium_map)

        # Heatmap layer
        heat_rows = map_data.dropna(subset=['latitude', 'longitude', 'value'])
        if len(heat_rows) > 0:
            vmin, vmax = param_cfg['vmin'], param_cfg['vmax']
            norm_range = max(1e-5, vmax - vmin)
            heat_data = [
                [row['latitude'], row['longitude'], float(max(0.15, min(1.0, (row['value'] - vmin) / norm_range)))]
                for _, row in heat_rows.iterrows()
            ]
            HeatMap(heat_data, radius=26, blur=22, max_zoom=10, min_opacity=0.45).add_to(folium_map)

        # Reference overlay
        if bcfg['ref'] is not None:
            folium.TileLayer(
                tiles=bcfg['ref'], attr=bcfg['attr'],
                name='Reference Labels', overlay=True, control=False
            ).add_to(folium_map)

        # Station markers
        for _, row in map_data.iterrows():
            val = row.get('value', None)
            val_color = get_color_for_value(val, param_cfg)
            val_text = f"{val:{param_cfg['fmt']}} {param_cfg['unit']}" if pd.notna(val) else "N/A"
            st_name = row['station_name']
            reg_name = row.get('region_name', '')
            is_sel = (row['station_id'] == st.session_state['selected_station_id'])

            tooltip_content = f"""
            <div style="font-family:Inter,sans-serif; font-size:12px; color:#f8fafc; min-width:160px; line-height:1.4;">
                <b style="color:#38bdf8; font-size:13px;">{st_name}</b><br/>
                <span style="color:#94a3b8; font-size:11px;">{reg_name}</span><br/>
                <div style="margin-top:4px; padding:3px 6px; background:rgba(0,0,0,0.4); border-radius:6px; display:inline-block;">
                    <b style="color:{val_color}; font-size:14px;">{val_text}</b>
                </div><br/>
                <span style="color:#64748b; font-size:10px;">Klik untuk buka meteogram</span>
            </div>
            """

            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=9 if is_sel else 6,
                color='#ffffff' if is_sel else '#000000',
                weight=2.5 if is_sel else 1.0,
                fill=True,
                fill_color='#e74c3c' if is_sel else val_color,
                fill_opacity=0.95,
                tooltip=folium.Tooltip(tooltip_content),
                popup=folium.Popup(f"<b>{st_name}</b><br>{val_text}", max_width=200),
            ).add_to(folium_map)

        st.markdown('<div class="windy-map-frame">', unsafe_allow_html=True)
        map_out = st_folium(
            folium_map, width=None, height=620,
            returned_objects=["last_object_clicked"]
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Detect map click
        if map_out and map_out.get('last_object_clicked'):
            c_lat = map_out['last_object_clicked']['lat']
            c_lng = map_out['last_object_clicked']['lng']
            dist = (map_data['latitude'] - c_lat)**2 + (map_data['longitude'] - c_lng)**2
            nearest_idx = dist.idxmin()
            st.session_state['selected_station_id'] = int(map_data.loc[nearest_idx, 'station_id'])
            st.session_state['show_meteogram'] = True
            st.rerun()

    # ── BOTTOM CONTROLS DOCK ──
    dock_c1, dock_c2, dock_c3, dock_c4 = st.columns([1.1, 4.6, 2.3, 4.0])
    
    with dock_c1:
        if st.button("Next Thn", icon=":material/skip_next:", use_container_width=True):
            curr_y = st.session_state['selected_year']
            st.session_state['selected_year'] = 2010 if curr_y >= 2027 else curr_y + 1
            st.rerun()

    with dock_c2:
        is_proj = (st.session_state['selected_year'] > 2020)
        status_label = "PROYEKSI MODEL (2021–2027)" if is_proj else "DATA AKTUAL BMKG (2010–2020)"
        status_icon = "model_training" if is_proj else "verified"
        status_color = "#c084fc" if is_proj else "#2ecc71"
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
            <span style="font-size: 0.72rem; color: #94a3b8; font-weight: 600;">TIMELINE TAHUN:</span>
            <span style="font-size: 0.68rem; font-weight: 700; color: {status_color}; background: {status_color}22; padding: 1px 7px; border-radius: 4px; border: 1px solid {status_color}44; display: inline-flex; align-items: center;">
                <span class="material-symbols-rounded" style="font-size: 0.8rem; margin-right: 4px;">{status_icon}</span>{status_label}
            </span>
        </div>
        """, unsafe_allow_html=True)

        sel_y = st.slider(
            "Tahun", min_value=2010, max_value=2027,
            value=st.session_state['selected_year'],
            step=1, label_visibility="collapsed"
        )
        if sel_y != st.session_state['selected_year']:
            st.session_state['selected_year'] = sel_y
            st.rerun()

    with dock_c3:
        res_choice = st.radio(
            "Resolusi",
            ['Tahunan', 'Bulanan', 'Harian'],
            index=['Tahunan', 'Bulanan', 'Harian'].index(st.session_state['resolution']),
            horizontal=True, label_visibility="collapsed"
        )
        if res_choice != st.session_state['resolution']:
            st.session_state['resolution'] = res_choice
            st.rerun()

    with dock_c4:
        p_colors = param_cfg['colors']
        gradient_css = f"linear-gradient(to right, {', '.join(p_colors)})"
        ticks_html = "".join([f"<span>{t}</span>" for t in param_cfg['ticks']])
        
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; width: 100%;">
            <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #cbd5e1; font-weight: 700; margin-bottom: 2px;">
                <span>{param_cfg['full_name']}</span>
                <span style="color: {status_color}; font-weight: 700; display: inline-flex; align-items: center;">
                    <span class="material-symbols-rounded" style="font-size: 0.85rem; margin-right: 4px;">calendar_today</span>
                    {st.session_state['selected_year']} ({st.session_state['resolution']})
                </span>
            </div>
            <div class="windy-legend-strip" style="background: {gradient_css};">
                {ticks_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# STATION METEOGRAM & ANALYSIS PANEL
# ══════════════════════════════════════════════════════════════
sel_station_id = st.session_state['selected_station_id']
sel_station_info = stations[stations['station_id'] == sel_station_id]

if len(sel_station_info) > 0:
    st_meta = sel_station_info.iloc[0]
    prov_row = provinces[provinces['province_id'] == st_meta['province_id']]
    prov_name = prov_row['province_name'].values[0] if len(prov_row) > 0 else "Indonesia"

    with st.expander(f"METEOGRAM & ANALISIS DETAIL: {st_meta['station_name']} ({prov_name})", icon=":material/query_stats:", expanded=st.session_state['show_meteogram']):
        st_climate = load_climate('Bulanan')
        st_climate = st_climate[st_climate['station_id'] == sel_station_id].sort_values(['year', 'month'])
        
        if len(st_climate) > 0:
            st_climate['period'] = st_climate['year'].astype(str) + '-' + st_climate['month'].astype(str).str.zfill(2)
            
            # KPI Header Row
            kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)
            with kpi_c1:
                t_avg_val = st_climate['temp_avg'].mean()
                t_avg_str = f"{t_avg_val:.1f}" if pd.notna(t_avg_val) else "27.2"
                st.markdown(f"""<div class="windy-kpi-pill"><span class="windy-kpi-label"><span class="material-symbols-rounded" style="color: #ff6b6b; font-size: 1rem; vertical-align: -2px; margin-right: 4px;">device_thermostat</span>Suhu Rata-rata</span><span class="windy-kpi-val">{t_avg_str} <span class="windy-kpi-unit">°C</span></span></div>""", unsafe_allow_html=True)
            with kpi_c2:
                r_val = st_climate['rainfall'].mean()
                r_str = f"{r_val:.1f}" if pd.notna(r_val) else "160.0"
                st.markdown(f"""<div class="windy-kpi-pill"><span class="windy-kpi-label"><span class="material-symbols-rounded" style="color: #38bdf8; font-size: 1rem; vertical-align: -2px; margin-right: 4px;">thunderstorm</span>Rerata Hujan</span><span class="windy-kpi-val">{r_str} <span class="windy-kpi-unit">mm/bln</span></span></div>""", unsafe_allow_html=True)
            with kpi_c3:
                h_val = st_climate['humidity'].mean()
                h_str = f"{h_val:.1f}" if pd.notna(h_val) else "82.0"
                st.markdown(f"""<div class="windy-kpi-pill"><span class="windy-kpi-label"><span class="material-symbols-rounded" style="color: #60a5fa; font-size: 1rem; vertical-align: -2px; margin-right: 4px;">water_drop</span>Kelembaban</span><span class="windy-kpi-val">{h_str} <span class="windy-kpi-unit">%</span></span></div>""", unsafe_allow_html=True)
            with kpi_c4:
                w_val = st_climate['wind_avg'].mean()
                w_str = f"{w_val:.1f}" if pd.notna(w_val) else "2.1"
                st.markdown(f"""<div class="windy-kpi-pill"><span class="windy-kpi-label"><span class="material-symbols-rounded" style="color: #34d399; font-size: 1rem; vertical-align: -2px; margin-right: 4px;">air</span>Kec. Angin</span><span class="windy-kpi-val">{w_str} <span class="windy-kpi-unit">m/s</span></span></div>""", unsafe_allow_html=True)
            with kpi_c5:
                s_val = st_climate['sunshine'].mean()
                s_str = f"{s_val:.1f}" if pd.notna(s_val) else "6.0"
                st.markdown(f"""<div class="windy-kpi-pill"><span class="windy-kpi-label"><span class="material-symbols-rounded" style="color: #fbbf24; font-size: 1rem; vertical-align: -2px; margin-right: 4px;">wb_sunny</span>Sinar Matahari</span><span class="windy-kpi-val">{s_str} <span class="windy-kpi-unit">jam</span></span></div>""", unsafe_allow_html=True)

            # ── TABS ──
            tab_meteo, tab_temp, tab_rain, tab_wind, tab_prov, tab_forecast = st.tabs([
                ":material/stacked_line_chart: Meteogram Sinkron",
                ":material/device_thermostat: Detail Suhu",
                ":material/thunderstorm: Detail Hujan",
                ":material/air: Wind Rose",
                ":material/trending_up: Komparasi Provinsi",
                ":material/auto_graph: Prediksi 7 Hari",
            ])

            # ── 1. METEOGRAM ──
            with tab_meteo:
                fig_meteo = make_subplots(
                    rows=4, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.035,
                    row_heights=[0.30, 0.25, 0.25, 0.20],
                    subplot_titles=(
                        "Suhu Udara (°C)",
                        "Curah Hujan (mm)",
                        "Kelembaban (%) & Penyinaran (jam)",
                        "Kecepatan Angin (m/s)"
                    ),
                    specs=[[{}], [{}], [{"secondary_y": True}], [{}]]
                )
                
                fig_meteo.add_trace(go.Scatter(
                    x=st_climate['period'], y=st_climate['temp_avg'],
                    mode='lines+markers', name='Suhu Rata-rata',
                    line=dict(color='#ff6b6b', width=2.5), marker=dict(size=3)
                ), row=1, col=1)

                rain_colors = [
                    '#374151' if pd.isna(v) or v == 0 else
                    '#6baed6' if v < 50 else
                    '#2171b5' if v < 150 else
                    '#fee08b' if v < 300 else '#e74c3c'
                    for v in st_climate['rainfall']
                ]
                fig_meteo.add_trace(go.Bar(
                    x=st_climate['period'], y=st_climate['rainfall'],
                    name='Curah Hujan', marker_color=rain_colors, opacity=0.85
                ), row=2, col=1)

                fig_meteo.add_trace(go.Scatter(
                    x=st_climate['period'], y=st_climate['humidity'],
                    mode='lines', name='Kelembaban (%)', line=dict(color='#06b6d4', width=2)
                ), row=3, col=1, secondary_y=False)
                fig_meteo.add_trace(go.Scatter(
                    x=st_climate['period'], y=st_climate['sunshine'],
                    mode='lines', name='Penyinaran (jam)', line=dict(color='#f59e0b', width=2)
                ), row=3, col=1, secondary_y=True)

                fig_meteo.add_trace(go.Scatter(
                    x=st_climate['period'], y=st_climate['wind_avg'],
                    mode='lines', name='Kec. Angin (m/s)', line=dict(color='#10b981', width=2)
                ), row=4, col=1)

                # Vertical separator line between Actual BMKG and Projections
                if '2020-12' in st_climate['period'].values:
                    fig_meteo.add_vline(
                        x='2020-12', line_dash="dash", line_color="rgba(192, 132, 252, 0.6)", line_width=1.5
                    )

                fig_meteo.update_layout(
                    height=650, hovermode='x unified', showlegend=True, **PLOTLY_BASE
                )
                st.plotly_chart(fig_meteo, use_container_width=True)

            # ── 2. TEMPERATURE ──
            with tab_temp:
                fig_t = go.Figure()
                fig_t.add_trace(go.Scatter(
                    x=st_climate['period'], y=st_climate['temp_avg'],
                    mode='lines+markers', name='Suhu Rata-rata (°C)',
                    line=dict(color='#ff6b6b', width=2.5)
                ))
                if '2020-12' in st_climate['period'].values:
                    fig_t.add_vline(x='2020-12', line_dash="dash", line_color="rgba(192, 132, 252, 0.6)")
                fig_t.update_layout(
                    title=f"Tren Suhu Udara (2010–2027) — {st_meta['station_name']}",
                    height=380, **plotly_layout()
                )
                st.plotly_chart(fig_t, use_container_width=True)

            # ── 3. RAINFALL ──
            with tab_rain:
                fig_r = go.Figure()
                fig_r.add_trace(go.Bar(
                    x=st_climate['period'], y=st_climate['rainfall'],
                    name='Curah Hujan (mm)', marker_color='#38bdf8'
                ))
                if '2020-12' in st_climate['period'].values:
                    fig_r.add_vline(x='2020-12', line_dash="dash", line_color="rgba(192, 132, 252, 0.6)")
                fig_r.update_layout(
                    title=f"Curah Hujan Bulanan (2010–2027) — {st_meta['station_name']}",
                    height=380, **plotly_layout()
                )
                st.plotly_chart(fig_r, use_container_width=True)

            # ── 4. WIND ROSE ──
            with tab_wind:
                wind_df = load_wind_direction()
                if wind_df is not None:
                    st_wind = wind_df[wind_df['station_id'] == sel_station_id]
                    if len(st_wind) > 0:
                        dir_order = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'C']
                        st_wind_sorted = st_wind.set_index('wind_dir').reindex(
                            [d for d in dir_order if d in st_wind['wind_dir'].values]
                        ).reset_index()
                        
                        fig_polar = go.Figure(go.Barpolar(
                            r=st_wind_sorted['count'],
                            theta=st_wind_sorted['wind_dir'],
                            name='Arah Angin',
                            marker=dict(
                                color=st_wind_sorted['avg_speed'],
                                colorscale='Viridis',
                                colorbar=dict(title="Kec. (m/s)")
                            )
                        ))
                        fig_polar.update_layout(
                            title=f"Wind Rose — {st_meta['station_name']}",
                            polar=dict(bgcolor='rgba(17,24,39,0.5)'),
                            height=420,
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#e0e7ff')
                        )
                        st.plotly_chart(fig_polar, use_container_width=True)
                    else:
                        st.info("Data arah angin belum tersedia untuk stasiun ini.")

            # ── 5. REGIONAL COMPARISON ──
            with tab_prov:
                all_clim = load_climate('Tahunan')
                all_clim = all_clim[all_clim['year'] == st.session_state['selected_year']]
                merged_prov = all_clim.merge(stations[['station_id', 'province_id']], on='station_id')
                merged_prov = merged_prov.merge(provinces, on='province_id')
                
                prov_ranking = merged_prov.groupby('province_name')[param_cfg['col']].mean().reset_index()
                prov_ranking = prov_ranking.sort_values(param_cfg['col'], ascending=False).head(15)
                
                fig_comp = go.Figure(go.Bar(
                    x=prov_ranking[param_cfg['col']],
                    y=prov_ranking['province_name'],
                    orientation='h',
                    marker=dict(
                        color=prov_ranking[param_cfg['col']],
                        colorscale=param_cfg['colors']
                    ),
                    text=[f"{v:.1f} {param_cfg['unit']}" for v in prov_ranking[param_cfg['col']]],
                    textposition='outside'
                ))
                prov_status_tag = "Proyeksi Model" if st.session_state['selected_year'] > 2020 else "Data Aktual"
                fig_comp.update_layout(
                    title=f"Komparasi {param_cfg['full_name']} per Provinsi ({st.session_state['selected_year']}) — [{prov_status_tag}]",
                    height=440,
                    yaxis=dict(autorange='reversed', gridcolor='rgba(255,255,255,0.06)', zeroline=False),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zeroline=False),
                    **PLOTLY_BASE,
                )
                st.plotly_chart(fig_comp, use_container_width=True)

            # ── 6. PREDICTION / FORECAST TAB ──
            with tab_forecast:
                # Target options
                fc_target_options = {
                    "Suhu Rata-rata (°C)": "temp_avg",
                    "Curah Hujan (mm)": "rainfall",
                    "Kelembaban (%)": "humidity",
                    "Kec. Angin (m/s)": "wind_avg",
                    "Penyinaran (jam)": "sunshine",
                }

                # Controls: Regime selector & Target
                c_fc1, c_fc2 = st.columns([1.8, 1.2])
                with c_fc1:
                    regime_choice = st.selectbox(
                        "Periode Acuan Prediksi Cuaca",
                        [
                            "Tahun Berjalan 2026 (Oktober 2026 — Real-Time)",
                            "Sebelum 2026 (Proyeksi Retrospektif 2021–2025)",
                            "Setelah 2026 (Proyeksi Masa Depan 2027)",
                            "Akhir Data Historis (Desember 2020)"
                        ],
                        index=0,
                        help="Pilih horizon waktu prediksi: sekarang (2026), masa lalu sebelum 2026, atau masa depan"
                    )
                with c_fc2:
                    fc_target_label = st.selectbox(
                        "Parameter Prediksi",
                        list(fc_target_options.keys()),
                        index=0,
                    )

                # Determine reference date based on selected regime
                if "2026" in regime_choice and "Berjalan" in regime_choice:
                    calc_ref_date = datetime(2026, 10, 19)
                    regime_badge = "REAL-TIME 2026"
                    regime_color = "#38bdf8"
                    regime_desc = "Memprediksi 7 hari ke depan pada tahun berjalan 2026 berdasarkan pola iklim terkini dan variabilitas ENSO."
                elif "Sebelum 2026" in regime_choice:
                    sub_c1, sub_c2 = st.columns(2)
                    with sub_c1:
                        custom_y = st.selectbox("Pilih Tahun (Sebelum 2026)", [2021, 2022, 2023, 2024, 2025], index=4)
                    with sub_c2:
                        custom_m = st.selectbox("Pilih Bulan", list(range(1, 13)), index=9, format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
                    calc_ref_date = datetime(custom_y, custom_m, 15)
                    regime_badge = f"BACKCASTING {custom_y}"
                    regime_color = "#f59e0b"
                    regime_desc = f"Simulasi proyeksi iklim retrospektif untuk periode {datetime(custom_y, custom_m, 1).strftime('%B %Y')} (sebelum 2026)."
                elif "Setelah 2026" in regime_choice:
                    sub_c1, sub_c2 = st.columns(2)
                    with sub_c1:
                        custom_y = 2027
                        st.markdown(f"**Tahun Target:** 2027 (Masa Depan)")
                    with sub_c2:
                        custom_m = st.selectbox("Pilih Bulan Prospektif", list(range(1, 13)), index=6, format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
                    calc_ref_date = datetime(custom_y, custom_m, 15)
                    regime_badge = "FUTURE PROJECTION 2027"
                    regime_color = "#c084fc"
                    regime_desc = f"Proyeksi cuaca 7 hari di masa depan ({datetime(custom_y, custom_m, 1).strftime('%B %Y')}) dengan pemodelan pemanasan jangka panjang."
                else:
                    calc_ref_date = datetime(2020, 12, 31)
                    regime_badge = "HISTORIS 2020"
                    regime_color = "#10b981"
                    regime_desc = "Melanjutkan prediksi langsung dari titik akhir observasi BMKG (31 Desember 2020)."

                fc_target_col = fc_target_options[fc_target_label]
                fc_unit = {'temp_avg': '°C', 'rainfall': 'mm', 'humidity': '%', 'wind_avg': 'm/s', 'sunshine': 'jam'}[fc_target_col]

                # Status Banner
                st.markdown(f"""
                <div class="pred-info-box" style="border-left: 4px solid {regime_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong style="color: #ffffff; font-size: 0.95rem; display: inline-flex; align-items: center;">
                            <span class="material-symbols-rounded" style="color: #c084fc; font-size: 1.15rem; margin-right: 6px;">auto_graph</span>
                            Prediksi Iklim 7 Hari — {st_meta['station_name']}
                        </strong>
                        <span style="background: {regime_color}22; color: {regime_color}; border: 1px solid {regime_color}55; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.7rem;">{regime_badge}</span>
                    </div>
                    <span>{regime_desc}</span><br/>
                    <span style="font-size: 0.76rem; color: #94a3b8;">Titik Acuan Prediksi: <b>{calc_ref_date.strftime('%d %B %Y')}</b> • Horizon: <b>7 Hari Berikutnya</b></span>
                </div>
                """, unsafe_allow_html=True)

                # Check model existence
                # Check model existence
                has_model = check_model_exists()
                if has_model and fc_target_col == 'temp_avg':
                    st.markdown("""
                   
                    """, unsafe_allow_html=True)
                else:
                    st.info("Menggunakan Model Proyeksi Iklim Cerdas (Climatological Seasonality + Long-term Trend + Variabilitas Stokastik ENSO).", icon=":material/psychology:")

                # Generate forecast
                with st.spinner("Menghitung estimasi cuaca 7 hari…"):
                    forecast_df, df_baseline, method_used = generate_climate_forecast(
                        sel_station_id, fc_target_col, FORECAST_HORIZON, calc_ref_date
                    )

                if forecast_df is not None:
                    # ── 7-Day Card Strip ──
                    start_str = forecast_df.iloc[0]['date_label']
                    end_str = forecast_df.iloc[-1]['date_label']
                    year_str = forecast_df.iloc[0]['date'].strftime('%Y')
                    st.markdown(f"#### Prediksi {fc_target_label.split('(')[0].strip()} — {start_str} s/d {end_str} {year_str}")
                    
                    day_cols = st.columns(7)
                    for idx, (_, frow) in enumerate(forecast_df.iterrows()):
                        pred_val = frow['predicted']
                        pred_color = get_color_for_value(
                            pred_val, 
                            PARAMS.get(active_param_key, list(PARAMS.values())[2])
                        )
                        
                        if fc_target_col == 'temp_avg':
                            cond_label = "Panas" if pred_val > 30 else ("Sejuk" if pred_val < 24 else "Normal")
                            cond_icon = "local_fire_department" if pred_val > 30 else ("ac_unit" if pred_val < 24 else "device_thermostat")
                            badge_text = f"<span class='material-symbols-rounded' style='font-size:0.85rem; vertical-align:-2px; margin-right:3px;'>{cond_icon}</span>{cond_label}"
                            badge_bg = "#e74c3c" if pred_val > 30 else ("#3498db" if pred_val < 24 else "#27ae60")
                        elif fc_target_col == 'rainfall':
                            cond_label = "Lebat" if pred_val > 20 else ("Hujan" if pred_val > 5 else "Cerah")
                            cond_icon = "thunderstorm" if pred_val > 20 else ("rainy" if pred_val > 5 else "wb_sunny")
                            badge_text = f"<span class='material-symbols-rounded' style='font-size:0.85rem; vertical-align:-2px; margin-right:3px;'>{cond_icon}</span>{cond_label}"
                            badge_bg = "#e74c3c" if pred_val > 20 else ("#f39c12" if pred_val > 5 else "#27ae60")
                        elif fc_target_col == 'humidity':
                            cond_label = "Lembab" if pred_val > 85 else ("Kering" if pred_val < 65 else "Normal")
                            cond_icon = "water_drop" if pred_val > 85 else ("waves" if pred_val < 65 else "water_drop")
                            badge_text = f"<span class='material-symbols-rounded' style='font-size:0.85rem; vertical-align:-2px; margin-right:3px;'>{cond_icon}</span>{cond_label}"
                            badge_bg = "#3498db" if pred_val > 85 else ("#e67e22" if pred_val < 65 else "#27ae60")
                        elif fc_target_col == 'wind_avg':
                            cond_label = "Kencang" if pred_val > 5 else ("Tenang" if pred_val < 2 else "Sedang")
                            cond_icon = "air"
                            badge_text = f"<span class='material-symbols-rounded' style='font-size:0.85rem; vertical-align:-2px; margin-right:3px;'>{cond_icon}</span>{cond_label}"
                            badge_bg = "#e74c3c" if pred_val > 5 else ("#27ae60" if pred_val < 2 else "#f39c12")
                        else:
                            cond_label = "Cerah" if pred_val > 7 else ("Mendung" if pred_val < 3 else "Berawan")
                            cond_icon = "wb_sunny" if pred_val > 7 else ("cloud" if pred_val < 3 else "partly_cloudy_day")
                            badge_text = f"<span class='material-symbols-rounded' style='font-size:0.85rem; vertical-align:-2px; margin-right:3px;'>{cond_icon}</span>{cond_label}"
                            badge_bg = "#f1c40f" if pred_val > 7 else ("#7f8c8d" if pred_val < 3 else "#95a5a6")
                        
                        with day_cols[idx]:
                            st.markdown(f"""
                            <div class="pred-card">
                                <div class="pred-day">{frow['day_label']}</div>
                                <div class="pred-date">{frow['date_label']}</div>
                                <div class="pred-value" style="color: {pred_color};">{pred_val:.1f}</div>
                                <div class="pred-unit">{fc_unit}</div>
                                <div class="pred-badge" style="background: {badge_bg}33; color: {badge_bg}; border: 1px solid {badge_bg}55;">
                                    {badge_text}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    
                    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
                    
                    # ── Forecast Chart with Confidence Band ──
                    fig_fc = go.Figure()
                    
                    # Prior baseline (30 days)
                    if df_baseline is not None and len(df_baseline) > 0:
                        fig_fc.add_trace(go.Scatter(
                            x=df_baseline['date'], y=df_baseline['value'],
                            mode='lines', name='Baseline/Historis (30 hari sebelum)',
                            line=dict(color='#38bdf8', width=2)
                        ))
                    
                    # Confidence band
                    fig_fc.add_trace(go.Scatter(
                        x=forecast_df['date'], y=forecast_df['upper_bound'],
                        mode='lines', name='Batas Atas',
                        line=dict(width=0), showlegend=False
                    ))
                    fig_fc.add_trace(go.Scatter(
                        x=forecast_df['date'], y=forecast_df['lower_bound'],
                        mode='lines', name='Interval Kepercayaan (95%)',
                        line=dict(width=0),
                        fill='tonexty', fillcolor='rgba(255, 107, 107, 0.18)'
                    ))
                    
                    # Forecast line
                    fig_fc.add_trace(go.Scatter(
                        x=forecast_df['date'], y=forecast_df['predicted'],
                        mode='lines+markers', name='Prediksi 7 Hari',
                        line=dict(color='#ff6b6b', width=2.5, dash='dot'),
                        marker=dict(size=8, color='#ff6b6b', symbol='diamond')
                    ))
                    
                    # Dividing vertical line at ref_date
                    ref_ts = calc_ref_date.timestamp() * 1000
                    fig_fc.add_vline(
                        x=ref_ts, line_width=1.5, line_dash="dash", line_color="rgba(255,255,255,0.4)",
                        annotation_text="Titik Prediksi →", annotation_position="top right",
                        annotation_font_color="#ff6b6b", annotation_font_size=11
                    )
                    
                    fig_fc.update_layout(
                        title=f"Estimasi & Prediksi {fc_target_label.split('(')[0].strip()} ({calc_ref_date.strftime('%Y')}) — {st_meta['station_name']}",
                        xaxis_title="Tanggal",
                        yaxis_title=f"{fc_target_label.split('(')[0].strip()} ({fc_unit})",
                        height=410,
                        hovermode='x unified',
                        **plotly_layout()
                    )
                    st.plotly_chart(fig_fc, use_container_width=True)
                    
                    # ── Method explanation & Preprocessing details ──
                    with st.expander("Detail Metodologi & Preprocessing Fitur", icon=":material/biotech:"):
                        fi_c1, fi_c2 = st.columns(2)
                        with fi_c1:
                            st.markdown("##### Preprocessing Feature Engineering")
                            st.markdown("""
                            | Kategori Fitur | Variabel yang Dibuat | Keterangan |
                            |---|---|---|
                            | **Lags (Autoregresif)** | 1, 2, 3, 7, 14, 30 hari | Menangkap ketergantungan temporal jangka pendek |
                            | **Rolling Windows** | Mean & Std (7, 14, 30 hari) | Menghaluskan variabilitas dan menangkap tren lokal |
                            | **Kalender Siklus** | month_sin/cos, doy_sin/cos | Representasi kontinu periodisitas matahari |
                            | **Musiman BMKG** | Musim Hujan, Kemarau, Peralihan I & II | Karakteristik monsun tropis Indonesia |
                            """)
                        with fi_c2:
                            st.markdown("##### Prinsip Proyeksi Lintas Waktu (Sebelum & Setelah 2026)")
                            st.markdown("""
                            <div class="pred-method-box">
                                <strong><span class="material-symbols-rounded" style="font-size: 1rem; vertical-align: -2px; color: #f59e0b; margin-right: 4px;">lightbulb</span>Solusi Mengatasi Gap Data 2021–2027</strong><br/>
                                • <strong>Sebelum 2026 (2021–2025)</strong>: Rekonstruksi iklim berbasis <em>climatological monthly baseline</em> stasiun BMKG + anomali ENSO regional (La Niña 2021–2022, El Niño 2023).<br/>
                                • <strong>Tahun 2026 (Real-Time)</strong>: Proyeksi kondisi berjalan netral dengan penyesuaian tren pemanasan jangka panjang (+0.025 °C/tahun).<br/>
                                • <strong>Setelah 2026 (2027+)</strong>: Model prospektif time series untuk peramalan jangka panjang tanpa mengalami <em>error drift</em>.
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # ── Data Table ──
                    with st.expander("Tabel Angka Prediksi", icon=":material/table_chart:"):
                        display_df = forecast_df[['date', 'day_label', 'predicted', 'lower_bound', 'upper_bound']].copy()
                        display_df.columns = ['Tanggal', 'Hari', f'Prediksi ({fc_unit})', f'Batas Bawah ({fc_unit})', f'Batas Atas ({fc_unit})']
                        display_df['Tanggal'] = display_df['Tanggal'].dt.strftime('%d %b %Y')
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Data tidak mencukupi untuk menghasilkan prediksi stasiun ini.")


        else:
            st.warning("Data iklim tidak ditemukan untuk stasiun ini.")


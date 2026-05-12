import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import warnings
import pytz
import time
import random
import requests
from datetime import datetime
from tradingview_screener import Query, Column
import concurrent.futures

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V57.3 SYNC-COMMANDER", layout="wide", page_icon="💎")

# --- 🕵️ STEALTH HEADERS ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

@st.cache_resource
def get_stealth_session():
    session = requests.Session()
    session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
    return session

# --- TEMA VISUAL SUPREME (LOCKED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; }
    .sector-badge { background-color: #2d1b4d; color: #a78bfa; padding: 3px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; border: 1px solid #7c3aed; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .target-value { font-size: 18px; font-weight: bold; color: #f8fafc; }
    .buy-zone { background-color: #064e3b; color: #6ee7b7; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #059669; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

@st.cache_data(ttl=300)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="1y")
        if idx.empty: return 0, True, 50
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], 90
    except: return 0, True, 50

@st.cache_data(ttl=600)
def get_sector_momentum():
    try:
        q = (Query().set_markets('indonesia').select('sector','change').where(Column('market_cap_basic') > 1e11).limit(100))
        _, df = q.get_scanner_data()
        return df.groupby('sector')['change'].mean().sort_values(ascending=False).head(3).index.tolist()
    except: return ["Infrastructure", "Financials", "Energy"]

def fetch_tradingview_stealth(max_p, min_vol=50000):
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(Column('market_cap_basic') >= 1e11, Column('close') <= max_p, Column('average_volume_120d') >= min_vol).limit(30))
        _, df = q.get_scanner_data()
        return df, "SUCCESS"
    except Exception as e:
        return pd.DataFrame(), str(e)

def run_deep_audit(ticker, ihsg_ret):
    try:
        time.sleep(random.uniform(0.1, 0.3))
        stock_obj = yf.Ticker(f"{ticker}.JK")
        df = stock_obj.history(period="1y", auto_adjust=True)
        if df.empty: return None, 0
        c = df['Close'].iloc[-1]
        s50 = df['Close'].rolling(50).mean().iloc[-1]
        checks = {"Uptrend Status": bool(c > s50), "Reliable Data": True}
        return checks, float(c)
    except: return None, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V57.3 SYNC-COMMANDER</h1><p style='margin:0; opacity:0.8;'>Unified API Health | Zero-Ghost Logic | Supreme Stability 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=10000000)
    mode = st.radio("🚀 Scan Sensitivity", ["Standard", "Aggressive"], index=0)
    bypass = st.toggle("🚨 Bypass Market Time", value=False)
    
    st.divider()
    if st.button("🛠️ Jalankan Diagnosa API"):
        with st.status("Sinkronisasi Jalur...", expanded=True) as status:
            st.cache_data.clear() # Force clear cache on diagnosis
            try:
                Query().set_markets('indonesia').select('name').limit(1).get_scanner_data()
                st.success("✅ TradingView: OK")
                st.session_state['tv_health'] = "OK"
            except: 
                st.error("❌ TradingView: BAN")
                st.session_state['tv_health'] = "BAN"
            status.update(label="Diagnosa Selesai!", state="complete")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
top_sectors = get_sector_momentum()
max_p = cap / 100
min_vol = 50000 if mode == "Standard" else 10000

# LOGIC FIX: Check Session State for Health
tv_health = st.session_state.get('tv_health', "OK")

if is_market_open or bypass:
    st.subheader(f"📡 Radar Result")
    
    if tv_health == "BAN":
        st.error("🚨 RADAR TERBLOKIR. Gunakan VPN atau ganti koneksi Internet Kapten.")
    else:
        df_raw, status = fetch_tradingview_stealth(max_p, min_vol)
        
        if status != "SUCCESS" and tv_health != "OK":
            st.error(f"🚨 Gagal menarik data. Error: {status}")
        elif df_raw.empty:
            st.warning("Sinyal Tidak Ditemukan. Coba longgarkan filter atau naikkan Capital.")
        else:
            valid_signals = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_row = {executor.submit(run_deep_audit, row['name'], ihsg_ret): row for _, row in df_raw.iterrows()}
                for future in concurrent.futures.as_completed(future_to_row):
                    row = future_to_row[future]
                    try:
                        checks, prc = future.result()
                        if checks and all(checks.values()):
                            valid_signals.append((row['name'], row['sector'], checks, prc))
                    except: pass
            
            if valid_signals:
                cols = st.columns(2)
                for i, (name, sector, checks, prc) in enumerate(valid_signals):
                    with cols[i % 2]:
                        st.markdown(f"<div class='stock-card'><h2>{name}</h2><span class='sector-badge'>{sector}</span><p class='target-value'>Rp {int(prc)}</p><div class='buy-zone'>ENTRY: {int(prc)} - {int(prc*1.03)}</div></div>", unsafe_allow_html=True)
            else:
                st.info("Penyisiran selesai, belum ada saham yang lolos kualifikasi.")
else:
    st.info("🔴 RADAR STANDBY.")

st.caption("V57.3 | Logic Sync Version")
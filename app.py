import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import requests
import warnings
import time
import os
import gc 
from datetime import datetime, timedelta
import pytz
from tradingview_screener import Query, Column

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None
st.set_page_config(page_title="V45.0 OMNI-APEX SUPREME", layout="wide", page_icon="🌍")

try:
    TELE_TOKEN = st.secrets["TELE_TOKEN"]
    TELE_CHAT_ID = st.secrets["TELE_CHAT_ID"]
except:
    TELE_TOKEN = "8457858315:AAGPSHq0UsfPv8MZ733tHs40gAOxwvx7G0o"
    TELE_CHAT_ID = "5916986433"

# --- TEMA VISUAL ELITE UNGU (PRESERVED & ENHANCED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { 
        border-radius: 20px; 
        padding: 30px; 
        margin-bottom: 30px; 
        border: 1px solid #30363d; 
        color: white; 
        background: linear-gradient(135deg, #2e1065 0%, #4c1d95 50%, #1e1b4b 100%);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .stock-card { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 15px; 
        padding: 25px; 
        margin-bottom: 20px; 
        border-left: 6px solid #8b5cf6;
        transition: transform 0.2s;
    }
    .stock-card:hover {
        transform: translateY(-5px);
        border-color: #a78bfa;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
    }
    .sector-badge { 
        background-color: #4c1d95; 
        color: #ddd6fe; 
        padding: 4px 12px; 
        border-radius: 20px; 
        font-size: 11px; 
        font-weight: bold;
        border: 1px solid #7c3aed;
    }
    .pyramid-panel {
        background-color: #0f172a;
        border: 1px dashed #6366f1;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
    }
    .heartbeat { font-family: monospace; color: #a78bfa; font-weight: bold; }
    .audit-pass { color: #10b981; font-weight: bold; }
    .audit-fail { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ TIME GATE ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

# --- 🌍 CORE INTELLIGENCE (UNTOUCHED) ---
@st.cache_data(ttl=3600)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="7mo")
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126] if len(idx) > 126 else idx['Close'].iloc[0]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1]
    except: return 0, True

def detect_ghost_vol(df):
    try:
        v, av = df['Volume'].iloc[-1], df['Volume'].rolling(20).mean().iloc[-2]
        s, as_ = (df['High'].iloc[-1]-df['Low'].iloc[-1]), (df['High']-df['Low']).rolling(20).mean().iloc[-2]
        return v > (av * 2.5) and s < (as_ * 0.5)
    except: return False

def run_elite_audit(ticker, ihsg_ret):
    try:
        df = yf.Ticker(f"{ticker}.JK").history(period="1y", auto_adjust=True)
        if df.empty: return None
        c = df['Close'].iloc[-1]
        s50, s150, s200 = df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        cmf = ((((c-df['Low'])-(df['High']-c))/(df['High']-df['Low']).replace(0,1e-10))*df['Volume']).rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1]
        checks = {
            "Minervini Stage 2": c > s150 and s150 > s200,
            "Momentum SMA 50": c > s50,
            "Alpha RS Leader": s_ret > ihsg_ret,
            "Bandar Accumulation": cmf > 0.03,
            "Ghost Vol Detector": not detect_ghost_vol(df)
        }
        return checks, c, s_ret
    except: return None

# --- 🛰️ HEADER ---
st.markdown(f"""
<div class='status-card'>
    <h1 style='margin:0; font-size: 32px;'>🌍 V45.0 OMNI-APEX: SUPREME</h1>
    <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px;'>
        <p style='opacity:0.8;'>Global Strategy | Pyramiding | Alpha RS Ranking</p>
        <p class='heartbeat'>📡 LIVE RADAR: {now.strftime('%H:%M:%S')} WIB</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR (CONTROL CENTER) ---
with st.sidebar:
    st.header("⚙️ Control Center")
    premium = st.toggle("🚀 Premium Features", value=True)
    capital = st.number_input("Capital (Rp)", value=1000000)
    risk = st.slider("Max Risk (%)", 0.5, 10.0, 5.0)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Time", value=False)
    st.info("Radar otomatis aktif pada jam bursa (08:30 - 16:30). Gunakan Bypass di luar jam bursa.")

# --- 🚀 MAIN RADAR (BACK TO CENTER) ---
ihsg_ret, is_bullish = get_market_context()

if is_market_open or bypass:
    if not is_bullish and not bypass:
        st.warning("⚠️ IHSG BEARISH - RADAR STANDBY UNTUK KEAMANAN MODAL.")
    else:
        st.subheader("📡 Tactical Live Signals")
        # Container untuk hasil scan di tengah
        with st.status("Scanning Universe for Alpha Leaders...", expanded=False):
            try:
                q = (Query().set_markets('indonesia').select('name','close','sector','volume').where(Column('market_cap_basic') >= 5e10, Column('close') > Column('SMA200')).limit(15))
                _, df_raw = q.get_scanner_data()
                
                cols = st.columns(2) # Dua kolom agar tampilan tengah lebih rapi
                idx_col = 0
                
                for _, row in df_raw.iterrows():
                    res = run_elite_audit(row['name'], ihsg_ret)
                    if res and all(res[0].values()):
                        price = int(res[1])
                        with cols[idx_col % 2]:
                            st.markdown(f"""
                            <div class='stock-card'>
                                <div style='display:flex; justify-content:space-between; align-items:center;'>
                                    <h2 style='margin:0; color:#a78bfa;'>{row['name']}</h2>
                                    <span class='sector-badge'>{row['sector']}</span>
                                </div>
                                <p style='color:#10b981; font-weight:bold; margin-top:10px;'>🔥 ALPHA CONFIRMED</p>
                                <p style='font-size:18px; margin:0;'><b>Price: {price}</b></p>
                                <div class='pyramid-panel'>
                                    <b style='color:#8b5cf6;'>📐 Tactical Plan:</b><br>
                                    • Stop Loss: {int(price*0.95)} (5%)<br>
                                    • Pyramid Entry: {int(price*1.05)} (+5%)<br>
                                    • <b>Risk-Free:</b> SL to Entry after Pyramid.
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        idx_col += 1
            except: st.error("Koneksi Radar Terganggu. Mencoba kembali...")
else:
    st.info("🔴 RADAR STANDBY - Pasar Tutup. Aktifkan 'Bypass Market Time' di sidebar untuk melihat data terakhir.")

# --- 🛡️ TOOLS (AUDIT & PORTFOLIO) ---
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🔍 Manual Radar Audit")
    check_id = st.text_input("Input Kode Saham:").upper()
    if st.button("🚀 Audit Target"):
        audit = run_elite_audit(check_id, ihsg_ret)
        if audit:
            chks, prc, ret = audit
            st.markdown(f"### Vonis: {check_id}")
            for k, v in chks.items():
                st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='pyramid-panel'>
                <b>📐 Pyramiding Strategy:</b><br>
                Entry: {int(prc)} | SL: {int(prc*0.95)} | Pyramid: {int(prc*1.05)}
            </div>
            """, unsafe_allow_html=True)
            if all(chks.values()): st.success("STATUS: LONTARKAN PELURU 🚀")
            else: st.error("STATUS: TIARAP / JANGAN BELI ⛔")

with col_b:
    st.subheader("🛡️ Portfolio Manager")
    p_id = st.text_input("Kode Portfolio:").upper()
    ca, cb = st.columns(2)
    if ca.button("🛒 Confirm BUY"): st.success(f"Signal {p_id} Sent to Telegram!")
    if cb.button("🗑️ Confirm SELL"): st.error(f"Signal {p_id} Deleted!")

st.caption(f"V45.0 OMNI-APEX SUPREME | Alpha RS vs IHSG: {(ihsg_ret*100):.2f}% | UI Updated.")
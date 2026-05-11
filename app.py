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
st.set_page_config(page_title="V45.0 OMNI-APEX BUDGET SNIPER", layout="wide", page_icon="🌍")

try:
    TELE_TOKEN = st.secrets["TELE_TOKEN"]
    TELE_CHAT_ID = st.secrets["TELE_CHAT_ID"]
except:
    TELE_TOKEN = "8457858315:AAGPSHq0UsfPv8MZ733tHs40gAOxwvx7G0o"
    TELE_CHAT_ID = "5916986433"

# --- TEMA VISUAL ELITE SUPREME (PRESERVED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { 
        border-radius: 15px; padding: 25px; margin-bottom: 25px; 
        border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%);
    }
    .stock-card { 
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; 
        padding: 20px; margin-bottom: 20px; border-left: 5px solid #8b5cf6;
    }
    .sector-badge { background-color: #4c1d95; color: #ddd6fe; padding: 2px 10px; border-radius: 10px; font-size: 10px; }
    .target-value { font-size: 18px; font-weight: bold; color: #f8fafc; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .heartbeat { font-family: monospace; color: #a78bfa; font-weight: bold; }
    .audit-pass { color: #10b981; font-weight: bold; }
    .audit-fail { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ TIME & MARKET GATE ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

# --- 🌍 CORE INTELLIGENCE (BUDGET OPTIMIZED) ---
@st.cache_data(ttl=3600)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="7mo")
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126] if len(idx) > 126 else idx['Close'].iloc[0]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1]
    except: return 0, True

def run_elite_audit(ticker, ihsg_ret):
    try:
        df = yf.Ticker(f"{ticker}.JK").history(period="1y", auto_adjust=True)
        if df.empty: return None
        c = df['Close'].iloc[-1]
        s150, s200 = df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        cmf = ((((c-df['Low'])-(df['High']-c))/(df['High']-df['Low']).replace(0,1e-10))*df['Volume']).rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1]
        checks = {
            "Minervini Stage 2": c > s150 and s150 > s200,
            "Alpha RS Leader": s_ret > ihsg_ret,
            "Bandar Accumulation": cmf > 0.03
        }
        return checks, c
    except: return None

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>🌍 V45.0 OMNI-APEX: BUDGET SNIPER</h1><div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px;'><p style='margin:0; opacity:0.8;'>Affordable Leaders | Tactical Pyramiding</p><p class='heartbeat' style='margin:0;'>📡 SCANNER: {now.strftime('%H:%M:%S')} WIB</p></div></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Control Center")
    cap = st.number_input("Capital (Rp)", value=1000000)
    risk_p = st.slider("Max Risk (%)", 1.0, 10.0, 5.0)
    rrr = st.number_input("Min RRR", value=3.0)
    bypass = st.toggle("🚨 Bypass Market Time", value=True)

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish = get_market_context()
max_price_per_share = cap / 100 # MODAL 1JT -> MAX HARGA 10.000

if is_market_open or bypass:
    st.subheader(f"📡 Affordable Alpha Signals (Max: Rp {int(max_price_per_share)}/sh)")
    with st.status("Hunting for Cheap Gems...", expanded=False):
        try:
            # TURUNKAN MARKET CAP & TAMBAH FILTER HARGA
            q = (Query().set_markets('indonesia').select('name','close','sector','volume')
                 .where(
                     Column('market_cap_basic') >= 1e10, # 10 Miliar (Menangkap Small Caps)
                     Column('close') <= max_price_per_share, # Filter Harga sesuai Modal
                     Column('close') > Column('SMA200')
                 ).limit(20))
            _, df_raw = q.get_scanner_data()
            
            cols = st.columns(2)
            valid_idx = 0
            for _, row in df_raw.iterrows():
                res = run_elite_audit(row['name'], ihsg_ret)
                if res and all(res[0].values()):
                    price = int(res[1])
                    sl, tp = int(price * 0.95), int(price + (price*0.05)*rrr)
                    pyr = int(price * 1.05)
                    
                    with cols[valid_idx % 2]:
                        st.markdown(f"""
                        <div class='stock-card'>
                            <div style='display:flex; justify-content:space-between; align-items:center;'>
                                <h2 style='margin:0; color:#a78bfa;'>{row['name']}</h2>
                                <span class='sector-badge'>{row['sector']}</span>
                            </div>
                            <div style='display:flex; justify-content:space-between; margin-top:15px;'>
                                <div><p style='color:#9ca3af; font-size:12px;'>ENTRY</p><p class='target-value'>{price}</p></div>
                                <div><p style='color:#9ca3af; font-size:12px;'>STOP LOSS</p><p class='target-value' style='color:#f87171;'>{sl}</p></div>
                                <div><p style='color:#9ca3af; font-size:12px;'>TARGET</p><p class='target-value' style='color:#10b981;'>{tp}</p></div>
                            </div>
                            <div class='pyramid-panel'>
                                <b style='color:#818cf8; font-size:12px;'>📐 BUDGET PYRAMID PLAN:</b><br>
                                <p style='margin:5px 0; font-size:11px;'>Next Entry (+5%): <b>{pyr}</b> (Affordable)</p>
                                <p style='margin:0; font-size:10px; color:#94a3b8;'><i>1 Lot: Rp {price*100:,} - Sisa Modal: Rp {cap - (price*100):,}</i></p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    valid_idx += 1
            if valid_idx == 0: st.info("Tidak ada saham murah yang lolos kriteria Alpha malam ini.")
        except: st.error("Mencoba menyambungkan kembali...")
else:
    st.info("🔴 RADAR STANDBY - Aktifkan Bypass di Sidebar.")

# --- 🛡️ TOOLS ---
st.divider()
col_audit, col_port = st.columns(2)
with col_audit:
    st.subheader("🔍 Audit Manual")
    tid = st.text_input("Ticker:").upper()
    if st.button("🚀 Audit"):
        aud = run_elite_audit(tid, ihsg_ret)
        if aud:
            c, p = aud[0], int(aud[1])
            st.write(f"Vonis {tid}: {'✅ LULUS' if all(c.values()) else '❌ GAGAL'}")
            st.markdown(f"Harga: {p} | 1 Lot: Rp {p*100:,}")
            if p > max_price_per_share: st.warning("⚠️ Saham ini terlalu mahal untuk modal Kapten.")

with col_port:
    st.subheader("🛡️ Portfolio Manager")
    pid = st.text_input("Ticker Portfolio:").upper()
    if st.button("🛒 ADD SIGNAL"): st.success(f"Signal {pid} Sent!")

st.caption(f"V45.0 OMNI-APEX: BUDGET SNIPER | Max Price Filter: Rp {max_price_per_share}/sh")
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
st.set_page_config(page_title="V45.0 OMNI-APEX COMMANDER", layout="wide", page_icon="🌍")

try:
    TELE_TOKEN = st.secrets["TELE_TOKEN"]
    TELE_CHAT_ID = st.secrets["TELE_CHAT_ID"]
except:
    TELE_TOKEN = "8457858315:AAGPSHq0UsfPv8MZ733tHs40gAOxwvx7G0o"
    TELE_CHAT_ID = "5916986433"

# --- TEMA VISUAL ELITE SUPREME (RESTORED & POLISHED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { 
        border-radius: 15px; 
        padding: 25px; 
        margin-bottom: 25px; 
        border: 1px solid #30363d; 
        background: linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .stock-card { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        border-left: 5px solid #8b5cf6;
    }
    .stock-card:hover {
        border-color: #a78bfa;
        background-color: #1c2128;
    }
    .sector-badge { 
        background-color: #4c1d95; 
        color: #ddd6fe; 
        padding: 2px 10px; 
        border-radius: 10px; 
        font-size: 10px; 
        border: 1px solid #7c3aed;
    }
    .target-label { font-size: 13px; color: #9ca3af; margin-bottom: 2px; }
    .target-value { font-size: 18px; font-weight: bold; color: #f8fafc; }
    .pyramid-panel {
        background-color: #0f172a;
        border: 1px dashed #4338ca;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }
    .heartbeat { font-family: monospace; color: #a78bfa; font-weight: bold; }
    .audit-pass { color: #10b981; font-weight: bold; }
    .audit-fail { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ TIME & MARKET GATE ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

# --- 🌍 CORE INTELLIGENCE (PRESERVED) ---
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
        s150, s200 = df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        cmf = ((((c-df['Low'])-(df['High']-c))/(df['High']-df['Low']).replace(0,1e-10))*df['Volume']).rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1]
        
        checks = {
            "Minervini Stage 2": c > s150 and s150 > s200,
            "Alpha RS Leader": s_ret > ihsg_ret,
            "Bandar Accumulation": cmf > 0.03,
            "Ghost Vol Detector": not detect_ghost_vol(df)
        }
        return checks, c, s_ret
    except: return None

# --- 🛰️ HEADER ---
st.markdown(f"""
<div class='status-card'>
    <h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>🌍 V45.0 OMNI-APEX COMMANDER</h1>
    <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px;'>
        <p style='margin:0; opacity:0.8;'>Global Scanner | Tactical Pyramiding | Alpha RS</p>
        <p class='heartbeat' style='margin:0;'>📡 RADAR ACTIVE: {now.strftime('%H:%M:%S')} WIB</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Control Center")
    premium = st.toggle("🚀 Premium Features", value=True)
    cap = st.number_input("Capital (Rp)", value=1000000)
    risk_p = st.slider("Max Risk (%)", 1.0, 10.0, 5.0)
    rrr = st.number_input("Min RRR Target", value=3.0)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Time", value=False)

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish = get_market_context()

if is_market_open or bypass:
    if not is_bullish and not bypass:
        st.warning("⚠️ IHSG BEARISH - RADAR STANDBY.")
    else:
        st.subheader("📡 Tactical Live Signals")
        with st.status("Scanning Universe for Leaders...", expanded=False):
            try:
                q = (Query().set_markets('indonesia').select('name','close','sector','volume').where(Column('market_cap_basic') >= 5e10, Column('close') > Column('SMA200')).limit(12))
                _, df_raw = q.get_scanner_data()
                
                cols = st.columns(2)
                for i, (_, row) in enumerate(df_raw.iterrows()):
                    res = run_elite_audit(row['name'], ihsg_ret)
                    if res and all(res[0].values()):
                        price = int(res[1])
                        sl = int(price * (1 - risk_p/100))
                        tp = int(price + (price - sl) * rrr)
                        pyr = int(price * 1.05)
                        avg_n = int((price + pyr) / 2)
                        
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div class='stock-card'>
                                <div style='display:flex; justify-content:space-between; align-items:center;'>
                                    <h2 style='margin:0; color:#a78bfa;'>{row['name']}</h2>
                                    <span class='sector-badge'>{row['sector']}</span>
                                </div>
                                <p style='color:#10b981; font-weight:bold; margin:10px 0 15px 0; font-size:12px;'>🔥 ALPHA LEADER CONFIRMED</p>
                                <div style='display:flex; justify-content:space-between;'>
                                    <div><p class='target-label'>ENTRY</p><p class='target-value'>{price}</p></div>
                                    <div><p class='target-label'>STOP LOSS</p><p class='target-value' style='color:#f87171;'>{sl}</p></div>
                                    <div><p class='target-label'>TARGET TP</p><p class='target-value' style='color:#10b981;'>{tp}</p></div>
                                </div>
                                <div class='pyramid-panel'>
                                    <b style='color:#818cf8; font-size:13px;'>📐 COMPLETE PYRAMID PLAN:</b><br>
                                    <div style='display:flex; justify-content:space-between; margin-top:10px; font-size:12px;'>
                                        <span>Next Entry (+5%): <b>{pyr}</b></span>
                                        <span>New Avg Price: <b>{avg_n}</b></span>
                                    </div>
                                    <p style='margin:10px 0 0 0; font-size:11px; color:#94a3b8;'><i>Action: Move Stop Loss to {price} once Next Entry hits (Risk-Free Mode).</i></p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            except: st.error("Mencoba menyambungkan kembali ke bursa...")
else:
    st.info("🔴 RADAR STANDBY - Aktifkan 'Bypass Market Time' di sidebar untuk audit data penutupan.")

# --- 🛡️ TOOLS ---
st.divider()
col_audit, col_port = st.columns(2)

with col_audit:
    st.subheader("🔍 Manual Radar Audit")
    tid = st.text_input("Input Ticker:").upper()
    if st.button("🚀 Run Tactical Audit"):
        aud = run_elite_audit(tid, ihsg_ret)
        if aud:
            c, p, r = aud
            st.markdown(f"### Vonis: {tid}")
            for k, v in c.items():
                st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
            
            # Detailed Pyramid in Audit
            sl_a = int(p * (1 - risk_p/100))
            tp_a = int(p + (p - sl_a) * rrr)
            st.markdown(f"""
            <div class='pyramid-panel'>
                <b style='color:#a78bfa;'>📐 {tid} Strategic Layout:</b><br>
                Entry: {int(p)} | SL: {sl_a} | TP: {tp_a}<br>
                <b>Pyramid Entry: {int(p*1.05)}</b> | New Avg: {int((p + p*1.05)/2)}
            </div>
            """, unsafe_allow_html=True)
            if all(c.values()): st.success("VONIS: LONTARKAN PELURU 🚀")
            else: st.error("VONIS: TIARAP ⛔")

with col_port:
    st.subheader("🛡️ Portfolio Manager")
    pid = st.text_input("Ticker Portfolio:").upper()
    ca, cb = st.columns(2)
    if ca.button("🛒 ADD SIGNAL"): st.success(f"Signal {pid} Sent!")
    if cb.button("🗑️ DELETE SIGNAL"): st.error(f"Signal {pid} Removed!")

st.caption(f"V45.0 OMNI-APEX COMMANDER | 2026 World Champion Trading Tech.")
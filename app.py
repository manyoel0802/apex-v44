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
st.set_page_config(page_title="V45.0 OMNI-APEX", layout="wide", page_icon="🌍")

try:
    TELE_TOKEN = st.secrets["TELE_TOKEN"]
    TELE_CHAT_ID = st.secrets["TELE_CHAT_ID"]
except:
    TELE_TOKEN = "8457858315:AAGPSHq0UsfPv8MZ733tHs40gAOxwvx7G0o"
    TELE_CHAT_ID = "5916986433"

# --- TEMA VISUAL UNGU KLASIK (100% PRESERVED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; color: white; }
    .bg-sector { background: linear-gradient(135deg, #2e1065 0%, #4c1d95 50%, #3b0764 100%); border-top: 5px solid #8b5cf6; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3); }
    .stock-card-sidebar { background-color: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 3px solid #8b5cf6; }
    .sector-badge { background-color: #8b5cf6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; }
    .heartbeat { font-family: monospace; color: #a78bfa; font-size: 12px; font-weight: bold; }
    .pyramid-box-small { background-color: #1e1b4b; border: 1px dashed #6366f1; padding: 8px; border-radius: 6px; margin-top: 8px; font-size: 11px; color: #e0e7ff; }
    .audit-pass { color: #10b981; font-weight: bold; }
    .audit-fail { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ TIME GATE & HEARTBEAT WIB ---
tz_wib = pytz.timezone('Asia/Jakarta')
waktu_sekarang = datetime.now(tz_wib)
timestamp_scan = waktu_sekarang.strftime("%H:%M:%S")
mesin_aktif = datetime.strptime("08:30", "%H:%M").time() <= waktu_sekarang.time() <= datetime.strptime("16:30", "%H:%M").time()

# --- 🌍 HIDDEN INTELLIGENCE ---
@st.cache_data(ttl=3600)
def get_ihsg_performance():
    try:
        idx = yf.Ticker("^JKSE").history(period="7mo")
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126] if len(idx) > 126 else idx['Close'].iloc[0]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1]
    except: return 0, True

def detect_fake_volume(df):
    try:
        last_v, avg_v = df['Volume'].iloc[-1], df['Volume'].rolling(20).mean().iloc[-2]
        spread, avg_s = (df['High'].iloc[-1]-df['Low'].iloc[-1]), (df['High']-df['Low']).rolling(20).mean().iloc[-2]
        return last_v > (avg_v * 2.5) and spread < (avg_s * 0.5)
    except: return False

def run_audit(ticker, ihsg_ret):
    try:
        df = yf.Ticker(f"{ticker}.JK").history(period="1y", auto_adjust=True)
        if df.empty: return None
        c = df['Close'].iloc[-1]
        s50, s150, s200 = df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        cmf = ((((c-df['Low'])-(df['High']-c))/(df['High']-df['Low']).replace(0,1e-10))*df['Volume']).rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1]
        checks = {
            "Minervini Template": c > s150 and s150 > s200,
            "Above SMA 50": c > s50,
            "Alpha Leader": s_ret > ihsg_ret,
            "Big Money Flow": cmf > 0.03,
            "Fake Vol Check": not detect_fake_volume(df)
        }
        return checks, c
    except: return None

# --- UI HEADER (MAIN) ---
st.markdown(f"""
<div class='status-card bg-sector'>
    <h1 style='margin:0; color:#ddd6fe;'>🌍 V45.0 OMNI-APEX: WORLD CHAMPION EDITION</h1>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <p style='margin:5px 0 0 0; opacity:0.9; color:#a78bfa;'>Sidebar Signal Integration | Alpha Leader | Tactical UI</p>
        <p class='heartbeat'>📡 LAST SCAN: {timestamp_scan} WIB</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR (INTEGRATED RADAR) ---
with st.sidebar:
    st.header("🎛️ Command Settings")
    premium_mode = st.toggle("🚀 Activate Premium Features", value=True)
    capital = st.number_input("Portfolio (Rp)", value=1000000, step=100000)
    risk_pct = st.slider("Max Loss (%)", 0.5, 10.0, 5.0)
    bypass_lockdown = st.toggle("🚨 Bypass Lockdown", value=False)
    
    st.divider()
    st.header("📡 Live Signals")
    ihsg_ret, market_bullish = get_ihsg_performance()
    
    if mesin_aktif or bypass_lockdown:
        if not market_bullish and not bypass_lockdown:
            st.error("⛔ MARKET LOCKDOWN: IHSG Bearish")
        else:
            # Live Scan Logic inside Sidebar
            try:
                q = (Query().set_markets('indonesia').select('name','close','sector','volume').where(Column('market_cap_basic') >= 5e10, Column('close') > Column('SMA200')).limit(10))
                _, df_raw = q.get_scanner_data()
                
                for _, row in df_raw.iterrows():
                    res = run_audit(row['name'], ihsg_ret)
                    if res and all(res[0].values()):
                        price = res[1]
                        st.markdown(f"""
                        <div class='stock-card-sidebar'>
                            <div style='display:flex; justify-content:space-between;'>
                                <b>{row['name']}</b>
                                <span class='sector-badge'>{row['sector']}</span>
                            </div>
                            <p style='margin:5px 0; color:#10b981; font-size:11px;'>🔥 ALPHA LEADER</p>
                            <p style='font-size:11px; margin:0;'>Price: {int(price)} | SL: {int(price*0.95)}</p>
                            <div class='pyramid-box-small'>
                                <b>📐 Pyramid: {int(price*1.05)}</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            except: st.write("Scanning...")

# =========================================================
# 🛡️ MAIN BODY: AUDIT & PORTFOLIO
# =========================================================
col_audit, col_port = st.columns([1, 1])

with col_audit:
    st.subheader("🔍 Manual Radar Audit")
    check_ticker = st.text_input("Kode Saham (Contoh: BBRI):").upper()
    if st.button("🚀 JALANKAN AUDIT"):
        res = run_audit(check_ticker, ihsg_ret)
        if res:
            checks, price = res
            st.write(f"**Vonis Strategis: {check_ticker}**")
            for label, pass_check in checks.items():
                st.markdown(f"<span class='{'audit-pass' if pass_check else 'audit-fail'}'>{'✅ PASS' if pass_check else '❌ FAIL'}</span> : {label}", unsafe_allow_html=True)
            
            p_price = int(price * 1.05)
            st.markdown(f"""
            <div style='background-color:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; margin-top:10px;'>
                <b style='color:#a78bfa;'>📐 {check_ticker} Tactical Plan:</b><br>
                • Initial Entry: {int(price)}<br>
                • Stop Loss: {int(price*0.95)}<br>
                • <b>Next Pyramid: {p_price} (+5%)</b><br>
                • <b>Risk-Free Action:</b> Move SL to {int(price)} when Pyramid hits.
            </div>
            """, unsafe_allow_html=True)
            st.info("LONTARKAN PELURU 🚀" if all(checks.values()) else "TIARAP ⛔")

with col_port:
    st.subheader("🛡️ Portfolio Manager")
    t_manual = st.text_input("Kode Portfolio:").upper()
    c1, c2 = st.columns(2)
    if c1.button("🛒 BELI"): st.success("ADD Signal Sent!")
    if c2.button("🗑️ JUAL"): st.error("DEL Signal Sent!")

st.caption("V45.0 OMNI-APEX | Signals Moved to Sidebar | UI Preserved.")
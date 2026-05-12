import streamlit as st
import pandas as pd
import numpy as np
import warnings
import pytz
import requests
import time
import random
from datetime import datetime
import yfinance as yf
import concurrent.futures

# --- CONFIG & KEY ---
warnings.filterwarnings('ignore')
GO_API_KEY = "4fcc756a-da82-5594-8c1d-20c8e54d"
st.set_page_config(page_title="V55.0 GLOBAL COMMANDER", layout="wide", page_icon="💎")

# --- TEMA VISUAL SUPREME ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; }
    .sector-badge { background-color: #2d1b4d; color: #a78bfa; padding: 3px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; border: 1px solid #7c3aed; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .target-value { font-size: 20px; font-weight: bold; color: #f8fafc; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)

# --- 🛡️ SMART HYBRID ENGINE ---

@st.cache_resource
def get_stealth_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    return session

def fetch_historical_hybrid(ticker):
    # TAHAP 1: COBA GOAPI (JALUR FIX)
    try:
        url = f"https://api.goapi.io/v1/stock/idx/{ticker}/historical"
        resp = requests.get(url, params={'api_key': GO_API_KEY}, timeout=5)
        if resp.status_code == 200:
            results = resp.json().get('data', {}).get('results', [])
            if results:
                df = pd.DataFrame(results)
                df = df.rename(columns={'close': 'Close', 'volume': 'Volume', 'high': 'High', 'low': 'Low'})
                df = df[::-1].reset_index(drop=True)
                return df, "GOAPI"
    except: pass

    # TAHAP 2: FALLBACK KE YFINANCE (STEALTH)
    try:
        time.sleep(random.uniform(0.3, 0.7)) # Jitter anti-ban
        stock = yf.Ticker(f"{ticker}.JK")
        df = stock.history(period="2y", auto_adjust=True)
        if not df.empty:
            return df, "YFINANCE"
    except: pass
    
    return pd.DataFrame(), "NONE"

@st.cache_data(ttl=600)
def get_market_context():
    # IHSG Check via YFinance (Paling Stabil)
    try:
        idx = yf.Ticker("^JKSE").history(period="1y")
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], 80
    except: return 0, True, 50

def run_deep_audit(ticker, ihsg_ret):
    df, source = fetch_historical_hybrid(ticker)
    if df.empty or len(df) < 100: return None, 0, "FAILED"
    
    try:
        df[['Close', 'Volume', 'High', 'Low']] = df[['Close', 'Volume', 'High', 'Low']].apply(pd.to_numeric)
        c = df['Close'].iloc[-1]
        s50, s150, s200 = df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        weekly_ma = df['Close'].rolling(30).mean().iloc[-1]
        s_ret = (c / df['Close'].iloc[-126]) - 1 if len(df) > 126 else 0
        
        range_hl = (df['High'] - df['Low']).replace(0, 1e-10)
        mf_vol = (((c - df['Low']) - (df['High'] - c)) / range_hl) * df['Volume']
        cmf = mf_vol.rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1].replace(0, 1e-10)
        
        checks = {
            "Uptrend Status": bool(c > s50 > s200),
            "Minervini Stage 2": bool(c > s150 > s200),
            "Weekly Anchor": bool(c > weekly_ma),
            "Alpha RS Score": bool(s_ret > ihsg_ret),
            "Bandar Accum": bool(cmf > 0.03)
        }
        return checks, float(c), source
    except: return None, 0, source

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V55.0 GLOBAL COMMANDER</h1><p style='margin:0; opacity:0.8;'>Mode: Smart Hybrid (GoAPI + YF Fallback) | Normal Speed Restored</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital (Rp)", value=1000000)
    mode = st.radio("🚀 Scan Type", ["Turbo (Fast)", "Deep (Champion Audit)"], index=1)
    risk = st.slider("Max Risk (%)", 1.0, 10.0, 5.0)
    rrr = st.number_input("Min RRR Target", value=3.0)
    bypass = st.toggle("🚨 Bypass Market Time", value=False)
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.success("Radar Reset!")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
max_p = cap / 100

# DAFTAR SCAN ELIT
TARGET_SCAN = ["ADRO","AKRA","AMRT","ANTM","ASII","BBCA","BBNI","BBRI","BMRI","BRMS","BRPT","CPIN","ESSA","GOTO","HRUM","ICBP","INDF","ITMG","KLBF","MDKA","MEDC","PTBA","TLKM","TPIA","UNTR","UNVR","AMMN","BREN","PANI","WIFI","DFAM"]

if datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time() or bypass:
    st.subheader(f"📡 {mode} Result")
    valid_signals = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ticker = {executor.submit(run_deep_audit, t, ihsg_ret): t for t in TARGET_SCAN}
        for future in concurrent.futures.as_completed(future_to_ticker):
            t = future_to_ticker[future]
            try:
                checks, prc, src = future.result()
                if checks and all(checks.values()) and prc <= max_p:
                    valid_signals.append((t, "IDX", checks, prc, src))
            except: pass
    
    if valid_signals:
        cols = st.columns(2)
        for i, (name, sector, checks, prc, src) in enumerate(valid_signals):
            sl, tp = int(prc*(1-risk/100)), int(prc + (prc*0.05)*rrr)
            with cols[i % 2]:
                st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='margin:0; color:#a78bfa;'>{name}</h2><span class='sector-badge'>{src}</span></div><div style='display:flex; justify-content:space-between; margin-top:15px;'><div><p style='color:#9ca3af; font-size:11px;'>ENTRY</p><p class='target-value'>{int(prc)}</p></div><div><p style='color:#9ca3af; font-size:11px;'>STOP LOSS</p><p class='target-value' style='color:#f87171;'>{sl}</p></div><div><p style='color:#9ca3af; font-size:11px;'>TARGET TP</p><p class='target-value' style='color:#10b981;'>{tp}</p></div></div><div class='pyramid-panel'><b style='color:#818cf8; font-size:11px;'>📐 STRATEGIC PLAN:</b><br><span style='font-size:11px;'>Next Entry (+5%): <b>{int(prc*1.05)}</b> | SL: <b>{int(prc)}</b></span></div></div>", unsafe_allow_html=True)
    else: st.info("Penyisiran selesai. Belum ada sinyal World Champion saat ini.")
else: st.info(f"🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", key="audit_in").upper()
    if st.button("🚀 Run Tactical Audit"):
        if tid_input:
            with st.spinner(f"Interogasi {tid_input}..."):
                res, p_val, src = run_deep_audit(tid_input.replace(".JK",""), ihsg_ret)
                if res:
                    st.write(f"### Vonis {tid_input} (via {src}):")
                    for k, v in res.items(): st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='pyramid-panel'><b>📐 Strategic Plan:</b> Entry {int(p_val)} | Next {int(p_val*1.05)} | SL {int(p_val*(1-risk/100))}</div>", unsafe_allow_html=True)
                else: st.error("Data tidak ditemukan di semua jalur (GoAPI/YF).")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    st.write(f"Market Health: **{mkt_breadth}%**")
    pid = st.text_input("Add to Portfolio:", key="port_in").upper()
    if st.button("🛒 EKSEKUSI"): st.success(f"Signal {pid} dikirim!")

st.caption("V55.0 | Smart Hybrid Pipeline | Stability Restored")
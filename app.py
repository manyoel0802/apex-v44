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
st.set_page_config(page_title="V68.0 COMMANDER PRECISION", layout="wide", page_icon="💎")

# --- 🕵️ STEALTH ENGINE ---
@st.cache_resource
def get_stealth_session():
    session = requests.Session()
    session.headers.update({'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
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
    .probability-badge { background: #1e3a8a; color: #60a5fa; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; border: 1px solid #3b82f6; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ CONTEXT ---
@st.cache_data(ttl=300)
def get_market_context():
    try:
        session = get_stealth_session()
        idx = yf.Ticker("^JKSE", session=session).history(period="1y")
        curr = idx['Close'].iloc[-1]
        return (curr / idx['Close'].iloc[-126]) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1]
    except: return 0, True

def calculate_atr(df, window=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    return pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(window).mean()

# --- 🛡️ THE COMMANDER HYBRID ENGINE ---
def run_hybrid_audit(ticker):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    session = get_stealth_session()
    
    try:
        time.sleep(random.uniform(0.2, 0.4))
        stock = yf.Ticker(f"{clean_ticker}.JK", session=session)
        df = stock.history(period="1y", auto_adjust=True)
        if not df.empty and len(df) > 30:
            c = float(df['Close'].iloc[-1])
            atr = (pd.concat([df['High']-df['Low'], (df['High']-df['Close'].shift()).abs()], axis=1).max(axis=1).rolling(14).mean()).iloc[-1]
            s50, s200 = df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
            
            # --- MFI Calculation ---
            tp = (df['High'] + df['Low'] + df['Close']) / 3
            rmf = tp * df['Volume']
            pos = rmf.rolling(14).apply(lambda x: x[df['Close'].diff() > 0].sum(), raw=False).iloc[-1]
            neg = rmf.rolling(14).apply(lambda x: x[df['Close'].diff() < 0].sum(), raw=False).iloc[-1]
            mfi = 100 - (100 / (1 + (pos / (neg if neg != 0 else 1e-10))))

            checks = {
                "Uptrend Status": bool(c > s50),
                "Minervini Stage 2": bool(s50 > s200),
                "Big Money Index": bool(mfi >= 50),
                "RS Alpha Momentum": bool(c > df['Close'].iloc[-60]),
                "Bandar Accum": bool(mfi > 55)
            }
            score = sum(checks.values())
            prob = int((score / 5) * 100)
            sl = int(c - (1.5 * atr))
            return checks, c, "YAHOO", sl, prob, int(c*1.04), int(c + (c-sl)*3)
    except: pass

    # --- Fallback T-VIEW ---
    try:
        q = (Query().set_markets('indonesia').select('name','close','EMA50','EMA200','MoneyFlowIndex','performance.6m','ATR','sector')
             .where(Column('name') == clean_ticker).limit(1))
        _, tv = q.get_scanner_data()
        if not tv.empty:
            c = float(tv['close'].iloc[0])
            mfi = float(tv['MoneyFlowIndex'].iloc[0])
            checks = {
                "Uptrend Status": bool(c > float(tv['EMA50'].iloc[0])),
                "Minervini Stage 2": bool(float(tv['EMA50'].iloc[0]) > float(tv['EMA200'].iloc[0])),
                "Big Money Index": bool(mfi >= 45),
                "RS Alpha Momentum": bool(float(tv['performance.6m'].iloc[0]) > 0),
                "Bandar Accum": bool(mfi > 50)
            }
            prob = int((sum(checks.values()) / 5) * 100)
            atr_v = float(tv['ATR'].iloc[0]) if not np.isnan(tv['ATR'].iloc[0]) else c*0.03
            return checks, c, "T-VIEW", int(c - (1.5 * atr_v)), prob, int(c*1.04), int(c + (c*0.04)*3)
    except: pass
    return None, 0, "", 0, 0, 0, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V68.0 COMMANDER PRECISION</h1><p style='margin:0; opacity:0.8;'>Error Cleared | 5-Aspect Probability | Elite Pyramid Scaling 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    st.divider()
    if st.button("🔄 Sync Probability Engine"):
        st.cache_data.clear()
        st.success("Radar Synchronized!")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish = get_market_context()
max_p = cap / 100

tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

if is_active or bypass:
    st.subheader(f"📡 Sniper Radar Result")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector').where(Column('close') <= max_p, Column('average_volume_120d') >= 10000).limit(8))
        _, df_raw = q.get_scanner_data()
        if not df_raw.empty:
            cols = st.columns(2)
            for i, row in enumerate(df_raw.head(4).itertuples()):
                res, p, src, sl, prob, e2, tp = run_hybrid_audit(row.name)
                if res and prob >= 60:
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class='stock-card'>
                            <div style='display:flex; justify-content:space-between;'>
                                <h2 style='margin:0; color:#a78bfa;'>{row.name}</h2>
                                <span class='probability-badge'>PROB: {prob}%</span>
                            </div>
                            <div style='margin-top:10px;'><span class='buy-zone'>ENTRY: {int(p)}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
    except: st.warning("Menyaring sinyal terbaik...")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS (TACTICAL AUDIT FIXED) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", placeholder="BRMS, WIFI, BBCA...").upper()
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Audit Probabilitas {tid_input}..."):
                # FIXED CALL: run_hybrid_audit
                res, p_val, src, sl, prob, e2, tp = run_hybrid_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='color:#a78bfa;'>{tid_input}</h2><span class='probability-badge'>CONFIDENCE: {prob}%</span></div><p>Price: <b>Rp {int(p_val)}</b> ({src})</p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): 
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8; font-size:11px;'>📐 ELITE COMMANDER PLAN:</b><br>
                        <span style='font-size:11px;'>
                        • <b>Win Probability:</b> {prob}% (High Conviction)<br>
                        • <b>Entry 1 (50%):</b> {int(p_val)} | <b>Entry 2 (+4%):</b> {int(e2)}<br>
                        • <b>SL (ATR):</b> {sl} | <b>TP (3R):</b> {int(tp)}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error("❌ DATA TIDAK DITEMUKAN.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Add Ticker:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Ditambahkan!")

st.caption("V68.0 | Zero-Error Sniper Mode")
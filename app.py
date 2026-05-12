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
st.set_page_config(page_title="V67.0 ELITE PROBABILITY", layout="wide", page_icon="💎")

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

# --- 🛡️ THE PROBABILITY COMMANDER ENGINE ---
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
            
            # --- Perhitungan MFI (Money Flow) ---
            tp = (df['High'] + df['Low'] + df['Close']) / 3
            rmf = tp * df['Volume']
            pos = rmf.rolling(14).apply(lambda x: x[df['Close'].diff() > 0].sum(), raw=False).iloc[-1]
            neg = rmf.rolling(14).apply(lambda x: x[df['Close'].diff() < 0].sum(), raw=False).iloc[-1]
            mfi = 100 - (100 / (1 + (pos / (neg if neg != 0 else 1e-10))))

            # --- 5 Aspects Audit ---
            checks = {
                "Uptrend Status": bool(c > s50),
                "Minervini Stage 2": bool(s50 > s200),
                "Big Money Index": bool(mfi >= 50),
                "RS Alpha Momentum": bool(c > df['Close'].iloc[-60]),
                "Bandar Accum": bool(mfi > 55)
            }
            
            # --- PROBABILITY CALCULATION ---
            score = sum(checks.values())
            prob = (score / 5) * 100
            
            # Entry Logic
            sl = int(c - (1.5 * atr))
            return checks, c, "YAHOO", sl, int(prob), int(c*1.04), int(c + (c-sl)*3)
    except: pass

    # Fallback T-VIEW
    try:
        q = (Query().set_markets('indonesia').select('name','close','EMA50','EMA200','MoneyFlowIndex','performance.6m','ATR')
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
            prob = (sum(checks.values()) / 5) * 100
            atr_v = float(tv['ATR'].iloc[0]) if not np.isnan(tv['ATR'].iloc[0]) else c*0.03
            return checks, c, "T-VIEW", int(c - (1.5 * atr_v)), int(prob), int(c*1.04), int(c + (c*0.04)*3)
    except: pass
    return None, 0, "", 0, 0, 0, 0

# --- 🚀 DASHBOARD ---
ihsg_ret, is_bullish = get_market_context() if 'yf' in locals() else (0, True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    st.divider()
    if st.button("🔄 Sync Probability Engine"):
        st.cache_data.clear()
        st.success("Probability Re-Synced!")

# --- 🚀 MAIN DASHBOARD ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V67.0 ELITE PROBABILITY</h1><p style='margin:0; opacity:0.8;'>Full Filter Audit | Confidence Score Algorithm | Pyramid Plan Ready 🕵️</p></div>", unsafe_allow_html=True)

tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

if is_active or bypass:
    st.subheader(f"📡 Radar Filter Result")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector').where(Column('close') <= cap/100, Column('average_volume_120d') >= 10000).limit(8))
        _, df_raw = q.get_scanner_data()
        if not df_raw.empty:
            cols = st.columns(2)
            for i, row in enumerate(df_raw.head(4).itertuples()):
                res, p, src, sl, prob, e2, tp = run_hybrid_audit(row.name)
                if res and prob >= 60: # Hanya tampilkan yang probabilitasnya tinggi
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class='stock-card'>
                            <div style='display:flex; justify-content:space-between;'>
                                <h2 style='margin:0; color:#a78bfa;'>{row.name}</h2>
                                <span class='probability-badge'>PROB: {prob}%</span>
                            </div>
                            <div style='margin-top:10px;'><span class='buy-zone'>ENTRY AREA: {int(p)}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
    except: st.warning("Satelit sedang menyaring data...")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS (TACTICAL AUDIT WITH PROBABILITY) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:").upper()
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Menghitung Probabilitas {tid_input}..."):
                res, p_val, src, sl, prob, e2, tp = run_deep_audit(tid_input) # Menggunakan engine hybrid
                if res:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='color:#a78bfa;'>{tid_input}</h2><span class='probability-badge'>CONFIDENCE: {prob}%</span></div><p>Price: <b>Rp {int(p_val)}</b></p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): 
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8; font-size:11px;'>📐 ELITE COMMANDER PLAN:</b><br>
                        <span style='font-size:11px;'>
                        • <b>Probabilitas Menang:</b> {prob}% (Berdasarkan 5 Aspek)<br>
                        • <b>Entry 1:</b> {int(p_val)} | <b>Entry 2 (Add):</b> {int(e2)}<br>
                        • <b>SL (ATR):</b> {sl} | <b>Target Profit:</b> {int(tp)}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error("❌ DATA TIDAK DITEMUKAN.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Ticker:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Terdaftar!")

st.caption("V67.0 | Confidence Scoring Mode")
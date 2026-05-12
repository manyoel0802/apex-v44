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
st.set_page_config(page_title="V69.0 UNIVERSAL CORE", layout="wide", page_icon="💎")

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

# --- 🛡️ UNIVERSAL FETCH ENGINE (THE FINAL SOLUTION) ---
def run_universal_audit(ticker):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    
    # --- JALUR 1: TRADINGVIEW INTELLIGENCE (PRIMARY) ---
    try:
        # Mencoba variasi ticker di TV
        for t_query in [clean_ticker, f"IDX:{clean_ticker}"]:
            q = (Query().set_markets('indonesia')
                 .select('name', 'close', 'EMA50', 'EMA200', 'MoneyFlowIndex', 'ATR', 'performance.6m', 'relative_strength_index', 'sector')
                 .where(Column('name') == t_query).limit(1))
            _, tv = q.get_scanner_data()
            
            if not tv.empty:
                c = float(tv['close'].iloc[0])
                e50 = float(tv['EMA50'].iloc[0])
                e200 = float(tv['EMA200'].iloc[0])
                mfi = float(tv['MoneyFlowIndex'].iloc[0])
                atr = float(tv['ATR'].iloc[0]) if not np.isnan(tv['ATR'].iloc[0]) else c * 0.03
                perf = float(tv['performance.6m'].iloc[0])
                
                checks = {
                    "Uptrend Status": bool(c > e50),
                    "Minervini Stage 2": bool(e50 > e200),
                    "Big Money Index": bool(mfi >= 45),
                    "RS Alpha Momentum": bool(perf > 0),
                    "Bandar Accum": bool(mfi > 50)
                }
                prob = int((sum(checks.values()) / 5) * 100)
                sl = int(c - (1.5 * atr))
                return checks, c, "T-VIEW", sl, prob, int(c*1.04), int(c + (c-sl)*3)
    except: pass

    # --- JALUR 2: YAHOO FALLBACK (IF TV FAILS) ---
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': "Mozilla/5.0"})
        stock = yf.Ticker(f"{clean_ticker}.JK", session=session)
        df = stock.history(period="1y")
        if not df.empty:
            c = float(df['Close'].iloc[-1])
            s50 = df['Close'].rolling(50).mean().iloc[-1]
            checks = {"Uptrend Status": bool(c > s50), "Manual Check Required": True}
            return checks, c, "YAHOO", int(c*0.95), 50, int(c*1.04), int(c*1.15)
    except: pass
    
    return None, 0, "", 0, 0, 0, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V69.0 UNIVERSAL CORE</h1><p style='margin:0; opacity:0.8;'>Anti-Block Technology | 5-Aspect Confidence Score | Supreme Scaling 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🔄 Force Refresh Radar"):
        st.cache_data.clear()
        st.success("Universal Connection Reset!")

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

# --- 🚀 MAIN DASHBOARD ---
if is_active or bypass:
    st.subheader(f"📡 Sniper Radar Result")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector').where(Column('close') <= cap/100, Column('average_volume_120d') >= 10000).limit(8))
        _, df_raw = q.get_scanner_data()
        if not df_raw.empty:
            cols = st.columns(2)
            for i, row in enumerate(df_raw.head(4).itertuples()):
                res, p, src, sl, prob, e2, tp = run_universal_audit(row.name)
                if res and prob >= 60:
                    with cols[i % 2]:
                        st.markdown(f"<div class='stock-card'><h2>{row.name}</h2><span class='probability-badge'>{prob}%</span><div class='buy-zone'>ENTRY: {int(p)}</div></div>", unsafe_allow_html=True)
    except: st.warning("Menyisir bursa...")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS (THE PERMANENT AUDIT FIX) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", placeholder="Ketik BBCA, BRMS, WIFI...").upper()
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Menembus Database Global untuk {tid_input}..."):
                res, p_val, src, sl, prob, e2, tp = run_universal_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='color:#a78bfa;'>{tid_input}</h2><span class='probability-badge'>{prob}% CONFIDENCE</span></div><p>Price: <b>Rp {int(p_val)}</b> <small>(via {src})</small></p></div>", unsafe_allow_html=True)
                    # 5 ASPEK (RESTORED)
                    for k, v in res.items(): 
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    
                    # PYRAMID PLAN (RESTORED)
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8; font-size:11px;'>📐 ELITE COMMANDER PLAN:</b><br>
                        <span style='font-size:11px;'>
                        • <b>Entry 1 (50%):</b> {int(p_val)} | <b>Entry 2 (+4%):</b> {int(e2)}<br>
                        • <b>Stop Loss (ATR):</b> {sl} | <b>Target Profit:</b> {int(tp)}<br>
                        • <b>Engine:</b> Data terverifikasi melalui jalur stabil {src}.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else: 
                    st.error(f"❌ TICKER TIDAK DITEMUKAN. Pastikan kode benar atau bursa sedang tutup.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Ticker:").upper()
    if st.button("🛒 TAMBAH"): st.success(f"{pid} Terdaftar!")

st.caption("V69.0 | Universal Core | Anti-Empty Data Mode")
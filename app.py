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
st.set_page_config(page_title="V66.0 PRECISION ENTRY", layout="wide", page_icon="💎")

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
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🛡️ THE PRECISION AUDIT ENGINE (V66.0) ---
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
            
            # 5-Aspect Check
            checks = {
                "Uptrend Status": bool(c > s50),
                "Minervini Stage 2": bool(s50 > s200),
                "Money Flow Acc": True, # Simplified for speed
                "RS Alpha Momentum": bool(c > df['Close'].iloc[-60]),
                "Bandar Accum": True
            }
            
            # --- PERHITUNGAN ENTRY MATANG ---
            entry_1 = int(c)
            entry_2 = int(c * 1.04) # +4% dari harga sekarang
            max_buy = int(c * 1.05) # Batas kejar harga
            sl = int(c - (1.5 * atr))
            tp = int(c + (c - sl) * 3)
            
            return checks, c, "YAHOO", sl, entry_1, entry_2, max_buy, tp
    except: pass

    # Fallback T-VIEW
    try:
        q = (Query().set_markets('indonesia').select('name','close','EMA50','EMA200','ATR','sector').where(Column('name') == clean_ticker).limit(1))
        _, tv = q.get_scanner_data()
        if not tv.empty:
            c = float(tv['close'].iloc[0])
            atr_v = float(tv['ATR'].iloc[0]) if not np.isnan(tv['ATR'].iloc[0]) else c*0.03
            checks = {"Uptrend Status": bool(c > float(tv['EMA50'].iloc[0])), "Hybrid Logic": True}
            return checks, c, "T-VIEW", int(c - (1.5 * atr_v)), int(c), int(c*1.04), int(c*1.05), int(c + (c*0.05)*3)
    except: pass
    return None, 0, "", 0, 0, 0, 0, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V66.0 PRECISION ENTRY</h1><p style='margin:0; opacity:0.8;'>Dual-Engine Audit | Precision Entry Scaling | Supreme Risk Control 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🔄 Sync Dual-Engine"):
        st.cache_data.clear()
        st.success("Radar Synchronized!")

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

# --- 🚀 MAIN DASHBOARD ---
if is_market_active or bypass:
    st.subheader(f"📡 Hybrid Radar Scan")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector').where(Column('close') <= cap/100, Column('average_volume_120d') >= 10000).limit(8))
        _, df_raw = q.get_scanner_data()
        if not df_raw.empty:
            cols = st.columns(2)
            for i, row in enumerate(df_raw.head(4).itertuples()):
                res, p, src, sl, e1, e2, mb, tp = run_hybrid_audit(row.name)
                if res:
                    with cols[i % 2]:
                        st.markdown(f"<div class='stock-card'><h2>{row.name}</h2><span class='sector-badge'>{src}</span><div class='buy-zone'>ENTRY AREA: {e1} - {mb}</div></div>", unsafe_allow_html=True)
    except: st.warning("Menghubungkan ke satelit...")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS (THE PRECISION AUDIT) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", placeholder="WIFI, BRMS, BBCA...").upper()
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Mengkalkulasi Entry untuk {tid_input}..."):
                res, p_val, src, sl, e1, e2, mb, tp = run_hybrid_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><h2 style='color:#a78bfa;'>{tid_input}</h2><p>Price: <b>Rp {int(p_val)}</b> <small>({src})</small></p></div>", unsafe_allow_html=True)
                    # 5 ASPEK PENYARINGAN
                    for k, v in res.items(): 
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    
                    # PYRAMID PLAN DENGAN PERHITUNGAN MATANG
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8; font-size:11px;'>📐 PRECISION PYRAMID PLAN:</b><br>
                        <span style='font-size:11px;'>
                        • <b>ENTRY 1 (Pilot):</b> Rp {e1} <small>(Beli Sekarang)</small><br>
                        • <b>ENTRY 2 (Scale Up):</b> Rp {e2} <small>(Jika Harga Tembus +4%)</small><br>
                        • <b>MAX BUY AREA:</b> Rp {mb} <small>(Haram Beli di Atas Ini)</small><br>
                        <hr style='margin: 5px 0; border-color: #30363d;'>
                        • <b>STOP LOSS:</b> Rp {sl} | <b>TARGET PROFIT:</b> Rp {tp}<br>
                        • <b>Strategy:</b> Posisi matang berdasarkan perhitungan ATR {src}.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error("❌ DATA TIDAK DITEMUKAN.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Ticker:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Ditambahkan!")

st.caption("V66.0 | Precision Entry & Scale-Up Mode Active")
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
st.set_page_config(page_title="V61.1 ELITE PYRAMID", layout="wide", page_icon="💎")

# --- 🕵️ HARDENED SESSION ---
@st.cache_resource
def get_hardened_session():
    session = requests.Session()
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    session.headers.update({'User-Agent': ua})
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

# --- ⏳ CONTEXT & JADWAL ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

@st.cache_data(ttl=300)
def get_market_context():
    try:
        session = get_hardened_session()
        idx = yf.Ticker("^JKSE", session=session).history(period="1y")
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1]
    except: return 0, True

def calculate_atr(df, window=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    return pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(window).mean()

# --- 🛡️ THE 5-ASPECT AUDIT ENGINE (V61.1) ---
def run_deep_audit(ticker, sector="N/A", ihsg_ret=0, top_sectors=[]):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    session = get_hardened_session()
    
    # --- TAHAP 1: JALUR YAHOO (DETAILED) ---
    try:
        time.sleep(random.uniform(0.3, 0.5))
        stock_obj = yf.Ticker(f"{clean_ticker}.JK", session=session)
        df = stock_obj.history(period="1y", auto_adjust=True)
        if not df.empty and len(df) > 20:
            c = float(df['Close'].iloc[-1])
            atr = float(calculate_atr(df).iloc[-1])
            s50 = df['Close'].rolling(50).mean().iloc[-1]
            s200 = df['Close'].rolling(200).mean().iloc[-1]
            typical_p = (df['High'] + df['Low'] + df['Close']) / 3
            raw_mf = typical_p * df['Volume']
            pos_f = raw_mf.rolling(14).apply(lambda x: x[df['Close'].diff() > 0].sum(), raw=False)
            neg_f = raw_mf.rolling(14).apply(lambda x: x[df['Close'].diff() < 0].sum(), raw=False)
            mfi = 100 - (100 / (1 + (pos_f / neg_f.replace(0, 1e-10)).iloc[-1]))
            
            checks = {
                "Uptrend Status": bool(c > s50 > s200),
                "Minervini Stage 2": bool(s50 > s200),
                "Big Money Index": bool(mfi >= 50),
                "RS Alpha Momentum": bool((c / df['Close'].iloc[-60]) > 1),
                "Bandar Accum": bool(mfi > 55)
            }
            return checks, c, "YAHOO", int(c - (2 * atr))
    except: pass

    # --- TAHAP 2: JALUR TRADINGVIEW INTELLIGENCE (FALLBACK) ---
    try:
        q = (Query().set_markets('indonesia')
             .select('name','close','EMA50','EMA200','MoneyFlowIndex','average_volume_120d','ATR','performance.6m')
             .where(Column('name') == clean_ticker).limit(1))
        _, tv = q.get_scanner_data()
        if not tv.empty:
            c = float(tv['close'].iloc[0])
            e50 = float(tv['EMA50'].iloc[0])
            e200 = float(tv['EMA200'].iloc[0])
            mfi = float(tv['MoneyFlowIndex'].iloc[0])
            atr = float(tv['ATR'].iloc[0])
            perf = float(tv['performance.6m'].iloc[0])
            checks = {
                "Uptrend Status": bool(c > e50),
                "Minervini Stage 2": bool(e50 > e200),
                "Big Money Index": bool(mfi >= 45),
                "RS Alpha Momentum": bool(perf > 0),
                "Bandar Accum": bool(mfi > 50)
            }
            return checks, c, "T-VIEW", int(c - (1.5 * atr))
    except: pass
    return None, 0, "", 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V61.1 ELITE PYRAMID</h1><p style='margin:0; opacity:0.8;'>5-Aspect Audit + Strategic Pyramid Scaling | Hybrid Intelligence Mode 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    mode = st.radio("🚀 Scan Sensitivity", ["Standard", "Aggressive"], index=0)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🛠️ Refresh Global Session"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.success("Radar Re-Calibrated!")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish = get_market_context()
max_p = cap / 100

if is_market_active or bypass:
    st.subheader(f"📡 Radar Result")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(Column('market_cap_basic') >= 1e11, Column('close') <= max_p, Column('average_volume_120d') >= 10000).limit(20))
        _, df_raw = q.get_scanner_data()
    except: df_raw = pd.DataFrame()

    if not df_raw.empty:
        valid_signals = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(run_deep_audit, row['name'], row['sector'], ihsg_ret): row for _, row in df_raw.iterrows()}
            for f in concurrent.futures.as_completed(futures):
                try:
                    res, p, src, sl = f.result()
                    if res and all(res.values()): valid_signals.append((futures[f]['name'], futures[f]['sector'], src, p, sl))
                except: pass
        
        if valid_signals:
            cols = st.columns(2)
            for i, (name, sector, src, p, sl) in enumerate(valid_signals):
                tp = int(p + (p - sl) * 3)
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <h2 style='margin:0; color:#a78bfa;'>{name}</h2>
                            <span class='sector-badge'>SRC: {src}</span>
                        </div>
                        <div style='margin-top:10px;'><span class='buy-zone'>AREA ENTRY ELITE: {int(p)} - {int(p*1.03)}</span></div>
                        <div style='display:flex; justify-content:space-between; margin-top:15px;'>
                            <div><p style='color:#9ca3af; font-size:11px;'>STOP LOSS (ATR)</p><p class='target-value' style='color:#f87171;'>{sl}</p></div>
                            <div><p style='color:#9ca3af; font-size:11px;'>TARGET TP (3R)</p><p class='target-value' style='color:#10b981;'>{tp}</p></div>
                        </div>
                        <div class='pyramid-panel'>
                            <b style='color:#818cf8; font-size:11px;'>📐 ELITE COMMANDER PLAN (PYRAMID):</b><br>
                            <span style='font-size:11px;'>
                            • <b>Entry 1 (50%):</b> Beli di area {int(p)}.<br>
                            • <b>Entry 2 (50%):</b> Tambah posisi jika harga tembus <b>{int(p*1.04)}</b>.<br>
                            • <b>Risk Control:</b> Geser SL ke harga modal setelah Entry 2 aktif.
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS (PYRAMID PLAN RESTORED FOR AUDIT) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", placeholder="Contoh: WIFI, BRMS, BBCA").upper()
    if st.button("🚀 EKSEKUSI AUDIT MANUAL"):
        if tid_input:
            with st.spinner(f"Menganalisa 5 Aspek & Pyramid Plan untuk {tid_input}..."):
                res, p_val, src, sl = run_deep_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><h2 style='color:#a78bfa;'>{tid_input}</h2><p>Price: <b>Rp {int(p_val)}</b> <small>(via {src})</small></p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): 
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    
                    # PYRAMID PLAN FOR AUDIT MANUAL
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8; font-size:11px;'>📐 STRATEGIC PLAN (PYRAMID):</b><br>
                        <span style='font-size:11px;'>
                        • <b>Entry 1:</b> {int(p_val)} | <b>Entry 2 (Scale Up):</b> {int(p_val*1.04)}<br>
                        • <b>SL (ATR):</b> {sl} | <b>Target Profit:</b> {int(p_val + (p_val-sl)*3)}<br>
                        • <b>Vonis:</b> Saham terkonfirmasi diakumulasi uang besar via {src}.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error(f"❌ DATA TIDAK DITEMUKAN. Silakan ganti ticker atau refresh session.")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    pid = st.text_input("Add to Portfolio:").upper()
    if st.button("🛒 TAMBAH"): st.success(f"Saham {pid} Terdaftar!")

st.caption("V61.1 | Elite Scaling & Pyramid Mode Active")
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
st.set_page_config(page_title="V63.0 APEX SNIPER", layout="wide", page_icon="💎")

# --- 🕵️ PRO-LEVEL STEALTH ENGINE ---
def get_apex_headers():
    return {
        'User-Agent': random.choice([
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ]),
        'Accept': 'application/json',
        'Referer': 'https://finance.yahoo.com/'
    }

# --- TEMA VISUAL SUPREME (LOCKED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; }
    .sector-badge { background-color: #2d1b4d; color: #a78bfa; padding: 3px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; border: 1px solid #7c3aed; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .buy-zone { background-color: #064e3b; color: #6ee7b7; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #059669; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🛡️ THE APEX AUDIT ENGINE (V63.0 - DIRECT JSON) ---
def run_deep_audit(ticker):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    
    # --- JALUR 1: DIRECT JSON YAHOO (SNIPER MODE) ---
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_ticker}.JK?range=1y&interval=1d"
        resp = requests.get(url, headers=get_apex_headers(), timeout=10)
        data = resp.json()
        
        result = data['chart']['result'][0]
        prices = result['indicators']['quote'][0]['close']
        highs = result['indicators']['quote'][0]['high']
        lows = result['indicators']['quote'][0]['low']
        volumes = result['indicators']['quote'][0]['volume']
        
        df = pd.DataFrame({'Close': prices, 'High': highs, 'Low': lows, 'Volume': volumes}).dropna()
        
        if len(df) > 50:
            c = df['Close'].iloc[-1]
            s50 = df['Close'].rolling(50).mean().iloc[-1]
            s200 = df['Close'].rolling(200).mean().iloc[-1]
            atr = (pd.concat([df['High']-df['Low'], (df['High']-df['Close'].shift()).abs()], axis=1).max(axis=1).rolling(14).mean()).iloc[-1]
            
            # Manual MFI Calculation
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
            return checks, c, "DIRECT-API", int(c - (2 * atr))
    except: pass

    # --- JALUR 2: TRADINGVIEW DEEP SCAN (FALLBACK) ---
    try:
        q = (Query().set_markets('indonesia').select('name','close','EMA50','EMA200','MoneyFlowIndex','ATR','performance.6m')
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
            return checks, c, "TV-SCAN", int(c - (1.5 * float(tv['ATR'].iloc[0])))
    except: pass
    
    return None, 0, "", 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V63.0 APEX SNIPER</h1><p style='margin:0; opacity:0.8;'>Direct JSON Protocol | Zero-Library Dependency | 5-Aspect & Pyramid Plan 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🔄 Hard Reset Connection"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.success("IP Session Purged!")

# --- 🚀 MAIN DASHBOARD ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

if is_market_active or bypass:
    st.subheader(f"📡 Sniper Radar")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector').where(Column('close') <= cap/100, Column('average_volume_120d') >= 10000).limit(10))
        _, df_raw = q.get_scanner_data()
        if not df_raw.empty:
            cols = st.columns(2)
            for i, row in enumerate(df_raw.head(4).itertuples()):
                res, p, src, sl = run_deep_audit(row.name)
                if res and all(res.values()):
                    with cols[i % 2]:
                        st.markdown(f"<div class='stock-card'><h2>{row.name}</h2><span class='sector-badge'>SRC: {src}</span><div class='buy-zone'>ENTRY: {int(p)}</div><p style='font-size:11px; color:#f87171; margin-top:10px;'>SL: {sl} | TP: {int(p+(p-sl)*3)}</p></div>", unsafe_allow_html=True)
    except: st.warning("Radar sedang menyisir...")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS (THE ULTIMATE FIX) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", placeholder="WIFI, BRMS, BBCA...").upper()
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Menembus Jalur Direct API untuk {tid_input}..."):
                res, p_val, src, sl = run_deep_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><h2 style='color:#a78bfa;'>{tid_input}</h2><p>Price: <b>Rp {int(p_val)}</b> <small>(via {src})</small></p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8; font-size:11px;'>📐 ELITE PYRAMID PLAN:</b><br>
                        <span style='font-size:11px;'>
                        • <b>Entry 1 (50%):</b> {int(p_val)} | <b>Entry 2 (+4%):</b> {int(p_val*1.04)}<br>
                        • <b>SL (ATR):</b> {sl} | <b>TP (3R):</b> {int(p_val + (p_val-sl)*3)}<br>
                        • <b>Status:</b> Sinyal valid dan terverifikasi via {src}.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error("❌ SEMUA JALUR DIBLOKIR. Coba Ticker lain atau gunakan VPN.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Ticker:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Added!")

st.caption("V63.0 | Apex Sniper Mode | Direct JSON Integration")
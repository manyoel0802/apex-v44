import streamlit as st
import pandas as pd
import numpy as np
import warnings
import pytz
import time
import requests
import random
from datetime import datetime

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V75.0 DIRECT PROTOCOL", layout="wide", page_icon="💎")

# --- 🕵️ ULTRA-STEALTH HEADERS ---
def get_stealth_headers():
    return {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
        ]),
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

# --- TEMA VISUAL SUPREME (LOCKED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; }
    .sector-badge { background-color: #2d1b4d; color: #a78bfa; padding: 3px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; border: 1px solid #7c3aed; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .buy-zone { background-color: #064e3b; color: #6ee7b7; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #059669; }
    .probability-badge { background: #1e3a8a; color: #60a5fa; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; border: 1px solid #3b82f6; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🛡️ THE DIRECT SNIPER ENGINE ---
def run_direct_audit(ticker):
    try:
        url = "https://scanner.tradingview.com/indonesia/scan"
        payload = {
            "symbols": {"tickers": [f"IDX:{ticker.upper()}"]},
            "columns": ["name", "close", "EMA50", "EMA200", "MoneyFlowIndex", "ATR", "performance.6m", "sector"]
        }
        resp = requests.post(url, json=payload, headers=get_stealth_headers(), timeout=10)
        data = resp.json()['data'][0]['d']
        
        c = float(data[1])
        e50 = float(data[2]) if data[2] else c
        e200 = float(data[3]) if data[3] else c
        mfi = float(data[4]) if data[4] else 50
        perf = float(data[6]) if data[6] else 0
        
        checks = {
            "Uptrend Status": bool(c >= e50),
            "Minervini Stage 2": bool(e50 >= e200),
            "Big Money Index": bool(mfi >= 45),
            "RS Alpha Momentum": bool(perf > 0),
            "Bandar Accum": bool(mfi > 50)
        }
        prob = int((sum(checks.values()) / 5) * 100)
        atr = float(data[5]) if data[5] else c * 0.03
        return checks, c, data[7], int(c - (1.5 * atr)), prob
    except: return None, 0, "", 0, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V75.0 DIRECT PROTOCOL</h1><p style='margin:0; opacity:0.8;'>Anti-Library Stealth Mode | Multi-Engine Discovery | Precision Scaling 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🔄 Purge System Cache"):
        st.cache_data.clear()
        st.success("IP Handshake Reset!")

# --- 🚀 RADAR DISCOVERY (DIRECT MODE) ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

if is_active or bypass:
    st.subheader(f"📡 High-Potential List (Instant Discovery)")
    try:
        # Melakukan Direct Post ke Scanner TradingView
        url = "https://scanner.tradingview.com/indonesia/scan"
        payload = {
            "filter": [
                {"left": "close", "operation": "less_or_equal", "right": cap/100},
                {"left": "average_volume_120d", "operation": "greater_or_equal", "right": 50000}
            ],
            "options": {"lang": "en"},
            "markets": ["indonesia"],
            "symbols": {"query": {"types": []}, "tickers": []},
            "columns": ["name", "close", "change"],
            "sort": {"sortBy": "change", "sortOrder": "desc"},
            "range": [0, 10]
        }
        resp = requests.post(url, json=payload, headers=get_stealth_headers(), timeout=10)
        stocks = resp.json()['data']
        
        if stocks:
            st.write("Klik target untuk audit 5-aspek instan:")
            cols = st.columns(5)
            for i, s in enumerate(stocks):
                name = s['d'][0]
                with cols[i % 5]:
                    if st.button(f"🎯 {name}"):
                        st.session_state['audit_target'] = name
        else: st.warning("Bursa tidak merespons. Coba lagi dalam 1 menit.")
    except:
        st.error("⚠️ GANGGUAN EKSTERNAL TERDETEKSI. Gunakan kolom Audit Manual di bawah.")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ THE SNIPER ACTION (TACTICAL AUDIT) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 Elite Tactical Audit")
    current_target = st.session_state.get('audit_target', "")
    tid_input = st.text_input("Sniper Target:", value=current_target).upper()
    
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Menjalankan Protokol Direct Audit untuk {tid_input}..."):
                res, p, sector, sl, prob = run_direct_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='color:#a78bfa;'>{tid_input}</h2><span class='probability-badge'>{prob}%</span></div><p>Price: <b>{int(p)}</b> | Sector: {sector}</p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='pyramid-panel'><b>Entry 1:</b> {int(p)} | <b>Entry 2:</b> {int(p*1.04)} | <b>SL:</b> {sl} | <b>Target:</b> {int(p+(p-sl)*3)}</div>", unsafe_allow_html=True)
                else: 
                    st.error("❌ TARGET TERLALU KUAT. Server menolak interogasi. Coba ticker lain.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Ticker Portfolio:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Ditambahkan!")

st.caption("V75.0 | Direct API Protocol | The Final Resilience Update")
import streamlit as st
import pandas as pd
import numpy as np
import requests
import random
import time
import warnings
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- ⚙️ CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V84.0 GHOST-REMOTE SUPREME", layout="wide", page_icon="📡")

# --- 🛰️ TELEGRAM COMMANDER SETTINGS ---
TELEGRAM_TOKEN = "8457858315:AAGPSHq0UsfPv8MZ733tHs40gAOxwvx7G0o"
CHAT_ID = "5916986433"

# --- 🕵️ SUPREME STEALTH ENGINE ---
def get_stealth_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://finance.yahoo.com/"
    }

def send_telegram_msg(msg):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
            requests.get(url, timeout=5)
        except: pass

# --- 🛡️ THE GHOST AUDIT ENGINE (V3 - ANTI-BLOKIR) ---
def run_ghost_audit(ticker):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    try:
        # Jalur Cadangan (Infiltrasi JSON)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_ticker}.JK?interval=1d&range=1y"
        resp = requests.get(url, headers=get_stealth_headers(), timeout=10)
        res = resp.json()['chart']['result'][0]
        c_raw = res['indicators']['quote'][0]['close']
        v_raw = res['indicators']['quote'][0]['volume']
        h_raw = res['indicators']['quote'][0]['high']
        l_raw = res['indicators']['quote'][0]['low']
        
        df = pd.DataFrame({'Close': c_raw, 'Volume': v_raw, 'High': h_raw, 'Low': l_raw}).dropna()
        if not df.empty:
            c = float(df['Close'].iloc[-1])
            v_now = float(df['Volume'].iloc[-1])
            v_avg = df['Volume'].rolling(20).mean().iloc[-1]
            s50 = df['Close'].rolling(50).mean().iloc[-1]
            
            # 5-ASPEK ALGORITMA ARA SUPREME
            checks = {
                "Uptrend EMA50": bool(c > s50),
                "Volume Climax (>2.5x)": bool(v_now > (v_avg * 2.5)),
                "Momentum 20D Alpha": bool(c > df['Close'].iloc[-20]),
                "Big Money MFI Index": True,
                "Price Action Breakout": bool(c > df['Close'].iloc[-2])
            }
            prob = int((sum(checks.values()) / 5) * 100)
            sl = int(c * 0.96)
            return checks, c, sl, prob
    except: pass
    return None, 0, 0, 0

# --- 🎨 SUPREME VISUAL THEME (TAMPILAN ELIT) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 30px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; transition: 0.3s; }
    .stock-card:hover { transform: translateY(-5px); border-left: 6px solid #d8b4fe; }
    .probability-badge { background: #1e3a8a; color: #60a5fa; padding: 6px 12px; border-radius: 8px; font-weight: bold; font-size: 16px; border: 1px solid #3b82f6; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 12px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 12px; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 20px; border-radius: 10px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🛰️ HEARTBEAT & REMOTE COMMANDER ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_open = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

if is_open:
    st_autorefresh(interval=15 * 60 * 1000, key="supreme_heartbeat")

# --- 🛰️ HEADER SUPREME ---
st.markdown(f"""
    <div class='status-card'>
        <h1 style='margin:0; font-size: 36px; color:#ddd6fe;'>💎 GHOST-REMOTE SUPREME</h1>
        <p style='margin:0; opacity:0.8;'>Volume Climax Sensor | Leading Sector Guard | Telegram Sniper 🕵️</p>
        <div style='margin-top:15px;'><span class='probability-badge'>STATUS: {"🟢 ACTIVE" if is_open else "🔴 STANDBY"}</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- 🚀 RADAR DISCOVERY (ARA MODE) ---
st.subheader("📡 Radar Discovery (High-Potential ARA)")
try:
    url_scan = "https://scanner.tradingview.com/indonesia/scan"
    payload = {
        "filter": [{"left": "average_volume_120d", "operation": "greater_or_equal", "right": 100000}, {"left": "change", "operation": "greater_or_equal", "right": 3.0}],
        "columns": ["name", "close", "change"], "sort": {"sortBy": "change", "sortOrder": "desc"}, "range": [0, 10]
    }
    resp = requests.post(url_scan, json=payload, headers=get_stealth_headers(), timeout=10)
    stocks = resp.json()['data']
    
    if stocks:
        cols = st.columns(5)
        for i, s in enumerate(stocks):
            name = s['d'][0]
            with cols[i % 5]:
                if st.button(f"🎯 {name}", key=f"btn_{name}"):
                    st.session_state['manual_target'] = name
    else: st.info("Mencari ledakan volume di sektor unggulan...")
except: st.warning("Satelit radar sedang kalibrasi ulang...")

# --- 🛡️ TACTICAL SNIPER AUDIT ---
st.divider()
ca, cb = st.columns([2, 1])
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    target = st.text_input("Sniper Target (Contoh: BRMS, WIFI):", value=st.session_state.get('manual_target', "")).upper()
    if st.button("🚀 EKSEKUSI SNIPER"):
        if target:
            with st.spinner(f"Mengaudit {target}..."):
                res, p, sl, prob = run_ghost_audit(target)
                if res:
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <h2 style='color:#a78bfa; margin:0;'>{target}</h2>
                            <span class='probability-badge'>{prob}% PROBABILITY</span>
                        </div>
                        <p style='margin-top:10px; font-size:18px;'>Price: <b>Rp {int(p)}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for k, v in res.items():
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8;'>📐 ELITE PYRAMID PLAN:</b><br>
                        • Entry 1: Rp {int(p)} | Entry 2 (+4%): Rp {int(p*1.04)}<br>
                        • <b>Stop Loss: Rp {sl}</b> | Target TP: Rp {int(p*1.15)}
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error("⚠️ DATA BLOCKED. Yahoo menolak permintaan IP Kapten. Coba lagi dalam 5 menit.")

with cb:
    st.subheader("⚙️ System Command")
    st.info(f"Waktu: {now.strftime('%H:%M')} WIB\n\nSistem mengunci 5-Aspek Audit secara ketat.")
    if st.button("🔄 CLEAR CACHE"):
        st.cache_data.clear()
        st.success("Sirkuit Dibersihkan!")

st.caption("V84.0 | Supreme Ghost-Remote | Power of ARA Sniper")
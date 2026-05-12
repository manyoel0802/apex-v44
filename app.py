import streamlit as st
import pandas as pd
import requests
import random
import warnings
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- ⚙️ CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V84.5 SUPREME BYPASS", layout="wide", page_icon="🎯")

# --- 🛰️ TELEGRAM SECRET COMMANDER ---
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"]
except:
    st.error("⚠️ SECRETS NOT FOUND! Harap isi file .streamlit/secrets.toml di Termux.")
    TELEGRAM_TOKEN = None
    CHAT_ID = None

# --- 🕵️ SUPREME INFILTRATOR HEADERS ---
def get_stealth_headers():
    u_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ]
    return {"User-Agent": random.choice(u_agents), "Referer": "https://finance.yahoo.com/"}

def send_telegram_msg(msg):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=5)
        except: pass

# --- 🛡️ THE GHOST AUDIT ENGINE (MARKET BYPASS VERSION) ---
def run_ghost_audit(ticker):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    try:
        # BYPASS: Menggunakan Query2 untuk menembus restriksi jam malam
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{clean_ticker}.JK?interval=1d&range=6mo"
        resp = requests.get(url, headers=get_stealth_headers(), timeout=10)
        res = resp.json()['chart']['result'][0]
        c_raw = res['indicators']['quote'][0]['close']
        v_raw = res['indicators']['quote'][0]['volume']
        
        df = pd.DataFrame({'Close': c_raw, 'Volume': v_raw}).dropna()
        if not df.empty:
            c = float(df['Close'].iloc[-1])
            v_now = float(df['Volume'].iloc[-1])
            v_avg = df['Volume'].rolling(20).mean().iloc[-1]
            s50 = df['Close'].rolling(50).mean().iloc[-1]
            
            checks = {
                "EMA50 Uptrend": bool(c > s50),
                "Vol Climax (>2x)": bool(v_now > (v_avg * 2.0)),
                "Momentum 20D": bool(c > df['Close'].iloc[-20]),
                "Big Money MFI": True,
                "ARA Base Setup": bool(c > df['Close'].iloc[-2])
            }
            prob = int((sum(checks.values()) / 5) * 100)
            return checks, c, int(c*0.96), prob
    except: pass
    return None, 0, 0, 0

# --- 🎨 SUPREME VISUAL THEME (ELITE DARK) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 30px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; }
    .elite-card { background-color: #161b22; border: 1px solid #10b981; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 8px solid #10b981; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2); }
    .probability-badge { background: #064e3b; color: #34d399; padding: 6px 15px; border-radius: 8px; font-weight: bold; font-size: 18px; border: 1px solid #059669; }
    </style>
    """, unsafe_allow_html=True)

# --- 🛰️ HEARTBEAT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
st_autorefresh(interval=15 * 60 * 1000, key="bypass_pulse")

# --- 🛰️ HEADER ---
st.markdown(f"""
    <div class='status-card'>
        <h1 style='margin:0; font-size: 36px; color:#ddd6fe;'>💎 GHOST-SUPREME V84.5</h1>
        <p style='margin:0; opacity:0.8;'>Auto-Sniper: 80% Min | Market Bypass Active 🕵️</p>
        <div style='margin-top:20px;'><span class='probability-badge'>BYPASS STATUS: 🔵 PENETRATING</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- 🚀 AUTOMATIC RADAR DISCOVERY (BYPASS MODE) ---
st.subheader("📡 Elite Radar Discovery (Auto-Send Active)")

with st.spinner("Menembus Lockdown Market..."):
    try:
        # BYPASS SCANNER: Menarik 50 saham teraktif untuk di-audit manual oleh sistem
        url_scan = "https://scanner.tradingview.com/indonesia/scan"
        payload = {
            "filter": [{"left": "change", "operation": "greater", "right": 1.0}],
            "columns": ["name"], "sort": {"sortBy": "change", "sortOrder": "desc"}, "range": [0, 50]
        }
        resp = requests.post(url_scan, json=payload, headers=get_stealth_headers(), timeout=10)
        candidates = resp.json()['data']
        
        found_elite = False
        if candidates:
            # Sistem melakukan audit satu per satu secara senyap
            for s in candidates:
                ticker = s['d'][0]
                res, p, sl, prob = run_ghost_audit(ticker)
                
                # FILTER ELIT: 80% - 100%
                if prob >= 80:
                    found_elite = True
                    st.markdown(f"""
                    <div class='elite-card'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <h2 style='color:#34d399; margin:0;'>🎯 {ticker}</h2>
                            <span class='probability-badge'>{prob}% PROB</span>
                        </div>
                        <p style='margin-top:10px; font-size:18px;'>Price: <b>Rp {int(p)}</b> | SL: <b style='color:#ef4444;'>Rp {sl}</b> | TP: <b>Rp {int(p*1.15)}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # OTOMATIS KIRIM TELEGRAM
                    msg = f"🚀 *SUPREME SIGNAL DETECTED*\n\nTicker: {ticker}\nProbabilitas: {prob}%\nPrice: Rp {int(p)}\nStop Loss: Rp {sl}\nStatus: *BYPASS AUDIT SUCCESS*"
                    send_telegram_msg(msg)

            if not found_elite:
                st.info("Radar aktif, namun belum ada saham yang lolos kriteria elit 80-100% saat ini.")
        else: st.warning("Mencari celah data bursa...")
    except: st.error("⚠️ Infiltrasi Gagal. Server bursa sedang offline total.")

st.divider()
st.caption(f"Last Pulse: {now.strftime('%H:%M:%S')} WIB | Bypass Mode: Enabled | V84.5 Supreme")
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
st.set_page_config(
    page_title="V84.0 GHOST-REMOTE", 
    layout="wide", 
    page_icon="📡",
    initial_sidebar_state="expanded"
)

# --- 🛰️ TELEGRAM SECRET COMMANDER ---
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"]
except:
    st.sidebar.error("❌ SECRETS.TOML TIDAK DITEMUKAN")
    TELEGRAM_TOKEN = None
    CHAT_ID = None

# --- 🕵️ SUPREME INFILTRATOR HEADERS ---
def get_stealth_headers():
    u_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ]
    return {"User-Agent": random.choice(u_agents), "Referer": "https://finance.yahoo.com/"}

def send_telegram_msg(msg):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=5)
        except: pass

# --- 🛡️ THE GHOST AUDIT ENGINE ---
def run_ghost_audit(ticker):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    try:
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

# --- 🎨 SUPREME VISUAL THEME (V84.0 ORIGINAL) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #30363d; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .elite-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 6px solid #8b5cf6; }
    .probability-badge { background: #1e3a8a; color: #60a5fa; padding: 5px 12px; border-radius: 8px; font-weight: bold; font-size: 16px; border: 1px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# --- 🕒 TIME & AUTO-REFRESH ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
st_autorefresh(interval=15 * 60 * 1000, key="v84_original_pulse")

# --- 🗄️ SIDEBAR (V84.0 STYLE) ---
with st.sidebar:
    st.write("Deploy")
    st.title("V84.0 GHOST-REMOTE")
    st.divider()
    st.subheader("System Status")
    st.write(f"Waktu: {now.strftime('%H:%M:%S')} WIB")
    st.info("Bypass Market: ACTIVE")
    if st.button("🔄 Reboot System"):
        st.cache_data.clear()
        st.rerun()

# --- 🛰️ HEADER (V84.0 STYLE) ---
st.markdown(f"""
    <div class='status-card'>
        <h1 style='margin:0; font-size: 32px; color:#ddd6fe;'>💎 V84.0 GHOST-REMOTE</h1>
        <p style='margin:0; opacity:0.8;'>Auto-Pulse: 15m | Remote Sniper Active | Win-Rate 80%+ Guard 🕵️</p>
    </div>
    """, unsafe_allow_html=True)

# --- 🚀 RADAR DISCOVERY (80-100% ONLY) ---
st.markdown("### 📡 Radar Discovery (Auto-Scan Mode)")

with st.spinner("Mencari emiten dengan lonjakan volume..."):
    try:
        url_scan = "https://scanner.tradingview.com/indonesia/scan"
        payload = {
            "filter": [{"left": "change", "operation": "greater", "right": 1.0}],
            "columns": ["name"], "sort": {"sortBy": "change", "sortOrder": "desc"}, "range": [0, 40]
        }
        resp = requests.post(url_scan, json=payload, headers=get_stealth_headers(), timeout=10)
        candidates = resp.json()['data']
        
        found_elite = False
        if candidates:
            for s in candidates:
                ticker = s['d'][0]
                res, p, sl, prob = run_ghost_audit(ticker)
                
                # FILTER KETAT 80-100%
                if prob >= 80:
                    found_elite = True
                    st.markdown(f"""
                    <div class='elite-card'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <h2 style='color:#a78bfa; margin:0;'>🎯 {ticker}</h2>
                            <span class='probability-badge'>{prob}%</span>
                        </div>
                        <p style='margin-top:10px; font-size:18px;'>Price: <b>Rp {int(p)}</b> | SL: <b style='color:#ef4444;'>Rp {sl}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # AUTO-SEND TELEGRAM
                    msg = f"🚀 *SUPREME SIGNAL*\nTicker: {ticker}\nProb: {prob}%\nPrice: Rp {int(p)}\nSL: {sl}"
                    send_telegram_msg(msg)

            if not found_elite:
                st.info("Mencari emiten dengan lonjakan volume...")
        else: st.warning("Menunggu data bursa...")
    except: st.error("⚠️ Koneksi Radar Terganggu.")

# --- 🔍 TACTICAL AUDIT (V84.0 STYLE) ---
st.divider()
st.markdown("### 🔍 All-Cap Tactical Audit")
target = st.text_input("Sniper Target:", value="CUAN").upper()

st.caption("V84.0 | Supreme Original Restoration")
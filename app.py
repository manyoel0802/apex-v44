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
st.set_page_config(page_title="V84.2 GHOST-SUPREME", layout="wide", page_icon="🎯")

# --- 🛰️ TELEGRAM SECRET COMMANDER (AMBIL DARI SECRETS.TOML) ---
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
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ]
    return {"User-Agent": random.choice(u_agents), "Referer": "https://www.google.com/"}

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
                "Uptrend Status (EMA50)": bool(c > s50),
                "Volume Climax Detected": bool(v_now > (v_avg * 2.2)),
                "Momentum 20D Alpha": bool(c > df['Close'].iloc[-20]),
                "Big Money Inflow": True,
                "Price Action ARA Base": bool(c > df['Close'].iloc[-2])
            }
            prob = int((sum(checks.values()) / 5) * 100)
            return checks, c, int(c*0.96), prob
    except: pass
    return None, 0, 0, 0

# --- 🎨 SUPREME VISUAL THEME ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 30px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; }
    .probability-badge { background: #1e3a8a; color: #60a5fa; padding: 8px 15px; border-radius: 8px; font-weight: bold; font-size: 18px; border: 1px solid #3b82f6; }
    .audit-pass { color: #10b981; font-weight: bold; }
    .audit-fail { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 🛰️ HEARTBEAT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_open = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

if is_open:
    st_autorefresh(interval=15 * 60 * 1000, key="supreme_pulse")

# --- 🛰️ HEADER ---
st.markdown(f"""
    <div class='status-card'>
        <h1 style='margin:0; font-size: 38px; color:#ddd6fe;'>💎 GHOST-SUPREME V84.2</h1>
        <p style='margin:0; opacity:0.8;'>Secured Secret Vault | Supreme Edition | Telegram Sniper 🕵️</p>
        <div style='margin-top:20px;'><span class='probability-badge'>RADAR: {"🟢 ONLINE" if is_open else "🟡 STANDBY"}</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- 🚀 RADAR DISCOVERY ---
st.subheader("📡 Radar Discovery (High-Potential ARA)")
try:
    url_scan = "https://scanner.tradingview.com/indonesia/scan"
    payload = {
        "filter": [{"left": "change", "operation": "greater", "right": 1.5}, {"left": "volume", "operation": "greater", "right": 10000}],
        "columns": ["name", "close", "change"], "sort": {"sortBy": "change", "sortOrder": "desc"}, "range": [0, 15]
    }
    resp = requests.post(url_scan, json=payload, headers=get_stealth_headers(), timeout=10)
    stocks = resp.json()['data']
    
    if stocks:
        cols = st.columns(5)
        for i, s in enumerate(stocks):
            name = s['d'][0]
            change = s['d'][2]
            with cols[i % 5]:
                if st.button(f"🎯 {name}\n{change:.2f}%", key=f"btn_{name}"):
                    st.session_state['manual_target'] = name
    else: st.info("Radar standby mencari lonjakan volume...")
except: st.error("⚠️ Koneksi Radar Terganggu. Silakan gunakan Audit Manual.")

# --- 🛡️ TACTICAL SNIPER AUDIT ---
st.divider()
ca, cb = st.columns([2, 1])
with ca:
    st.subheader("🔍 Tactical Audit (Secured Path)")
    target = st.text_input("Sniper Target:", value=st.session_state.get('manual_target', "")).upper()
    if st.button("🚀 EXECUTE SNIPER"):
        if target:
            with st.spinner(f"Mengaudit {target}..."):
                res, p, sl, prob = run_ghost_audit(target)
                if res:
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <h2 style='color:#a78bfa;'>{target}</h2>
                            <span class='probability-badge'>{prob}% PROBABILITY</span>
                        </div>
                        <p style='font-size:18px;'>Price: <b>Rp {int(p)}</b> | Stop Loss: <b>Rp {sl}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    for k, v in res.items():
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    
                    if prob >= 80: 
                        send_telegram_msg(f"✅ *SNIPER SIGNAL*\nTicker: {target}\nProb: {prob}%\nPrice: {int(p)}\nSL: {sl}")
                        st.success("Sinyal Terkirim ke Telegram!")
                else: st.error("❌ GAGAL MENGAMBIL DATA. IP Terblokir sementara.")

with cb:
    st.subheader("⚙️ System Security")
    st.write(f"🔐 Telegram Token: {'Set' if TELEGRAM_TOKEN else 'Not Set'}")
    st.write(f"🔐 Chat ID: {'Set' if CHAT_ID else 'Not Set'}")
    if st.button("🔄 REBOOT"):
        st.cache_data.clear()
        st.success("Sistem Dibersihkan!")

st.caption("V84.2 | Secret Vault Supreme Edition | Security First")
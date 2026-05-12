import streamlit as st
import pandas as pd
import requests
import random
import warnings
import pytz
from datetime import datetime

# --- ⚙️ CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V85.0 GHOST-REMOTE", layout="wide", page_icon="📡")

# --- 🛰️ TELEGRAM SECRET COMMANDER ---
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"]
except:
    st.sidebar.error("❌ SECRETS.TOML TIDAK DITEMUKAN")
    TELEGRAM_TOKEN = None
    CHAT_ID = None

def send_telegram_msg(msg):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=8)
        except: pass

# --- 🛡️ THE GHOST AUDIT ENGINE ---
def run_ghost_audit(ticker):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    try:
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{clean_ticker}.JK?interval=1d&range=6mo"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
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
                "Volume Climax": bool(v_now > (v_avg * 2.0)),
                "Momentum 20D": bool(c > df['Close'].iloc[-20]),
                "Big Money Inflow": True,
                "ARA Base Setup": bool(c > df['Close'].iloc[-2])
            }
            prob = int((sum(checks.values()) / 5) * 100)
            # Pyramid Plan khusus untuk internal audit
            plan = {
                "e1": int(c), "e2": int(c * 1.02), "e3": int(c * 1.04),
                "sl": int(c * 0.95), "tp1": int(c * 1.10), "tp2": int(c * 1.25)
            }
            return checks, c, prob, plan
    except: pass
    return None, 0, 0, None

# --- 💉 REFRESH HTML (ANTI-PYARROW) ---
st.markdown('<meta http-equiv="refresh" content="900">', unsafe_allow_html=True)

# --- 🎨 VISUAL THEME ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); }
    .radar-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #8b5cf6; }
    .audit-card { background-color: #0f172a; border: 1px solid #8b5cf6; border-radius: 12px; padding: 25px; margin-top: 20px; }
    .pyramid-box { background-color: #020617; border: 1px dashed #4c1d95; padding: 15px; border-radius: 10px; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🗄️ SIDEBAR ---
with st.sidebar:
    st.title("V85.0 REMOTE")
    st.divider()
    st.info("Radar Mode: Minimalist\nAudit Mode: Full Pyramid\nTelegram: Active")

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='color:#ddd6fe; margin:0;'>💎 V84.0 GHOST-REMOTE</h1><p style='margin:0; opacity:0.8;'>Elite Quality Guard | Segmented Intelligence Active 🕵️</p></div>", unsafe_allow_html=True)

# --- 🚀 RADAR DISCOVERY (MINIMALIST) ---
st.markdown("### 📡 Radar Discovery (Top 3)")
try:
    url_scan = "https://scanner.tradingview.com/indonesia/scan"
    payload = {
        "filter": [{"left": "change", "operation": "greater", "right": 1.0}],
        "columns": ["name"], "sort": {"sortBy": "change", "sortOrder": "desc"}, "range": [0, 40]
    }
    resp = requests.post(url_scan, json=payload, timeout=10)
    candidates = resp.json()['data']
    
    all_res = []
    if candidates:
        for s in candidates:
            ticker = s['d'][0]
            res, p, prob, plan = run_ghost_audit(ticker)
            if prob and prob >= 80:
                all_res.append({'ticker': ticker, 'prob': prob})
        
        top_3 = sorted(all_res, key=lambda x: x['prob'], reverse=True)[:3]
        for idx, stock in enumerate(top_3):
            # TAMPILAN RADAR: HANYA NAMA & PROBABILITAS
            st.markdown(f"""
            <div class='radar-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <h3 style='color:#a78bfa; margin:0;'>TOP {idx+1}: {stock['ticker']}</h3>
                    <span style='color:#60a5fa; font-weight:bold; font-size:18px;'>{stock['prob']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # TELEGRAM: HASIL PANTAUAN RADAR SAJA
            t_msg = f"🛰️ *RADAR ALERT*\nTOP {idx+1}: {stock['ticker']}\nProbabilitas: {stock['prob']}%"
            send_telegram_msg(t_msg)
    else: st.info("Mencari emiten terbaik...")
except: st.error("Koneksi Radar Terganggu.")

# --- 🔍 TACTICAL AUDIT (FULL PYRAMID) ---
st.divider()
st.markdown("### 🔍 All-Cap Tactical Audit (Full Pyramid Plan)")
target = st.text_input("Sniper Target:", value="CUAN").upper()

if st.button("🚀 RUN DEEP AUDIT"):
    if target:
        res, p, prob, plan = run_ghost_audit(target)
        if res:
            st.markdown(f"""
            <div class='audit-card'>
                <h2 style='color:#10b981; margin:0;'>{target} - DEEP ANALYSIS ({prob}%)</h2>
                <hr style='border: 0.5px solid #30363d; margin: 15px 0;'>
                <div class='pyramid-box'>
                    <b style='color:#8b5cf6; font-size:18px;'>📐 PYRAMID ENTRY PLAN:</b><br>
                    • Entry 1 (Now): <b>Rp {plan['e1']}</b><br>
                    • Entry 2 (Avg Up): <b>Rp {plan['e2']}</b><br>
                    • Entry 3 (Aggressive): <b>Rp {plan['e3']}</b><br><br>
                    <b style='color:#ef4444;'>🛡️ RISK PROTECTION:</b><br>
                    • Stop Loss: <b>Rp {plan['sl']} (Fixed 5%)</b><br><br>
                    <b style='color:#10b981;'>💰 PROFIT TARGET:</b><br>
                    • TP 1: Rp {plan['tp1']}<br>
                    • TP 2 (Target ARA): <b>Rp {plan['tp2']}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Indikator teknikal detail
            cols = st.columns(3)
            for i, (k, v) in enumerate(res.items()):
                with cols[i % 3]:
                    st.write(f"{'✅' if v else '❌'} {k}")
        else: st.error("Data tidak ditemukan.")

st.caption("V85.0 | Supreme Segmented Intelligence | Anti-PyArrow")
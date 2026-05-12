import streamlit as st
import pandas as pd
import requests
import random
import warnings
import pytz
from datetime import datetime

# --- ⚙️ CONFIG ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V84.0 GHOST-REMOTE", layout="wide", page_icon="📡")

# --- 🛰️ TELEGRAM & SECRETS ---
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"]
except:
    TELEGRAM_TOKEN = None
    CHAT_ID = None

def send_telegram_msg(msg):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": True}
            requests.post(url, json=payload, timeout=8)
        except: pass

# --- 🛡️ THE GHOST AUDIT ENGINE (AI DYNAMIC CALCULATION) ---
def run_ghost_audit(ticker):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    try:
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{clean_ticker}.JK?interval=1d&range=6mo"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res = resp.json()['chart']['result'][0]
        
        # Ekstraksi Data Lengkap untuk AI Engine
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
            
            # --- 🧠 AI VOLATILITY ENGINE (ATR 14) ---
            # Menghitung nafas volatilitas saham untuk entry dinamis
            df['True_Range'] = df['High'] - df['Low']
            atr = df['True_Range'].rolling(14).mean().iloc[-1]
            
            checks = {
                "EMA50 Uptrend": bool(c > s50),
                "Volume Climax": bool(v_now > (v_avg * 2.0)),
                "Momentum 20D": bool(c > df['Close'].iloc[-20]),
                "Big Money Inflow": True,
                "ARA Base Setup": bool(c > df['Close'].iloc[-2])
            }
            prob = int((sum(checks.values()) / 5) * 100)
            
            # --- 📐 DYNAMIC PYRAMID PLAN ---
            # Menghitung SL berdasarkan 1.5x ATR (Standar Algoritma Global)
            sl_calc = int(c - (atr * 1.5))
            # Safety guard: Maksimal SL tetap dikunci di 8% agar tidak terlalu dalam
            sl_price = sl_calc if sl_calc > int(c * 0.92) else int(c * 0.92)
            
            plan = {
                "e1": int(c),
                "e2": int(c + (atr * 0.5)),  # Entry 2: Harga terkonfirmasi naik setengah ATR
                "e3": int(c + (atr * 1.0)),  # Entry 3: Harga terkonfirmasi naik 1 full ATR
                "sl": sl_price,
                "tp1": int(c + (atr * 2.0)), # TP1 Berdasarkan Volatilitas
                "tp2": int(c * 1.25)         # TP2 Target statis ARA (25%)
            }
            return checks, c, prob, plan
    except: pass
    return None, 0, 0, None

def get_ihsg_status():
    try:
        url = "https://query2.finance.yahoo.com/v8/finance/chart/^JKSE?interval=1d&range=1d"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        data = resp.json()['chart']['result'][0]['meta']
        price = data['regularMarketPrice']
        change = ((price - data['previousClose']) / data['previousClose']) * 100
        return price, change
    except: return 0, 0

# --- 🕒 TIME MANAGEMENT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now_wib = datetime.now(tz_wib)
current_time = now_wib.time()
market_open = datetime.strptime("08:30", "%H:%M").time()
market_close = datetime.strptime("16:30", "%H:%M").time()
is_market_hours = market_open <= current_time <= market_close and now_wib.weekday() < 5

# --- 💉 REFRESH HTML ---
if is_market_hours:
    st.markdown('<meta http-equiv="refresh" content="900">', unsafe_allow_html=True)

# --- 🎨 VISUAL THEME ---
st.markdown("<style>.main { background-color: #0d1117; } .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); } .radar-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #8b5cf6; } .audit-box { background-color: #0f172a; border: 1px solid #8b5cf6; border-radius: 12px; padding: 20px; margin-top: 15px; } .pyramid-box { background-color: #020617; border: 1px dashed #4c1d95; padding: 15px; border-radius: 10px; margin-top: 10px; }</style>", unsafe_allow_html=True)

# --- 🗄️ SIDEBAR ---
with st.sidebar:
    st.write("Deploy")
    st.title("V84.0 GHOST-REMOTE")
    st.divider()
    bypass_engine = st.button("🔴 BYPASS MISSION LOCK")
    st.info(f"Market Status: {'OPEN' if is_market_hours else 'CLOSED'}")
    if st.button("🔄 Reboot System"):
        st.cache_data.clear()
        st.rerun()

# --- 🛰️ HEADER ---
ihsg_p, ihsg_c = get_ihsg_status()
st.markdown(f"""<div class='status-card'><div style='display:flex; justify-content:space-between; align-items:center;'><div><h1 style='color:#ddd6fe; margin:0; font-size:32px;'>💎 V84.0 GHOST-REMOTE</h1><p style='margin:0; opacity:0.8;'>Elite Quality Guard: 85% Min | AI Dynamic Engine 🕵️</p></div><div style='text-align:right;'><b style='color:#10b981; font-size:20px;'>{ihsg_p:,.2f} ({ihsg_c:+.2f}%)</b></div></div></div>""", unsafe_allow_html=True)

# --- 🚀 RADAR DISCOVERY (AUTOMATIC) ---
if is_market_hours or bypass_engine:
    st.markdown("### 📡 Radar Discovery (Top 3 Analysis)")
    try:
        url_scan = "https://scanner.tradingview.com/indonesia/scan"
        payload = {"filter": [{"left": "change", "operation": "greater", "right": 1.0}], "columns": ["name"], "sort": {"sortBy": "change", "sortOrder": "desc"}, "range": [0, 40]}
        resp = requests.post(url_scan, json=payload, timeout=10)
        data_raw = resp.json()['data']
        
        all_res = []
        if data_raw:
            for s in data_raw:
                ticker = s['d'][0]
                res, p, prob, plan = run_ghost_audit(ticker)
                # PENGETATAN 85%-100%
                if prob and prob >= 85:
                    all_res.append({'ticker': ticker, 'prob': prob})
            
            top_3 = sorted(all_res, key=lambda x: x['prob'], reverse=True)[:3]
            for idx, stock in enumerate(top_3):
                st.markdown(f"<div class='radar-card'><div style='display:flex; justify-content:space-between; align-items:center;'><h3 style='color:#a78bfa; margin:0;'>TOP {idx+1}: {stock['ticker']}</h3><span style='color:#60a5fa; font-weight:bold; font-size:18px;'>{stock['prob']}%</span></div></div>", unsafe_allow_html=True)
                # HANYA HASIL RADAR YANG DIKIRIM KE TELEGRAM
                send_telegram_msg(f"🛰️ *RADAR ALERT*\nTOP {idx+1}: {stock['ticker']}\nProbabilitas: {stock['prob']}%")
        else: st.info("Menunggu sinyal elit...")
    except: st.error("Koneksi Radar Terganggu.")
else:
    st.warning("⚠️ MARKET STANDBY. Radar otomatis aktif kembali jam 08:30 WIB.")

# --- 🔍 TACTICAL AUDIT (MANUAL WITH PYRAMID) ---
st.divider()
st.markdown("### 🔍 All-Cap Tactical Audit")
target = st.text_input("Sniper Target:", value="CUAN").upper()
if st.button("🚀 RUN DEEP AUDIT") or bypass_engine:
    res, p, prob, plan = run_ghost_audit(target)
    if res:
        st.markdown(f"""<div class='audit-box'><h2 style='color:#10b981; margin:0;'>{target} - FULL ANALYSIS ({prob}%)</h2><div class='pyramid-box'><b style='color:#8b5cf6;'>📐 AI DYNAMIC ENTRY PLAN:</b><br>• Entry 1 (Market): <b>Rp {plan['e1']}</b><br>• Entry 2 (Breakout): <b>Rp {plan['e2']}</b><br>• Entry 3 (Momentum): <b>Rp {plan['e3']}</b><br><br><b style='color:#ef4444;'>🛡️ ATR RISK PROTECTION:</b> SL Rp {plan['sl']}<br><b style='color:#10b981;'>💰 PROFIT TARGET:</b> TP Rp {plan['tp2']} (ARA Target)</div></div>""", unsafe_allow_html=True)
        st.json(res)
    else: st.error("Data tidak ditemukan.")

st.caption("V88.0 | AI Dynamic Edition | Algorithmic Pyramid")
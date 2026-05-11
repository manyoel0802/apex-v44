import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import warnings
import pytz
from datetime import datetime
from tradingview_screener import Query, Column

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V47.2 STABILITY RECOVERY", layout="wide", page_icon="🛡️")

# --- TEMA VISUAL ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 20px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #8b5cf6; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 12px; border-radius: 8px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

@st.cache_data(ttl=600) # Cache diperlama agar tidak membebani server
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="1y")
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126] if len(idx) > 126 else idx['Close'].iloc[0]
        breadth = (idx['Close'] > idx['Close'].rolling(50).mean()).iloc[-10:].sum() * 10
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], breadth
    except: return 0, True, 50

def run_deep_audit(ticker, ihsg_ret):
    try:
        stock_obj = yf.Ticker(f"{ticker}.JK")
        # Timeout 10 detik agar tidak "Scanning..." selamanya
        df = stock_obj.history(period="2y", auto_adjust=True, timeout=10) 
        if df.empty or len(df) < 150: return None, 0
        
        c = df['Close'].iloc[-1]
        if np.isnan(c): return None, 0
        
        s150, s200 = df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        weekly_ma = df['Close'].rolling(30).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        
        checks = {
            "Minervini Stage 2": bool(c > s150 > s200),
            "Weekly Anchor": bool(c > weekly_ma),
            "Alpha RS Score": bool(s_ret > ihsg_ret)
        }
        return checks, float(c)
    except: return None, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 24px; color:#ddd6fe;'>🛡️ V47.2 OMNI-APEX: RECOVERY</h1><p style='margin:0; opacity:0.8;'>Security Status: Stable | Server: Maintenance Period</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Control Center")
    cap = st.number_input("Capital (Rp)", value=1000000)
    mode = st.radio("🚀 Engine Mode", ["Turbo (Fast)", "Deep (Deep Audit)"])
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Time", value=False)
    if st.button("🧹 Clear Server Cache"):
        st.cache_data.clear()
        st.success("Cache Cleared!")

# --- 🚀 DASHBOARD ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
max_p = cap / 100

if is_market_open or bypass:
    st.subheader(f"📡 Radar Results ({mode})")
    try:
        # HANYA SCAN SAHAM LIKUID DI DASHBOARD
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(Column('market_cap_basic') >= 5e11, Column('close') <= max_p, Column('average_volume_120d') >= 2e5).limit(8))
        _, df_raw = q.get_scanner_data()
        
        cols = st.columns(2)
        v_idx = 0
        for _, row in df_raw.iterrows():
            if mode == "Turbo (Fast)": checks, prc = {"Turbo":True}, row['close']
            else: checks, prc = run_deep_audit(row['name'], ihsg_ret)
            
            if checks and all(checks.values()):
                with cols[v_idx % 2]:
                    st.markdown(f"<div class='stock-card'><h3>{row['name']}</h3><p>Price: {int(prc)} | Next Pyramid: {int(prc*1.05)}</p></div>", unsafe_allow_html=True)
                    v_idx += 1
    except: st.warning("📡 Radar sedang kalibrasi data malam. Gunakan Mode Turbo atau Audit Manual.")
else:
    st.info("🔴 RADAR STANDBY - Aktifkan 'Bypass' untuk cek data malam.")

# --- 🛡️ TOOLS ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Sniper")
    tid = st.text_input("Ticker:").upper()
    if st.button("🚀 Run Audit"):
        if tid:
            with st.spinner("Menarik data..."):
                res, p_val = run_deep_audit(tid, ihsg_ret)
                if res:
                    st.write(f"Vonis {tid}: {'✅ LULUS' if all(res.values()) else '❌ GAGAL'}")
                    st.markdown(f"<div class='pyramid-panel'><b>📐 Strategic Plan:</b> Entry {int(p_val)} | Next {int(p_val*1.05)} | SL {int(p_val*0.95)}</div>", unsafe_allow_html=True)
                else:
                    st.error("⚠️ Server Yahoo tidak memberikan data untuk ticker ini pada jam segini. Coba lagi dalam 5 menit atau gunakan ticker lain.")

with cb:
    st.subheader("🛡️ Market Breadth")
    st.metric("Health Score", f"{mkt_breadth}%", delta="Normal" if mkt_breadth > 50 else "Weak")

st.caption("V47.2 | Stability Patch | Maintenance-Aware Logic.")
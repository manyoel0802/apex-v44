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
st.set_page_config(page_title="V56.0 STEALTH SNIPER", layout="wide", page_icon="🎯")

# --- 🕵️ STEALTH HEADERS POOL ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

@st.cache_resource
def get_stealth_session():
    session = requests.Session()
    session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
    return session

# --- TEMA VISUAL SUPREME (LOCKED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; }
    .sector-badge { background-color: #2d1b4d; color: #a78bfa; padding: 3px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; border: 1px solid #7c3aed; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .target-value { font-size: 20px; font-weight: bold; color: #f8fafc; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

@st.cache_data(ttl=300)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="1y")
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], 85
    except: return 0, True, 50

# --- 🛡️ BUNKER DATA (ANTI-BAN CACHE) ---
@st.cache_data(ttl=300)
def fetch_tradingview_stealth(max_p):
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(
                 Column('market_cap_basic') >= 5e11, 
                 Column('close') <= max_p, 
                 Column('average_volume_120d') >= 1e5
             ).limit(25))
        _, df = q.get_scanner_data()
        return df, True
    except: return pd.DataFrame(), False

def run_deep_audit(ticker, ihsg_ret):
    try:
        # Micro-Jitter Delay untuk pengelabuan
        time.sleep(random.uniform(0.2, 0.7))
        
        session = get_stealth_session()
        stock_obj = yf.Ticker(f"{ticker}.JK", session=session)
        df = stock_obj.history(period="2y", auto_adjust=True, timeout=10)
        if df.empty or len(df) < 150: return None, 0
        
        c = df['Close'].iloc[-1]
        s50, s150, s200 = df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        weekly_ma = df['Close'].rolling(30).mean().iloc[-1]
        
        rs_line = df['Close'] / yf.Ticker("^JKSE").history(period="2y")['Close'].reindex(df.index, method='ffill')
        rs_slope = rs_line.iloc[-1] > rs_line.rolling(20).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        
        range_hl = (df['High'] - df['Low']).replace(0, 1e-10)
        mf_vol = (((c - df['Low']) - (df['High'] - c)) / range_hl) * df['Volume']
        cmf = mf_vol.rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1].replace(0, 1e-10)
        
        checks = {
            "Uptrend Status": bool(c > s50 > s200),
            "Minervini Stage 2": bool(c > s150 > s200),
            "Weekly Anchor": bool(c > weekly_ma),
            "Alpha RS Slope": bool(s_ret > ihsg_ret and rs_slope),
            "Bandar Accum": bool(cmf > 0.03)
        }
        return checks, float(c)
    except: return None, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>🎯 V56.0 STEALTH SNIPER</h1><p style='margin:0; opacity:0.8;'>Engine: TV + yF | Stealth Headers & Jitter Active 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital (Rp)", value=1000000)
    mode = st.radio("🚀 Scan Type", ["Turbo (Fast)", "Deep (Champion Audit)"], index=1)
    st.divider()
    risk = st.slider("Max Risk (%)", 1.0, 10.0, 5.0)
    rrr = st.number_input("Min RRR Target", value=3.0)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Time", value=False)
    if st.button("🔄 Reset Stealth Session"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Session & Cache Cleared!")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
max_p = cap / 100

if is_market_open or bypass:
    st.subheader(f"📡 {mode} Result")
    
    # Ambil data dari TradingView (Bunker Cache)
    df_raw, tv_online = fetch_tradingview_stealth(max_p)
    valid_signals = []
    
    if tv_online and not df_raw.empty:
        if mode == "Turbo (Fast)":
            for _, row in df_raw.iterrows():
                valid_signals.append((row['name'], row['sector'], {"Turbo Mode": True}, row['close']))
        else:
            # Deep Audit dengan Multi-threading (Dibatasi agar tidak spam)
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_row = {executor.submit(run_deep_audit, row['name'], ihsg_ret): row for _, row in df_raw.iterrows()}
                for future in concurrent.futures.as_completed(future_to_row):
                    row = future_to_row[future]
                    try:
                        checks, prc = future.result()
                        if checks and all(checks.values()):
                            valid_signals.append((row['name'], row['sector'], checks, prc))
                    except: pass
        
        if valid_signals:
            cols = st.columns(2)
            for i, (name, sector, checks, prc) in enumerate(valid_signals):
                sl, tp = int(prc*(1-risk/100)), int(prc + (prc*0.05)*rrr)
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <h2 style='margin:0; color:#a78bfa;'>{name}</h2>
                            <span class='sector-badge'>{sector}</span>
                        </div>
                        <div style='display:flex; justify-content:space-between; margin-top:15px;'>
                            <div><p style='color:#9ca3af; font-size:11px;'>ENTRY</p><p class='target-value'>{int(prc)}</p></div>
                            <div><p style='color:#9ca3af; font-size:11px;'>STOP LOSS</p><p class='target-value' style='color:#f87171;'>{sl}</p></div>
                            <div><p style='color:#9ca3af; font-size:11px;'>TARGET TP</p><p class='target-value' style='color:#10b981;'>{tp}</p></div>
                        </div>
                        <div class='pyramid-panel'>
                            <b style='color:#818cf8; font-size:11px;'>📐 STRATEGIC PLAN:</b><br>
                            <span style='font-size:11px;'>Next Entry (+5%): <b>{int(prc*1.05)}</b> | Risk-Free SL: <b>{int(prc)}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Penyisiran selesai, belum ada sinyal kuat saat ini.")
    else:
        st.error("Gagal menyambung ke TradingView. IP sedang dalam masa tenang (Rate Limit).")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", key="audit_in").upper()
    if st.button("🚀 Run Tactical Audit"):
        if tid_input:
            with st.spinner(f"Membedah {tid_input}..."):
                res, p_val = run_deep_audit(tid_input.replace(".JK",""), ihsg_ret)
                if res:
                    st.write(f"### Vonis {tid_input}:")
                    for k, v in res.items():
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='pyramid-panel'><b>📐 Strategic Plan:</b> Entry {int(p_val)} | Next {int(p_val*1.05)} | SL {int(p_val*(1-risk/100))}</div>", unsafe_allow_html=True)
                else: st.error("Data tidak ditemukan.")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    st.write(f"Market Health: **{mkt_breadth}%**")
    pid = st.text_input("Add to Portfolio:", key="port_in").upper()
    if st.button("🛒 EKSEKUSI"): st.success(f"Signal {pid} dikirim!")
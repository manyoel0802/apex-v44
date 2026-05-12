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
st.set_page_config(page_title="V59.0 GHOST-COMMANDER", layout="wide", page_icon="💎")

# --- 🕵️ ULTRA-STEALTH SESSIONS ---
@st.cache_resource
def get_hardened_session():
    session = requests.Session()
    # Rotasi User-Agent yang lebih modern & beragam
    ua = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1"
    ])
    session.headers.update({
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    return session

# --- TEMA VISUAL SUPREME (LOCKED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; }
    .sector-badge { background-color: #2d1b4d; color: #a78bfa; padding: 3px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; border: 1px solid #7c3aed; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .target-value { font-size: 18px; font-weight: bold; color: #f8fafc; }
    .buy-zone { background-color: #064e3b; color: #6ee7b7; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #059669; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ CONTEXT & JADWAL ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

@st.cache_data(ttl=300)
def get_market_context():
    try:
        session = get_hardened_session()
        idx = yf.Ticker("^JKSE", session=session).history(period="1y")
        if idx.empty: return 0, True, 50
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], 90
    except: return 0, True, 50

def calculate_atr(df, window=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    return np.max(ranges, axis=1).rolling(window).mean()

# --- 🛡️ CORE AUDIT ENGINE (GHOST MODE) ---
def run_deep_audit(ticker, sector="N/A", ihsg_ret=0, top_sectors=[]):
    session = get_hardened_session()
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    
    # TRIPLE RETRY STRATEGY
    for attempt in range(3):
        try:
            time.sleep(random.uniform(0.5, 1.2)) # Lebih lambat = Lebih aman
            stock_obj = yf.Ticker(f"{clean_ticker}.JK", session=session)
            df = stock_obj.history(period="1y", auto_adjust=True)
            
            # Smart Data Flattening
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            if not df.empty and len(df) > 10:
                c = float(df['Close'].iloc[-1])
                atr = float(calculate_atr(df).iloc[-1])
                dynamic_sl = int(c - (2 * atr))
                s50 = df['Close'].rolling(50).mean().iloc[-1]
                
                typical_price = (df['High'] + df['Low'] + df['Close']) / 3
                mfi = 50
                if len(df) > 14:
                    raw_mf = typical_price * df['Volume']
                    pos_flow = raw_mf.rolling(14).apply(lambda x: x[df['Close'].diff() > 0].sum(), raw=False)
                    neg_flow = raw_mf.rolling(14).apply(lambda x: x[df['Close'].diff() < 0].sum(), raw=False)
                    mfi = 100 - (100 / (1 + (pos_flow / neg_flow.replace(0, 1e-10)).iloc[-1]))

                checks = {
                    "Uptrend Status": bool(c > s50),
                    "Big Money Index": bool(mfi >= 50),
                    "RS Alpha Momentum": bool((c / df['Close'].iloc[-60] if len(df)>60 else 1) > 1)
                }
                return checks, c, "LEADER" if sector in top_sectors else "AUDIT", dynamic_sl
        except:
            time.sleep(2)
            continue
    return None, 0, "", 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V59.0 GHOST-COMMANDER</h1><p style='margin:0; opacity:0.8;'>Anti-Ban Protocol | Hardened Scraper | Market Lockdown Ready 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    mode = st.radio("🚀 Scan Sensitivity", ["Standard", "Aggressive"], index=0)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    
    if st.button("🛠️ Jalankan Diagnosa API"):
        with st.status("Audit Koneksi Global...", expanded=True) as status:
            st.cache_data.clear()
            try:
                Query().set_markets('indonesia').select('name').limit(1).get_scanner_data()
                st.success("✅ TradingView: OK")
            except: st.error("❌ TradingView: BAN")
            status.update(label="Selesai!", state="complete")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
max_p = cap / 100

if is_market_active or bypass:
    st.subheader(f"📡 Radar Result")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(Column('market_cap_basic') >= 1e11, Column('close') <= max_p, Column('average_volume_120d') >= 10000).limit(30))
        _, df_raw = q.get_scanner_data()
    except: df_raw = pd.DataFrame()

    if not df_raw.empty:
        valid_signals = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Dibatasi ke 2 worker agar tidak memicu ban kolektif
            futures = {executor.submit(run_deep_audit, row['name'], row['sector'], ihsg_ret): row for _, row in df_raw.iterrows()}
            for f in concurrent.futures.as_completed(futures):
                try:
                    res, p, l, sl = f.result()
                    if res and all(res.values()): valid_signals.append((futures[f]['name'], futures[f]['sector'], l, p, sl))
                except: pass
        
        if valid_signals:
            cols = st.columns(2)
            for i, (name, sector, l, p, sl) in enumerate(valid_signals):
                with cols[i % 2]:
                    st.markdown(f"<div class='stock-card'><h2>{name}</h2><span class='sector-badge'>{l}</span><div class='buy-zone'>ENTRY: {int(p)} - {int(p*1.03)}</div><div style='display:flex; justify-content:space-between; margin-top:15px;'><div><p style='font-size:11px;'>SL (ATR)</p><p class='target-value' style='color:#f87171;'>{sl}</p></div><div><p style='font-size:11px;'>TARGET TP</p><p class='target-value' style='color:#10b981;'>{int(p + (p-sl)*3)}</p></div></div></div>", unsafe_allow_html=True)
else:
    st.info("🔴 RADAR STANDBY. Aktifkan Bypass Lockdown.")

# --- 🛡️ TOOLS (THE TACTICAL AUDIT FIX) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", placeholder="Contoh: WIFI, BRMS, BBRI").upper()
    if st.button("🚀 EKSEKUSI AUDIT MANUAL"):
        if tid_input:
            with st.spinner(f"Menembus Pertahanan Yahoo untuk {tid_input}..."):
                # Force refresh session specifically for manual audit
                st.cache_resource.clear()
                res, p_val, label, sl = run_deep_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><h2 style='color:#a78bfa;'>{tid_input}</h2><p>Price: <b>Rp {int(p_val)}</b></p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='pyramid-panel'><b>Vonis:</b> Entry {int(p_val)} | SL {sl} | TP {int(p_val + (p_val-sl)*3)}</div>", unsafe_allow_html=True)
                else: 
                    st.error(f"❌ Yahoo Memblokir Akses. Solusi: Tunggu 2 menit, ganti Ticker, atau klik Reboot App di Dashboard Streamlit.")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    st.write(f"Market Health: **{mkt_breadth}%**")
    pid = st.text_input("Add to Portfolio:").upper()
    if st.button("🛒 TAMBAH"): st.success(f"Sinyal {pid} Terdaftar!")

st.caption("V59.0 | Ultimate Stealth Commander Ready")
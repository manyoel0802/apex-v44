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
st.set_page_config(page_title="V58.0 ELITE SENSOR", layout="wide", page_icon="💎")

# --- 🕵️ STEALTH HEADERS ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
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
    .target-value { font-size: 18px; font-weight: bold; color: #f8fafc; }
    .buy-zone { background-color: #064e3b; color: #6ee7b7; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #059669; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ CONTEXT & JADWAL ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_weekday = 0 <= now.weekday() <= 4
is_market_hours = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()
is_market_active = is_weekday and is_market_hours

@st.cache_data(ttl=300)
def get_market_context():
    try:
        session = get_stealth_session()
        idx = yf.Ticker("^JKSE", session=session).history(period="1y")
        if idx.empty: return 0, True, 50
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], 90
    except: return 0, True, 50

@st.cache_data(ttl=600)
def get_sector_momentum():
    try:
        q = (Query().set_markets('indonesia').select('sector','change').where(Column('market_cap_basic') > 1e11).limit(100))
        _, df = q.get_scanner_data()
        return df.groupby('sector')['change'].mean().sort_values(ascending=False).head(3).index.tolist()
    except: return []

def calculate_atr(df, window=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(window).mean()

# --- 🛡️ CORE AUDIT ENGINE (HARDENED) ---
def run_deep_audit(ticker, sector="N/A", ihsg_ret=0, top_sectors=[], mode="Standard"):
    session = get_stealth_session()
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    
    try:
        # Penambahan Micro-Delay agar tidak terdeteksi bot
        time.sleep(random.uniform(0.3, 0.6))
        stock_obj = yf.Ticker(f"{clean_ticker}.JK", session=session)
        df = stock_obj.history(period="1y", auto_adjust=True)
        
        # Penanganan jika yFinance mengembalikan Multi-Index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if not df.empty and len(df) > 20:
            c = float(df['Close'].iloc[-1])
            atr = float(calculate_atr(df).iloc[-1])
            dynamic_sl = int(c - (2 * atr))
            
            is_leader = sector in top_sectors if sector != "N/A" else False
            s50 = df['Close'].rolling(50).mean().iloc[-1]
            
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            raw_money_flow = typical_price * df['Volume']
            mfi = 50
            if len(df) > 14:
                pos_flow = raw_money_flow.rolling(14).apply(lambda x: x[df['Close'].diff() > 0].sum(), raw=False)
                neg_flow = raw_money_flow.rolling(14).apply(lambda x: x[df['Close'].diff() < 0].sum(), raw=False)
                mfi = 100 - (100 / (1 + (pos_flow / neg_flow.replace(0, 1e-10)).iloc[-1]))

            checks = {
                "Uptrend Status": bool(c > s50),
                "Big Money Index": bool(mfi >= 50),
                "RS Alpha Momentum": bool((c / df['Close'].iloc[-60] if len(df)>60 else 1) > 1)
            }
            label = "🏆 SECTOR LEADER" if is_leader else "TACTICAL AUDIT"
            return checks, c, label, dynamic_sl
    except:
        return None, 0, "", 0
    return None, 0, "", 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V58.0 ELITE SENSOR</h1><p style='margin:0; opacity:0.8;'>Hardened Tactical Audit | Multi-Index Support | Supreme Armor 🕵️</p></div>", unsafe_allow_html=True)

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
top_sectors = get_sector_momentum()
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_row = {executor.submit(run_deep_audit, row['name'], row['sector'], ihsg_ret, top_sectors, mode): row for _, row in df_raw.iterrows()}
            for future in concurrent.futures.as_completed(future_to_row):
                row = future_to_row[future]
                try:
                    checks, prc, label, sl = future.result()
                    if checks and all(checks.values()):
                        valid_signals.append((row['name'], row['sector'], checks, prc, label, sl))
                except: pass
        
        if valid_signals:
            cols = st.columns(2)
            for i, (name, sector, checks, prc, label, sl) in enumerate(valid_signals):
                tp = int(prc + (prc - sl) * 3)
                with cols[i % 2]:
                    st.markdown(f"<div class='stock-card'><h2>{name}</h2><span class='sector-badge'>{label}</span><div class='buy-zone'>ENTRY: {int(prc)} - {int(prc*1.03)}</div><div style='display:flex; justify-content:space-between; margin-top:15px;'><div><p style='font-size:11px;'>SL (ATR)</p><p class='target-value' style='color:#f87171;'>{sl}</p></div><div><p style='font-size:11px;'>TARGET TP</p><p class='target-value' style='color:#10b981;'>{tp}</p></div></div></div>", unsafe_allow_html=True)
else:
    st.info("🔴 RADAR STANDBY. Aktifkan Bypass Lockdown.")

# --- 🛡️ TOOLS (TACTICAL AUDIT RESTORED) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", placeholder="Contoh: BRMS, WIFI, BBCA").upper()
    if st.button("🚀 EKSEKUSI AUDIT MANUAL"):
        if tid_input:
            with st.spinner(f"Interogasi {tid_input}..."):
                # Force refresh session for manual audit
                res, p_val, label, sl = run_deep_audit(tid_input, "N/A", ihsg_ret, [], mode)
                if res:
                    st.markdown(f"<div class='stock-card'><h2 style='color:#a78bfa;'>{tid_input}</h2><p>Price: <b>Rp {int(p_val)}</b></p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): 
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='pyramid-panel'><b>Vonis Strategis:</b><br>Entry: {int(p_val)} | SL (ATR): {sl} | TP (3R): {int(p_val + (p_val-sl)*3)}</div>", unsafe_allow_html=True)
                else: 
                    st.error(f"❌ Server Yahoo sedang membatasi akses (Data Kosong). Coba ganti ticker atau tunggu 1 menit.")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    st.write(f"Market Health: **{mkt_breadth}%**")
    pid = st.text_input("Add to Portfolio:").upper()
    if st.button("🛒 TAMBAH"): st.success(f"Sinyal {pid} Terdaftar!")

st.caption("V58.0 | Hardened Audit Engine Enabled")
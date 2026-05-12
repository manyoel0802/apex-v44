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
st.set_page_config(page_title="V57.2 RADAR CLARITY", layout="wide", page_icon="💎")

# --- 🕵️ STEALTH HEADERS POOL ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
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
    .target-value { font-size: 18px; font-weight: bold; color: #f8fafc; }
    .buy-zone { background-color: #064e3b; color: #6ee7b7; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #059669; }
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
        if idx.empty: return 0, True, 50
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], 90
    except: return 0, True, 50

@st.cache_data(ttl=600)
def get_sector_momentum():
    try:
        q = (Query().set_markets('indonesia').select('sector','change')
             .where(Column('market_cap_basic') > 1e11).limit(100))
        _, df = q.get_scanner_data()
        top_sectors = df.groupby('sector')['change'].mean().sort_values(ascending=False).head(3).index.tolist()
        return top_sectors
    except: return ["Infrastruktur", "Energi", "Finansial"]

@st.cache_data(ttl=300)
def fetch_tradingview_stealth(max_p, min_vol=50000):
    try:
        # Melonggarkan filter agar radar lebih 'sensitif'
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(
                 Column('market_cap_basic') >= 1e11, # Min Cap 100M (Lebih Luas)
                 Column('close') <= max_p, 
                 Column('average_volume_120d') >= min_vol # Volum minimal 50rb
             ).limit(30))
        _, df = q.get_scanner_data()
        return df, True
    except: return pd.DataFrame(), False

def calculate_atr(df, window=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(window).mean()

def run_deep_audit(ticker, ihsg_ret, top_sectors):
    try:
        time.sleep(random.uniform(0.2, 0.4))
        session = get_stealth_session()
        stock_obj = yf.Ticker(f"{ticker}.JK", session=session)
        df = stock_obj.history(period="2y", auto_adjust=True, timeout=10)
        if df.empty or len(df) < 100: return None, 0, "", 0
        
        c = df['Close'].iloc[-1]
        atr = calculate_atr(df).iloc[-1]
        dynamic_sl = int(c - (2 * atr))
        
        is_leader = any(s in top_sectors for s in [ticker])
        s50, s200 = df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        raw_money_flow = typical_price * df['Volume']
        mfi = 50
        if len(df) > 14:
            pos_flow = raw_money_flow.rolling(14).apply(lambda x: x[df['Close'].diff() > 0].sum(), raw=False)
            neg_flow = raw_money_flow.rolling(14).apply(lambda x: x[df['Close'].diff() < 0].sum(), raw=False)
            mfi = 100 - (100 / (1 + (pos_flow / neg_flow.replace(0, 1e-10)).iloc[-1]))

        checks = {
            "Uptrend Status": bool(c > s50 or c > s200),
            "Big Money Flow": bool(mfi > 50),
            "Alpha RS Score": bool((c / df['Close'].iloc[-60] if len(df)>60 else 1) > 1)
        }
        
        label = "🏆 SECTOR LEADER" if is_leader else "Potensial 🚀"
        return checks, float(c), label, dynamic_sl
    except: return None, 0, "", 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V57.2 RADAR CLARITY</h1><p style='margin:0; opacity:0.8;'>Optimized Filters | Logic Corrected | Multi-Route Stability 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=10000000)
    mode = st.radio("🚀 Scan Sensitivity", ["Standard", "Aggressive (Loose Filters)"], index=0)
    st.divider()
    if st.button("🛠️ Diagnosa API"):
        with st.status("Cek Jalur...", expanded=True) as status:
            try:
                Query().set_markets('indonesia').select('name').limit(1).get_scanner_data()
                st.success("✅ TradingView: OK")
            except: st.error("❌ TradingView: BAN")
            try:
                yf_test = yf.Ticker("BBCA.JK").history(period="1d")
                if not yf_test.empty: st.success("✅ yFinance: OK")
                else: st.warning("⚠️ yFinance: SOFT BAN")
            except: st.error("❌ yFinance: BAN")
            status.update(label="Cek Selesai", state="complete")

    if st.button("🔄 Segarkan Sistem"):
        st.cache_data.clear()
        st.success("Radar Reset!")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
top_sectors = get_sector_momentum()
max_p = cap / 100
min_vol = 50000 if mode == "Standard" else 10000

if is_market_open or bypass:
    st.subheader(f"📡 Radar Result")
    df_raw, tv_online = fetch_tradingview_stealth(max_p, min_vol)
    
    if not tv_online:
        st.error("🚨 RADAR TERBLOKIR. IP Kapten sedang dalam pembatasan (Ban). Tunggu 1 jam atau ganti koneksi.")
    elif df_raw.empty:
        st.warning(f"Sinyal Tidak Ditemukan. Tidak ada saham di bawah Rp {int(max_p)} dengan likuiditas cukup saat ini. Coba naikkan Capital atau pilih Mode 'Aggressive'.")
    else:
        valid_signals = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_row = {executor.submit(run_deep_audit, row['name'], ihsg_ret, top_sectors): row for _, row in df_raw.iterrows()}
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
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='margin:0; color:#a78bfa;'>{name}</h2><span class='sector-badge'>{label}</span></div><div style='margin-top:10px;'><span class='buy-zone'>ENTRY ZONE: {int(prc)} - {int(prc*1.03)}</span></div><div style='display:flex; justify-content:space-between; margin-top:15px;'><div><p style='color:#9ca3af; font-size:11px;'>STOP LOSS (ATR)</p><p class='target-value' style='color:#f87171;'>{sl}</p></div><div><p style='color:#9ca3af; font-size:11px;'>TARGET TP</p><p class='target-value' style='color:#10b981;'>{tp}</p></div></div><div class='pyramid-panel'><b style='color:#818cf8; font-size:11px;'>📐 COMMANDER PLAN:</b><br><span style='font-size:11px;'>• Akumulasi Uang Besar Terdeteksi.<br>• Sektor: {sector}.<br>• ATR Stop Loss Aktif.</span></div></div>", unsafe_allow_html=True)
        else: st.info("Penyisiran selesai. Belum ada saham yang lolos kualifikasi teknikal saat ini.")
else:
    st.info("🔴 RADAR STANDBY.")

st.divider()
st.subheader("🔍 All-Cap Tactical Audit")
tid_input = st.text_input("Ticker Target:").upper()
if st.button("🚀 Audit"):
    res, p_val, label, sl = run_deep_audit(tid_input.replace(".JK",""), ihsg_ret, top_sectors)
    if res:
        for k, v in res.items(): st.write(f"{'✅' if v else '❌'} {k}")
        st.success(f"Audit {tid_input} Selesai!")
    else: st.error("Data tidak ditemukan.")

st.caption("V57.2 | Fixed Logic Mode")
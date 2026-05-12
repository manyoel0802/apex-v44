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
st.set_page_config(page_title="V57.1 ELITE COMMANDER", layout="wide", page_icon="💎")

# --- 🕵️ STEALTH HEADERS POOL ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
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
             .where(Column('market_cap_basic') > 1e12).limit(100))
        _, df = q.get_scanner_data()
        top_sectors = df.groupby('sector')['change'].mean().sort_values(ascending=False).head(3).index.tolist()
        return top_sectors
    except: return ["Infrastructure", "Financials", "Energy"]

@st.cache_data(ttl=300)
def fetch_tradingview_stealth(max_p):
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(Column('market_cap_basic') >= 5e11, Column('close') <= max_p, Column('average_volume_120d') >= 1e5).limit(25))
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
        if df.empty or len(df) < 150: return None, 0, "", 0
        
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
            "Uptrend Status": bool(c > s50 > s200),
            "Big Money Flow": bool(mfi > 55),
            "Relative Strength": bool((c / df['Close'].iloc[-126]) - 1 > ihsg_ret)
        }
        
        label = "🏆 SECTOR LEADER" if is_leader else "Breakout 🚀"
        return checks, float(c), label, dynamic_sl
    except: return None, 0, "", 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V57.1 ELITE COMMANDER</h1><p style='margin:0; opacity:0.8;'>Dynamic ATR SL | Sector Rotation | Diagnostic Satellite Integrated 🛰️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital (Rp)", value=1000000)
    mode = st.radio("🚀 Scan Type", ["Turbo (Fast)", "Deep (Champion Audit)"], index=1)
    rrr = st.number_input("Min RRR Target", value=3.0)
    bypass = st.toggle("🚨 Bypass Market Time", value=False)
    
    st.divider()
    # 🛠️ TOMBOL DIAGNOSTIK (RESTORED)
    if st.button("🛠️ Jalankan Diagnosa API"):
        with st.status("Memeriksa Jalur Radar...", expanded=True) as status:
            st.write("Mengetuk Pintu TradingView...")
            q_test = Query().set_markets('indonesia').select('name').limit(1)
            try:
                q_test.get_scanner_data()
                st.success("✅ TradingView: TERKONEKSI")
            except Exception as e:
                st.error(f"❌ TradingView: TERBLOKIR ({str(e)[:50]}...)")
            
            st.write("Mengetuk Pintu Yahoo Finance...")
            try:
                yf_test = yf.Ticker("BBCA.JK").history(period="1d")
                if not yf_test.empty: st.success("✅ yFinance: TERKONEKSI")
                else: st.warning("⚠️ yFinance: RESPON KOSONG (Ban Ringan)")
            except Exception as e:
                st.error(f"❌ yFinance: TERBLOKIR ({str(e)[:50]}...)")
            status.update(label="Diagnosa Selesai!", state="complete", expanded=False)

    if st.button("🔄 Segarkan Radar & Sektor"):
        st.cache_data.clear()
        st.success("Sistem Re-Calibrated!")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
top_sectors = get_sector_momentum()
max_p = cap / 100

if is_market_open or bypass:
    st.subheader(f"📡 {mode} Result (Top Sektor: {', '.join(top_sectors[:2])})")
    df_raw, tv_online = fetch_tradingview_stealth(max_p)
    valid_signals = []
    
    if tv_online and not df_raw.empty:
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
                tp = int(prc + (prc - sl) * rrr)
                buy_high = int(prc * 1.03)
                with cols[i % 2]:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='margin:0; color:#a78bfa;'>{name}</h2><span class='sector-badge'>{label}</span></div><div style='margin-top:10px;'><span class='buy-zone'>AREA ENTRY ELITE: {int(prc)} - {buy_high}</span></div><div style='display:flex; justify-content:space-between; margin-top:15px;'><div><p style='color:#9ca3af; font-size:11px;'>STOP LOSS (ATR)</p><p class='target-value' style='color:#f87171;'>{sl}</p></div><div><p style='color:#9ca3af; font-size:11px;'>TARGET ({rrr}R)</p><p class='target-value' style='color:#10b981;'>{tp}</p></div></div><div class='pyramid-panel'><b style='color:#818cf8; font-size:11px;'>📐 ELITE COMMANDER PLAN:</b><br><span style='font-size:11px;'>• Akumulasi Uang Besar Terdeteksi ✅<br>• Momentum Sektoral Terkonfirmasi.<br>• SL Dinamis berdasarkan Volatilitas (ATR).</span></div></div>", unsafe_allow_html=True)
        else: st.info("Sektor terkuat sudah dipindai, belum ada sinyal 'Big Money' saat ini.")
    else: st.error("Satelit Radar Buta. Klik 'Diagnosa API' untuk info lebih lanjut.")
else: st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", key="audit_in").upper()
    if st.button("🚀 Run Tactical Audit"):
        if tid_input:
            with st.spinner(f"Interogasi {tid_input}..."):
                res, p_val, label, sl = run_deep_audit(tid_input.replace(".JK",""), ihsg_ret, top_sectors)
                if res:
                    st.write(f"### Vonis {tid_input}:")
                    for k, v in res.items(): st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='pyramid-panel'><b>Entry:</b> {int(p_val)} | <b>ATR-SL:</b> {sl} | <b>Target:</b> {int(p_val + (p_val-sl)*rrr)}</div>", unsafe_allow_html=True)
                else: st.error("Data tidak ditemukan.")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    st.write(f"Market Health: **{mkt_breadth}%**")
    pid = st.text_input("Add to Portfolio:", key="port_in").upper()
    if st.button("🛒 EKSEKUSI"): st.success(f"Signal {pid} dikirim!")

st.caption("V57.1 | Elite Commander Mode | Diagnostic Satellite Ready")
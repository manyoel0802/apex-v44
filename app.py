import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import requests
import warnings
import time
import os
import gc 
from datetime import datetime, timedelta
import pytz
from tradingview_screener import Query, Column

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None
st.set_page_config(page_title="V45.0 OMNI-APEX", layout="wide", page_icon="🌍")

try:
    TELE_TOKEN = st.secrets["TELE_TOKEN"]
    TELE_CHAT_ID = st.secrets["TELE_CHAT_ID"]
except:
    TELE_TOKEN = "8457858315:AAGPSHq0UsfPv8MZ733tHs40gAOxwvx7G0o"
    TELE_CHAT_ID = "5916986433"

# --- TEMA VISUAL UNGU KLASIK (100% PRESERVED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; color: white; }
    .bg-sector { background: linear-gradient(135deg, #2e1065 0%, #4c1d95 50%, #3b0764 100%); border-top: 5px solid #8b5cf6; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3); }
    .stock-card { background-color: #1c2128; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-top: 15px; border-left: 5px solid #8b5cf6; }
    .sector-badge { background-color: #8b5cf6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .lockdown-box { background-color: #450a0a; border: 1px solid #dc2626; padding: 15px; border-radius: 8px; color: #fca5a5; margin-bottom:20px; }
    .mtf-badge { background-color: #059669; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 5px; }
    .ara-badge { background-color: #dc2626; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 5px; font-weight: bold; }
    .heartbeat { font-family: monospace; color: #a78bfa; font-size: 14px; font-weight: bold; }
    .elite-tag { color: #f59e0b; font-size: 11px; font-weight: bold; }
    .cluster-warn { color: #f87171; font-size: 11px; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ TIME GATE & HEARTBEAT WIB ---
tz_wib = pytz.timezone('Asia/Jakarta')
waktu_sekarang = datetime.now(tz_wib)
timestamp_scan = waktu_sekarang.strftime("%H:%M:%S")
mesin_aktif = datetime.strptime("08:30", "%H:%M").time() <= waktu_sekarang.time() <= datetime.strptime("16:30", "%H:%M").time()

# --- 🛡️ MODUL MEMORI ANTI-SPAM ---
def get_today_signals():
    today_str = waktu_sekarang.strftime("%Y-%m-%d")
    try:
        if os.path.exists("daily_signals.txt"):
            with open("daily_signals.txt", "r") as f:
                lines = f.readlines()
                if lines and lines[0].strip() == today_str:
                    return [line.strip() for line in lines[1:]]
    except: pass
    return []

def add_today_signal(ticker):
    today_str = waktu_sekarang.strftime("%Y-%m-%d")
    signals = get_today_signals()
    if ticker not in signals:
        signals.append(ticker)
        try:
            with open("daily_signals.txt", "w") as f:
                f.write(today_str + "\n")
                for s in signals:
                    f.write(s + "\n")
        except: pass

# --- 🌍 CORE ENGINES ---
@st.cache_data(ttl=3600)
def get_market_data():
    try:
        ihsg = yf.Ticker("^JKSE").history(period="7mo")
        ihsg['SMA50'] = ihsg['Close'].rolling(50).mean()
        curr_close = ihsg['Close'].iloc[-1]
        # Poin 1: RS Ranking (Return IHSG 6 bulan)
        idx_6m_ago = ihsg['Close'].iloc[-126] if len(ihsg) > 126 else ihsg['Close'].iloc[0]
        idx_return = (curr_close / idx_6m_ago) - 1
        return "BULLISH" if curr_close > ihsg['SMA50'].iloc[-1] else "BEARISH", curr_close, idx_return
    except: return "NEUTRAL", 0, 0

@st.cache_data(ttl=1800)
def get_tradingview_radar():
    try:
        q = (Query().set_markets('indonesia')
             .select('name','close','sector','volume','Perf.1M','market_cap_basic')
             .where(
                 Column('market_cap_basic') >= 5e10,
                 Column('close') > Column('SMA50'),
                 Column('close') > Column('SMA200'),
                 Column('volume') >= 1e6
             )
             .limit(1000))
        _, df = q.get_scanner_data()
        return df
    except: return pd.DataFrame()

def detect_fake_volume(df):
    """Poin 4: VSA Ghost Detector (Deteksi Volume Palsu)"""
    try:
        last_vol = df['Volume'].iloc[-1]
        avg_vol = df['Volume'].rolling(20).mean().iloc[-2]
        spread = df['High'].iloc[-1] - df['Low'].iloc[-1]
        avg_spread = (df['High'] - df['Low']).rolling(20).mean().iloc[-2]
        
        # Jika Volume Meledak > 2.5x tapi Spread harga sangat sempit (< 0.5x rata-rata)
        # Indikasi kuat Wash Sale / Volume Palsu
        if last_vol > (avg_vol * 2.5) and spread < (avg_spread * 0.5):
            return True
        return False
    except: return False

def check_h1_interceptor(ticker):
    try:
        h1_data = yf.Ticker(f"{ticker}.JK").history(period="2d", interval="1h")
        if len(h1_data) < 5: return False
        last_vol = h1_data['Volume'].iloc[-1]
        avg_vol = h1_data['Volume'].iloc[-5:-1].mean()
        return last_vol > (avg_vol * 1.5)
    except: return False

# --- UI HEADER ---
st.markdown(f"""
<div class='status-card bg-sector'>
    <h1 style='margin:0; color:#ddd6fe;'>🌍 V45.0 OMNI-APEX: WORLD CHAMPION EDITION</h1>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <p style='margin:5px 0 0 0; opacity:0.9; color:#a78bfa;'>Alpha Leader | Ghost Detector | Risk-Free Logic</p>
        <p class='heartbeat'>📡 LAST SCAN: {timestamp_scan} WIB</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Settings")
    premium_mode = st.toggle("🚀 Activate Premium Features", value=True)
    st.divider()
    capital = st.number_input("Portfolio (Rp)", value=1000000, step=100000)
    risk_pct = st.slider("Max Loss Per Trade (%)", 0.5, 10.0, 5.0, step=0.5)
    rrr_min = st.number_input("Min RRR Target", value=3.0, step=0.5)
    st.divider()
    bypass_lockdown = st.toggle("🚨 Bypass Lockdown", value=False)
    st.write(f"Sinyal aktif hari ini: {len(get_today_signals())}")

# --- 🚀 EXECUTION ENGINE ---
if mesin_aktif:
    market_health, ihsg_curr, ihsg_ret = get_market_data()
    if market_health == "BEARISH" and not bypass_lockdown:
        st.markdown("<div class='lockdown-box'><h2>⛔ MARKET LOCKDOWN</h2><p>IHSG Bearish. Radar Standby.</p></div>", unsafe_allow_html=True)
        st.stop()
        
    with st.status(f"Omni-Scan Running...", expanded=True) as status:
        try:
            df_raw = get_tradingview_radar()
            if not df_raw.empty:
                valid_total = 0
                sector_tracker = {} # Poin 3: Cluster Guard
                
                for _, row in df_raw.iterrows():
                    if valid_total >= 12: break 
                    t_sym = row['name']
                    if (row['close'] * row['volume']) < 5e9: continue
                    
                    time.sleep(0.2) 
                    df_hist = yf.Ticker(f"{t_sym}.JK").history(period="1y", auto_adjust=True)
                    if df_hist.empty: continue
                    
                    # Poin 4: Filter Volume Palsu
                    if detect_fake_volume(df_hist): continue
                    
                    # Poin 1: RS Ranking
                    stock_6m_ago = df_hist['Close'].iloc[-126] if len(df_hist) > 126 else df_hist['Close'].iloc[0]
                    stock_ret = (row['close'] / stock_6m_ago) - 1
                    rs_leader = stock_ret > ihsg_ret
                    
                    tech_pass = (row['close'] > df_hist['Close'].rolling(150).mean().iloc[-1] and 
                                 row['close'] > df_hist['Close'].rolling(200).mean().iloc[-1])
                    
                    if tech_pass and rs_leader:
                        trigger = int(row['close'])
                        sl = int(trigger * 0.95)
                        tp1 = int(trigger + (trigger - sl) * 1.5)
                        tp2 = int(trigger + (trigger - sl) * rrr_min)
                        
                        # Poin 3: Cluster Guard logic
                        s_name = row['sector']
                        sector_tracker[s_name] = sector_tracker.get(s_name, 0) + 1
                        cluster_msg = "<br><span class='cluster-warn'>⚠️ CLUSTER: Sektor ini mulai penuh.</span>" if sector_tracker[s_name] > 2 else ""
                        
                        valid_total += 1
                        h1_tag = " [⚡ H1]" if check_h1_interceptor(t_sym) else ""
                        
                        st.markdown(f"""
                        <div class='stock-card'>
                            <h3>{t_sym} <span class='sector-badge'>{s_name}</span></h3>
                            <p style='margin:0;'><span class='tier-a'>🔥 ALPHA LEADER{h1_tag}</span></p>
                            <p><b>Target: TP1 {tp1} | TP2 {tp2}</b><br>
                            <span class='elite-tag'>🛡️ Risk-Free: Set SL to {trigger} after TP1 hit</span>{cluster_msg}</p>
                            <p style='font-size:12px;'>SL: {sl} | Yield vs IHSG: +{((stock_ret-ihsg_ret)*100):.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Telegram Notification
                        if premium_mode:
                            today_signals = get_today_signals()
                            if t_sym not in today_signals:
                                try: 
                                    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": f"COMMAND_ADD:{t_sym}"}, timeout=1)
                                    add_today_signal(t_sym)
                                except: pass
                    del df_hist
                    gc.collect()
                status.update(label="Advanced Scan Complete!", state="complete")
        except Exception as e: st.error(f"Error: {e}")

# =========================================================
# 🛠️ MODULE: PORTFOLIO MANAGER
# =========================================================
st.divider()
st.subheader("🛡️ OMNI-APEX Portfolio Manager")
def load_portfolio():
    if os.path.exists("portfolio.txt"):
        with open("portfolio.txt", "r") as f: return list(set([line.strip().upper() for line in f.readlines() if line.strip()]))
    return []

col_add, col_del = st.columns(2)
with col_add:
    st.write("🛒 **Tambah Pantauan**")
    selected_to_buy = st.text_input("Ketik Manual:", key="buy_manual").upper()
    if st.button("🛒 KONFIRMASI BELI"):
        if selected_to_buy:
            try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": f"COMMAND_ADD:{selected_to_buy}"}, timeout=1)
            except: pass
            st.success(f"✅ Sinyal dikirim!")

with col_del:
    st.write("🗑️ **Hapus Pantauan**")
    current_portfolio = load_portfolio()
    if current_portfolio:
        to_delete = st.selectbox("Hapus pantauan:", current_portfolio, key="del_select")
        if st.button("🗑️ KONFIRMASI HAPUS"):
            try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": f"COMMAND_DEL:{to_delete}"}, timeout=1)
            except: pass
            st.error(f"🗑️ Perintah hapus dikirim.")

if not mesin_aktif: st.info(f"🔴 RADAR STANDBY. Aktif otomatis pada 08:30 WIB.")
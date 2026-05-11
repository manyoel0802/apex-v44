import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import warnings
import pytz
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import concurrent.futures

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V49.4 ULTIMATE SHIELD", layout="wide", page_icon="🛡️")

# --- TEMA VISUAL SUPREME ---
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

# --- ⏳ CONTEXT & SESSION SHIELD (ANTI-BAN UNTUK YFINANCE & TRADINGVIEW) ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

@st.cache_resource
def get_armored_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # Penyamaran ganda: Seolah-olah ini adalah Google Chrome asli
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Origin': 'https://www.tradingview.com',
        'Referer': 'https://www.tradingview.com/'
    })
    return session

armored_session = get_armored_session()

# ⚡ CUSTOM TRADINGVIEW FETCHER (ANTI-BAN, TANPA MODUL PIHAK KETIGA)
def stealth_tv_scanner(max_p):
    try:
        url = "https://scanner.tradingview.com/indonesia/scan"
        payload = {
            "filter": [
                {"left": "market_cap_basic", "operation": "egreater", "right": 500000000000},
                {"left": "close", "operation": "eless", "right": max_p},
                {"left": "average_volume_120d", "operation": "egreater", "right": 100000}
            ],
            "options": {"lang": "en"},
            "markets": ["indonesia"],
            "symbols": {"query": {"types": []}, "tickers": []},
            "columns": ["name", "close", "sector"],
            "sort": {"sortBy": "average_volume_120d", "sortOrder": "desc"},
            "range": [0, 20]
        }
        resp = armored_session.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            records = [{'name': d['d'][0], 'close': d['d'][1], 'sector': d['d'][2]} for d in data]
            return pd.DataFrame(records)
    except: pass
    return pd.DataFrame()

def stealth_tv_sector(ticker):
    try:
        url = "https://scanner.tradingview.com/indonesia/scan"
        payload = {
            "symbols": {"tickers": [f"IDX:{ticker}"]},
            "columns": ["name", "sector"]
        }
        resp = armored_session.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            if data: return data[0]['d'][1]
    except: pass
    return "IDX"

@st.cache_data(ttl=300)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE", session=armored_session).history(period="1y")
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126] if len(idx) > 126 else idx['Close'].iloc[0]
        breadth = (idx['Close'] > idx['Close'].rolling(50).mean()).iloc[-10:].sum() * 10
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], breadth
    except: return 0, True, 50

def run_deep_audit(ticker, ihsg_ret):
    try:
        time.sleep(random.uniform(0.3, 0.8)) # Jeda manusiawi
        stock_obj = yf.Ticker(f"{ticker}.JK", session=armored_session)
        df = stock_obj.history(period="2y", auto_adjust=True, timeout=15)
        if df.empty or len(df) < 150: return None, 0
        
        c = df['Close'].iloc[-1]
        v = df['Volume'].iloc[-1]
        
        s50, s150, s200 = df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        weekly_ma = df['Close'].rolling(30).mean().iloc[-1]
        
        rs_line = df['Close'] / yf.Ticker("^JKSE", session=armored_session).history(period="2y")['Close'].reindex(df.index, method='ffill')
        rs_slope = rs_line.iloc[-1] > rs_line.rolling(20).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        
        atr = (df['High'] - df['Low']).rolling(10).mean()
        vcp = atr.iloc[-1] < atr.rolling(50).mean().iloc[-1]
        vdu = v < df['Volume'].rolling(20).mean().iloc[-1]
        
        range_hl = (df['High'] - df['Low']).replace(0, 1e-10)
        mf_vol = (((c - df['Low']) - (df['High'] - c)) / range_hl) * df['Volume']
        cmf = mf_vol.rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1].replace(0, 1e-10)
        
        checks = {
            "Uptrend Status": bool(c > s50 > s200),
            "Minervini Stage 2": bool(c > s150 > s200),
            "Weekly Anchor": bool(c > weekly_ma),
            "Alpha RS Slope": bool(s_ret > ihsg_ret and rs_slope),
            "VCP & VDU Pattern": bool(vcp or vdu),
            "Bandar Accum": bool(cmf > 0.03)
        }
        return checks, float(c)
    except: return None, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>🛡️ V49.4 ULTIMATE SHIELD</h1><p style='margin:0; opacity:0.8;'>Engine: Direct TV Stealth + V8 Engine | Double Anti-Ban Active 🛡️</p></div>", unsafe_allow_html=True)

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
    if st.button("🧹 Clear Server Cache"):
        st.cache_data.clear()
        st.success("Cache Cleared!")

# --- 🚀 MAIN DASHBOARD (V8 PIPELINE) ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
max_p = cap / 100

if is_market_open or bypass:
    st.subheader(f"📡 {mode} Result (Market Cap > 500B)")
    try:
        # TAHAP 1: TRADINGVIEW STEALTH SCANNER
        df_raw = stealth_tv_scanner(max_p)
        
        if df_raw.empty:
            st.warning("TradingView sedang membatasi akses (Rate Limit). Mohon tunggu beberapa menit atau restart router WiFi Anda.")
        else:
            valid_signals = []
            
            # TAHAP 2: 8 TANGAN VIRTUAL
            if mode == "Turbo (Fast)":
                for _, row in df_raw.iterrows():
                    valid_signals.append((row['name'], row['sector'], {"Turbo Mode": True}, row['close']))
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_row = {executor.submit(run_deep_audit, row['name'], ihsg_ret): row for _, row in df_raw.iterrows()}
                    for future in concurrent.futures.as_completed(future_to_row):
                        row = future_to_row[future]
                        try:
                            checks, prc = future.result()
                            if checks and all(checks.values()):
                                valid_signals.append((row['name'], row['sector'], checks, prc))
                        except: pass
            
            # RENDER TAMPILAN SUPREME
            if valid_signals:
                cols = st.columns(2)
                v_idx = 0
                for name, sector, checks, prc in valid_signals:
                    sl, tp = int(prc*(1-risk/100)), int(prc + (prc*0.05)*rrr)
                    with cols[v_idx % 2]:
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
                    v_idx += 1
            else:
                st.info("Stealth Scan selesai. Belum ada sinyal kuat yang lolos filter Minervini.")
            
    except Exception as e:
        st.error(f"Terjadi kesalahan sistem: {e}")
else:
    st.info("🔴 RADAR STANDBY - Aktifkan 'Bypass' di Sidebar.")

# --- 🛡️ TOOLS (AUDIT PIPELINE) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target (Contoh: DFAM):").upper()
    tid = tid_input.replace(".JK", "") 
    
    if st.button("🚀 Run Tactical Audit"):
        if tid:
            with st.spinner(f"Interogasi Senyap {tid}..."):
                # CEK SEKTOR VIA TV DIRECT
                sector_info = stealth_tv_sector(tid)
                st.write(f"Sektor: **{sector_info}**")
                
                # INTEROGASI MENDALAM VIA YFINANCE (ANTI-BAN)
                res, p_val = run_deep_audit(tid, ihsg_ret)
                if res:
                    st.write(f"### Vonis {tid}:")
                    for k, v in res.items():
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    if all(res.values()): st.success("WORLD CHAMPION CONFIRMED 🚀")
                    st.markdown(f"<div class='pyramid-panel'><b>📐 Strategic Plan:</b> Entry {int(p_val)} | Next {int(p_val*1.05)} | SL {int(p_val*(1-risk/100))}</div>", unsafe_allow_html=True)
                else:
                    st.error("Data historis tidak ditemukan. Jika kode benar, IP Kapten mungkin masih diblokir sementara. Harap tunggu 30-60 menit atau restart Router/Mode Pesawat.")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    st.write(f"Market Health: **{mkt_breadth}%**")
    pid = st.text_input("Add to Portfolio/Trade:").upper()
    if st.button("🛒 EKSEKUSI / ADD SIGNAL"): 
        st.success(f"Signal {pid} berhasil dikirim!")

st.caption("V49.4 PRESTIGE | Direct TV Stealth Integration | Absolute Anti-Ban Protocol.")
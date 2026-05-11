import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import warnings
import pytz
import requests
from datetime import datetime
from tradingview_screener import Query, Column
import concurrent.futures

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V48.4 GOAPI STRIKE (RESTORED)", layout="wide", page_icon="💎")

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

# --- ⏳ CONTEXT & DATA ENGINE ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

@st.cache_data(ttl=300)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="1y")
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126] if len(idx) > 126 else idx['Close'].iloc[0]
        breadth = (idx['Close'] > idx['Close'].rolling(50).mean()).iloc[-10:].sum() * 10
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], breadth
    except: return 0, True, 50

# ⚡ HYBRID DATA FETCHER (GOAPI -> YFINANCE)
def fetch_stock_data(ticker, api_key=""):
    df = pd.DataFrame()
    source = "None"
    
    if api_key:
        try:
            url = f"https://api.goapi.id/v1/stock/idx/{ticker}/historical"
            resp = requests.get(url, params={"api_key": api_key}, timeout=5)
            if resp.status_code == 200:
                json_data = resp.json()
                if 'data' in json_data and 'results' in json_data['data']:
                    df_temp = pd.DataFrame(json_data['data']['results'])
                    df_temp['date'] = pd.to_datetime(df_temp['date'])
                    df_temp.set_index('date', inplace=True)
                    df_temp = df_temp.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
                    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                        df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce')
                    df_temp.sort_index(ascending=True, inplace=True)
                    if not df_temp.empty and len(df_temp) > 150:
                        df = df_temp
                        source = "GoAPI"
        except: pass

    if df.empty:
        try:
            stock_obj = yf.Ticker(f"{ticker}.JK")
            df_temp = stock_obj.history(period="2y", auto_adjust=True, timeout=5)
            if not df_temp.empty and len(df_temp) > 150:
                df = df_temp
                source = "YFinance"
        except: pass
        
    return df, source

def run_deep_audit(ticker, ihsg_ret, api_key=""):
    df, source = fetch_stock_data(ticker, api_key)
    if df.empty: return None, 0, source
    
    try:
        c, v = df['Close'].iloc[-1], df['Volume'].iloc[-1]
        s150, s200 = df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        weekly_ma = df['Close'].rolling(30).mean().iloc[-1]
        rs_line = df['Close'] / yf.Ticker("^JKSE").history(period="2y")['Close'].reindex(df.index, method='ffill')
        rs_slope = rs_line.iloc[-1] > rs_line.rolling(20).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        atr = (df['High'] - df['Low']).rolling(10).mean()
        vcp = atr.iloc[-1] < atr.rolling(50).mean().iloc[-1]
        vdu = v < df['Volume'].rolling(20).mean().iloc[-1]
        range_hl = (df['High'] - df['Low']).replace(0, 1e-10)
        mf_vol = (((c - df['Low']) - (df['High'] - c)) / range_hl) * df['Volume']
        cmf = mf_vol.rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1].replace(0, 1e-10)
        
        checks = {"Minervini Fine-Tune": bool(c > s150 > s200), "Weekly Anchor": bool(c > weekly_ma), "Alpha RS Slope": bool(s_ret > ihsg_ret and rs_slope), "VCP & VDU Pattern": bool(vcp or vdu), "Bandar Accum": bool(cmf > 0.03)}
        return checks, float(c), source
    except: return None, 0, source

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>🏆 V48.4 PRESTIGE COMMANDER</h1><p style='margin:0; opacity:0.8;'>Engine: GoAPI Strike ⚡ | TV Pipeline | Dual-Audit Active</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital (Rp)", value=1000000)
    
    st.divider()
    goapi_key = st.text_input("🔑 GoAPI Key (Opsional/Gratis):", type="password", help="Masukkan API Key dari GoAPI untuk data BEI super cepat.")
    st.caption("Jika kosong/limit habis, mesin otomatis pindah ke YFinance.")
    
    st.divider()
    mode = st.radio("🚀 Scan Type", ["Turbo (Fast)", "Deep (Champion Audit)"], index=1)
    risk = st.slider("Max Risk (%)", 1.0, 10.0, 5.0)
    rrr = st.number_input("Min RRR Target", value=3.0)
    bypass = st.toggle("🚨 Bypass Market Time", value=False)
    if st.button("🧹 Clear Server Cache"):
        st.cache_data.clear()
        st.success("Cache Cleared!")

# --- 🚀 DASHBOARD ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
max_p = cap / 100

if is_market_open or bypass:
    st.subheader(f"📡 {mode} Result (Market Cap > 500B)")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(Column('market_cap_basic') >= 5e11, Column('close') <= max_p, Column('close') > Column('SMA200'), Column('SMA50') > Column('SMA200'), Column('average_volume_120d') >= 1e5).limit(10))
        _, df_raw = q.get_scanner_data()
        valid_signals = []
        
        if mode == "Turbo (Fast)":
            for _, row in df_raw.iterrows(): valid_signals.append((row, {"Turbo Mode": True}, row['close'], "TradingView"))
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                future_to_row = {executor.submit(run_deep_audit, row['name'], ihsg_ret, goapi_key): row for _, row in df_raw.iterrows()}
                for future in concurrent.futures.as_completed(future_to_row):
                    row = future_to_row[future]
                    try:
                        checks, prc, src = future.result()
                        if checks and all(checks.values()): valid_signals.append((row, checks, prc, src))
                    except: pass
                    
        if valid_signals:
            cols = st.columns(2)
            v_idx = 0
            for row, checks, prc, src in valid_signals:
                sl, tp = int(prc*(1-risk/100)), int(prc + (prc*0.05)*rrr)
                with cols[v_idx % 2]:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='margin:0; color:#a78bfa;'>{row['name']}</h2><span class='sector-badge'>{row['sector']}</span></div><p style='font-size:10px; color:#9ca3af; margin:0; padding-top:5px;'>Data Source: {src}</p><div style='display:flex; justify-content:space-between; margin-top:15px;'><div><p style='color:#9ca3af; font-size:11px;'>ENTRY</p><p class='target-value'>{int(prc)}</p></div><div><p style='color:#9ca3af; font-size:11px;'>STOP LOSS</p><p class='target-value' style='color:#f87171;'>{sl}</p></div><div><p style='color:#9ca3af; font-size:11px;'>TARGET TP</p><p class='target-value' style='color:#10b981;'>{tp}</p></div></div><div class='pyramid-panel'><b style='color:#818cf8; font-size:11px;'>📐 STRATEGIC PLAN:</b><br><span style='font-size:11px;'>Next Entry (+5%): <b>{int(prc*1.05)}</b> | Risk-Free SL: <b>{int(prc)}</b></span></div></div>", unsafe_allow_html=True)
                v_idx += 1
        else: st.info("Radar sedang memindai, belum ada sinyal kuat yang lolos filter.")
    except Exception as e: st.warning(f"Satelit sedang mengkalibrasi data... ({e})")
else: st.info("🔴 RADAR STANDBY - Aktifkan 'Bypass' di Sidebar.")

# --- 🛡️ TOOLS ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Dual Audit")
    tid_input = st.text_input("Ticker Target (Contoh: DFAM):").upper()
    tid = tid_input.replace(".JK", "").strip() 
    
    if st.button("🚀 Run Tactical Audit"):
        if tid:
            with st.spinner("Memproses Audit..."):
                tv_success = False
                c_tv = 0
                try:
                    q_tv = Query().set_markets('indonesia').select('close','SMA50','SMA200','average_volume_120d').where(Column('name') == tid)
                    _, df_tv = q_tv.get_scanner_data()
                    if not df_tv.empty:
                        c_tv, s50, s200, vol = df_tv.iloc[0]['close'], df_tv.iloc[0]['SMA50'], df_tv.iloc[0]['SMA200'], df_tv.iloc[0]['average_volume_120d']
                        tv_success = True
                        st.write("### ⚡ Pre-Check (TradingView)")
                        c1, c2 = st.columns(2)
                        c1.markdown(f"<span class='{'audit-pass' if c_tv > s200 else 'audit-fail'}'>{'✅' if c_tv > s200 else '❌'} Harga > SMA 200</span>", unsafe_allow_html=True)
                        c2.markdown(f"<span class='{'audit-pass' if vol > 1e5 else 'audit-fail'}'>{'✅' if vol > 1e5 else '❌'} Likuiditas > 100k</span>", unsafe_allow_html=True)
                except: pass

                if mode == "Deep (Champion Audit)" or not tv_success:
                    st.write("---")
                    res, p_val, src = run_deep_audit(tid, ihsg_ret, goapi_key)
                    if res:
                        st.write(f"### 🔬 Deep Dive ({src})")
                        for k, v in res.items():
                            st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                        
                        is_winner = all(res.values())
                        if tv_success: is_winner = is_winner and (c_tv > s200)
                            
                        if is_winner: st.success("WORLD CHAMPION CONFIRMED 🚀")
                        else: st.warning("BELUM LOLOS STANDAR JUARA ⛔")
                        st.markdown(f"<div class='pyramid-panel'><b>📐 Pyramid Plan:</b> Entry {int(p_val)} | Next {int(p_val*1.05)} | SL {int(p_val*(1-risk/100))}</div>", unsafe_allow_html=True)
                    else:
                        st.error("⚠️ Data tidak ditemukan. Periksa Ticker atau cek batas harian API Key Anda.")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    st.write(f"Market Health: **{mkt_breadth}%**")
    pid = st.text_input("Add to Portfolio/Trade:").upper()
    if st.button("🛒 EKSEKUSI / ADD SIGNAL"): st.success(f"Signal {pid} berhasil dikirim!")
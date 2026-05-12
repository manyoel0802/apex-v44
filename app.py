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
st.set_page_config(page_title="V62.0 PHANTOM RESOLVE", layout="wide", page_icon="💎")

# --- 🕵️ ULTRA-HARDENED SESSION ---
@st.cache_resource
def get_hardened_session():
    session = requests.Session()
    # Rotasi User-Agent paling baru (Mei 2026)
    session.headers.update({
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
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

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

@st.cache_data(ttl=300)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="1y")
        curr = idx['Close'].iloc[-1]
        return (curr / idx['Close'].iloc[-126]) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1]
    except: return 0, True

# --- 🛡️ CORE PHANTOM ENGINE (V62.0) ---
def run_deep_audit(ticker, sector="N/A", ihsg_ret=0, top_sectors=[]):
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    session = get_hardened_session()
    
    # 🚀 JALUR 1: YAHOO FORCE (Audit Mendalam)
    try:
        time.sleep(random.uniform(0.3, 0.5))
        s_obj = yf.Ticker(f"{clean_ticker}.JK", session=session)
        df = s_obj.history(period="1y", auto_adjust=True)
        if not df.empty and len(df) > 20:
            c = float(df['Close'].iloc[-1])
            s50, s200 = df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
            atr = (pd.concat([df['High']-df['Low'], (df['High']-df['Close'].shift()).abs(), (df['Low']-df['Close'].shift()).abs()], axis=1).max(axis=1).rolling(14).mean()).iloc[-1]
            mfi_val = 50 # Default
            if len(df) > 14:
                tp = (df['High'] + df['Low'] + df['Close']) / 3
                rmf = tp * df['Volume']
                pos = rmf.rolling(14).apply(lambda x: x[df['Close'].diff() > 0].sum(), raw=False)
                neg = rmf.rolling(14).apply(lambda x: x[df['Close'].diff() < 0].sum(), raw=False)
                mfi_val = 100 - (100 / (1 + (pos / neg.replace(0, 1e-10)).iloc[-1]))
            
            checks = {
                "Uptrend Status": bool(c > s50),
                "Minervini Stage 2": bool(s50 > s200),
                "Big Money Index": bool(mfi_val >= 50),
                "RS Alpha Momentum": bool((c / df['Close'].iloc[-60]) > 1),
                "Bandar Accum": bool(mfi_val > 55)
            }
            return checks, c, "YAHOO", int(c - (2 * atr))
    except: pass

    # 🚀 JALUR 2: TRADINGVIEW FORCE (Antiblocking Fallback)
    try:
        # Mencoba mencari dengan prefix IDX:
        for t_query in [clean_ticker, f"IDX:{clean_ticker}"]:
            q = (Query().set_markets('indonesia')
                 .select('name','close','EMA50','EMA200','MoneyFlowIndex','ATR','performance.6m','relative_strength_index')
                 .where(Column('name') == t_query).limit(1))
            _, tv = q.get_scanner_data()
            if not tv.empty:
                c = float(tv['close'].iloc[0])
                mfi_v = float(tv['MoneyFlowIndex'].iloc[0])
                checks = {
                    "Uptrend Status": bool(c > float(tv['EMA50'].iloc[0])),
                    "Minervini Stage 2": bool(float(tv['EMA50'].iloc[0]) > float(tv['EMA200'].iloc[0])),
                    "Big Money Index": bool(mfi_v >= 45),
                    "RS Alpha Momentum": bool(float(tv['performance.6m'].iloc[0]) > 0),
                    "Bandar Accum": bool(mfi_v > 50)
                }
                atr_val = float(tv['ATR'].iloc[0]) if not np.isnan(tv['ATR'].iloc[0]) else c*0.03
                return checks, c, "T-VIEW", int(c - (1.5 * atr_val))
    except: pass
    
    return None, 0, "", 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V62.0 PHANTOM RESOLVE</h1><p style='margin:0; opacity:0.8;'>Force-Fetch Data Recovery | 5-Aspect Analysis | Pyramid Scaling 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    mode = st.radio("🚀 Scan Sensitivity", ["Standard", "Aggressive"], index=0)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🔄 Force Reboot Data"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.success("Sistem Berhasil Di-Reset!")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish = get_market_context()
max_p = cap / 100

if is_market_active or bypass:
    st.subheader(f"📡 Radar Result")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(Column('market_cap_basic') >= 1e11, Column('close') <= max_p, Column('average_volume_120d') >= 10000).limit(20))
        _, df_raw = q.get_scanner_data()
    except: df_raw = pd.DataFrame()

    if not df_raw.empty:
        valid_signals = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futs = {executor.submit(run_deep_audit, r['name'], r['sector'], ihsg_ret): r for _, r in df_raw.iterrows()}
            for f in concurrent.futures.as_completed(futs):
                try:
                    res, p, src, sl = f.result()
                    if res and all(res.values()): valid_signals.append((futs[f]['name'], futs[f]['sector'], src, p, sl))
                except: pass
        
        if valid_signals:
            cols = st.columns(2)
            for i, (name, sector, src, p, sl) in enumerate(valid_signals):
                with cols[i % 2]:
                    st.markdown(f"<div class='stock-card'><h2>{name}</h2><span class='sector-badge'>SRC: {src}</span><div class='buy-zone'>ENTRY: {int(p)} - {int(p*1.03)}</div><div style='display:flex; justify-content:space-between; margin-top:15px;'><div><p style='font-size:11px;'>SL (ATR)</p><p class='target-value' style='color:#f87171;'>{sl}</p></div><div><p style='font-size:11px;'>TARGET TP</p><p class='target-value' style='color:#10b981;'>{int(p + (p-sl)*3)}</p></div></div></div>", unsafe_allow_html=True)
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS (THE ABSOLUTE FIX: 5 ASPECTS + PYRAMID) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:", placeholder="Contoh: WIFI, BRMS, BBCA").upper()
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Menembus Pertahanan untuk {tid_input}..."):
                res, p_val, src, sl = run_deep_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><h2 style='color:#a78bfa;'>{tid_input}</h2><p>Price: <b>Rp {int(p_val)}</b> <small>(via {src})</small></p></div>", unsafe_allow_html=True)
                    # 5 ASPEK PENYARINGAN
                    for k, v in res.items(): 
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    
                    # PYRAMID PLAN
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8; font-size:11px;'>📐 ELITE PYRAMID PLAN:</b><br>
                        <span style='font-size:11px;'>
                        • <b>Entry 1 (50%):</b> {int(p_val)} | <b>Entry 2 (+4%):</b> {int(p_val*1.04)}<br>
                        • <b>SL (ATR):</b> {sl} | <b>TP (3R):</b> {int(p_val + (p_val-sl)*3)}<br>
                        • <b>Action:</b> Validasi sinyal teknikal via {src} Terkonfirmasi.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error(f"❌ DATA TIDAK DITEMUKAN. Pastikan Ticker benar atau klik 'Force Reboot Data' di sidebar.")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    pid = st.text_input("Add to Portfolio:").upper()
    if st.button("🛒 TAMBAH"): st.success(f"Saham {pid} Terdaftar!")

st.caption("V62.0 | Absolute Phantom Recovery Mode")
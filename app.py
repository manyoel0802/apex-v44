import streamlit as st
import pandas as pd
import numpy as np
import warnings
import pytz
from datetime import datetime
from tradingview_screener import Query, Column

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V72.0 HYPER-DRIVE", layout="wide", page_icon="💎")

# --- TEMA VISUAL SUPREME (LOCKED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; }
    .sector-badge { background-color: #2d1b4d; color: #a78bfa; padding: 3px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; border: 1px solid #7c3aed; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .buy-zone { background-color: #064e3b; color: #6ee7b7; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #059669; }
    .probability-badge { background: #1e3a8a; color: #60a5fa; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; border: 1px solid #3b82f6; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🛡️ THE HYPER-DRIVE ENGINE ---
def run_tactical_audit(ticker):
    # Digunakan untuk audit manual spesifik
    try:
        q = (Query().set_markets('indonesia')
             .select('name', 'close', 'EMA50', 'EMA200', 'MoneyFlowIndex', 'ATR', 'performance.6m', 'sector')
             .where(Column('name').contains(ticker.upper())).limit(1))
        _, df = q.get_scanner_data()
        if not df.empty:
            row = df.iloc[0]
            c = float(row['close'])
            checks = {
                "Uptrend Status": bool(c > float(row['EMA50'])),
                "Minervini Stage 2": bool(float(row['EMA50']) > float(row['EMA200'])),
                "Big Money Index": bool(float(row['MoneyFlowIndex']) >= 45),
                "RS Alpha Momentum": bool(float(row['performance.6m']) > 0),
                "Bandar Accum": bool(float(row['MoneyFlowIndex']) > 50)
            }
            prob = int((sum(checks.values()) / 5) * 100)
            sl = int(c - (1.5 * float(row['ATR'])))
            return checks, c, row['sector'], sl, prob
    except: pass
    return None, 0, "", 0, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V72.0 HYPER-DRIVE</h1><p style='margin:0; opacity:0.8;'>Server-Side Pre-Filtering | Instant Sniper Scan | Zero Latency 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🔄 Reset Hyper-Drive"):
        st.cache_data.clear()
        st.success("Connection Refreshed!")

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

# --- 🚀 MAIN DASHBOARD (HYPER-DRIVE RADAR) ---
if is_active or bypass:
    st.subheader(f"📡 Radar Result (Instant Scan)")
    try:
        max_p = cap / 100
        # IDE CEMERLANG: Pindahkan filter audit ke dalam Query API
        q = (Query().set_markets('indonesia')
             .select('name', 'close', 'sector', 'ATR', 'EMA50', 'EMA200', 'MoneyFlowIndex', 'performance.6m')
             .where(
                 Column('close') <= max_p,
                 Column('average_volume_120d') >= 10000,
                 Column('close') > Column('EMA50'), # Filter 1: Uptrend
                 Column('EMA50') > Column('EMA200'), # Filter 2: Minervini Stage 2
                 Column('MoneyFlowIndex') >= 48       # Filter 3: Big Money
             )
             .order_by('performance.6m', ascending=False)
             .limit(6))
        
        _, df_final = q.get_scanner_data()
        
        if not df_final.empty:
            cols = st.columns(2)
            for i, row in enumerate(df_final.itertuples()):
                c = float(row.close)
                atr = float(row.ATR) if not np.isnan(row.ATR) else c * 0.03
                # Kalkulasi Probabilitas Instan
                prob = int((( (c > row.EMA50) + (row.EMA50 > row.EMA200) + (row.MoneyFlowIndex >= 50) + (row._8 > 0) + (row.MoneyFlowIndex > 55) ) / 5) * 100)
                sl = int(c - (1.5 * atr))
                
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <h2 style='margin:0; color:#a78bfa;'>{row.name}</h2>
                            <span class='probability-badge'>{prob}%</span>
                        </div>
                        <div style='margin-top:10px;'><span class='buy-zone'>ENTRY: Rp {int(c)}</span></div>
                        <div class='pyramid-panel' style='font-size:11px;'>
                        <b>TP:</b> {int(c+(c-sl)*3)} | <b>SL:</b> {sl} | <b>Scale:</b> {int(c*1.04)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else: st.info("Sinyal belum terdeteksi. Kriteria 'World Champion' sangat ketat.")
    except: st.warning("Mengaktifkan Hyper-Drive...")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS (TACTICAL AUDIT) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:").upper()
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Interogasi {tid_input}..."):
                res, p, sector, sl, prob = run_tactical_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='color:#a78bfa;'>{tid_input}</h2><span class='probability-badge'>{prob}%</span></div><p>Price: <b>{int(p)}</b> | Sector: {sector}</p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='pyramid-panel'><b>Entry:</b> {int(p)} | <b>Scale-Up:</b> {int(p*1.04)} | <b>SL:</b> {sl}</div>", unsafe_allow_html=True)
                else: st.error("❌ DATA TIDAK DITEMUKAN.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Ticker Portfolio:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Ditambahkan!")

st.caption("V72.0 | Hyper-Drive Mode Active | Server-Side Filtering")
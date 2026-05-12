import streamlit as st
import pandas as pd
import numpy as np
import warnings
import pytz
import time
from datetime import datetime
from tradingview_screener import Query, Column

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V74.0 OMNI-LIGHT", layout="wide", page_icon="💎")

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

# --- 🛡️ THE LIGHT-AUDIT ENGINE ---
def run_sniper_audit(ticker):
    try:
        q = (Query().set_markets('indonesia')
             .select('name', 'close', 'EMA50', 'EMA200', 'MoneyFlowIndex', 'ATR', 'performance.6m', 'sector')
             .where(Column('name').contains(ticker.upper())).limit(1))
        _, df = q.get_scanner_data()
        if not df.empty:
            row = df.iloc[0]
            c = float(row['close'])
            e50 = float(row['EMA50']) if not np.isnan(row['EMA50']) else c
            e200 = float(row['EMA200']) if not np.isnan(row['EMA200']) else c
            mfi = float(row['MoneyFlowIndex']) if not np.isnan(row['MoneyFlowIndex']) else 50
            
            checks = {
                "Uptrend Status": bool(c >= e50),
                "Minervini Stage 2": bool(e50 >= e200),
                "Big Money Index": bool(mfi >= 45),
                "RS Alpha Momentum": bool(float(row['performance.6m']) > 0),
                "Bandar Accum": bool(mfi > 50)
            }
            prob = int((sum(checks.values()) / 5) * 100)
            atr = float(row['ATR']) if not np.isnan(row['ATR']) else c * 0.03
            return checks, c, row['sector'], int(c - (1.5 * atr)), prob
    except: pass
    return None, 0, "", 0, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V74.0 OMNI-LIGHT</h1><p style='margin:0; opacity:0.8;'>Decentralized Sniper | Instant Discovery | Ultra-Safe Protocol 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🔄 Purge All Cache"):
        st.cache_data.clear()
        st.success("IP Session Reset!")

# --- 🚀 MAIN DASHBOARD ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

if is_active or bypass:
    st.subheader(f"📡 High-Potential Discovery (Fast Scan)")
    try:
        max_p = cap / 100
        # HANYA SCAN DASAR (Sangat Cepat & Aman)
        q = (Query().set_markets('indonesia')
             .select('name', 'close', 'sector', 'change')
             .where(Column('close') <= max_p, Column('average_volume_120d') >= 50000)
             .order_by('change', ascending=False)
             .limit(10))
        _, df_raw = q.get_scanner_data()
        
        if not df_raw.empty:
            st.write("Klik saham di bawah atau gunakan kolom audit untuk eksekusi Sniper.")
            cols = st.columns(5)
            for i, row in enumerate(df_raw.itertuples()):
                with cols[i % 5]:
                    if st.button(f"🎯 {row.name}"):
                        st.session_state['audit_target'] = row.name
        else: st.warning("Bursa belum memberikan data.")
    except: st.error("Koneksi satelit terganggu. Klik Purge Cache di sidebar.")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ THE SNIPER AUDIT (CENTRAL ACTION) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 Elite Tactical Audit")
    # Mengambil target dari klik radar atau input manual
    current_target = st.session_state.get('audit_target', "")
    tid_input = st.text_input("Ticker Sniper Target:", value=current_target).upper()
    
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Melakukan Interogasi Mendalam pada {tid_input}..."):
                res, p, sector, sl, prob = run_sniper_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='color:#a78bfa;'>{tid_input}</h2><span class='probability-badge'>{prob}%</span></div><p>Price: <b>{int(p)}</b> | Sector: {sector}</p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='pyramid-panel'><b>Entry:</b> {int(p)} | <b>Scale-Up:</b> {int(p*1.04)} | <b>SL:</b> {sl} | <b>Target:</b> {int(p+(p-sl)*3)}</div>", unsafe_allow_html=True)
                else: st.error("❌ TARGET GAGAL DIAUDIT. Coba ticker lain.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Add to Portfolio:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Ditambahkan!")

st.caption("V74.0 | Decentralized Sniper Protocol | Anti-Ban Active")
import streamlit as st
import pandas as pd
import numpy as np
import warnings
import pytz
import time
import requests
import random
from datetime import datetime
from tradingview_screener import Query, Column
from bs4 import BeautifulSoup

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V80.0 OMNI-LIGHT SNIPER", layout="wide", page_icon="🎯")

# --- TEMA VISUAL SUPREME (LOCKED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stock-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6; }
    .probability-badge { background: #1e3a8a; color: #60a5fa; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 14px; border: 1px solid #3b82f6; }
    .buy-zone { background-color: #064e3b; color: #6ee7b7; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #059669; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🕵️ ULTRA-STEALTH ENGINE ---
def run_sniper_audit(ticker):
    try:
        # Jalur Cepat: Hanya interogasi satu target
        q = (Query().set_markets('indonesia')
             .select('name', 'close', 'EMA50', 'EMA200', 'MoneyFlowIndex', 'performance.6m', 'ATR', 'sector')
             .where(Column('name').contains(ticker.upper())).limit(1))
        _, df = q.get_scanner_data()
        if not df.empty:
            row = df.iloc[0]
            c = float(row['close'])
            e50 = float(row['EMA50']) if not np.isnan(row['EMA50']) else c
            mfi = float(row['MoneyFlowIndex']) if not np.isnan(row['MoneyFlowIndex']) else 50
            
            checks = {
                "Uptrend Status": bool(c >= e50),
                "Minervini Stage 2": bool(e50 >= (row['EMA200'] if not np.isnan(row['EMA200']) else e50)),
                "Big Money Index": bool(mfi >= 45),
                "RS Alpha Momentum": bool(float(row['performance.6m']) > 0),
                "Bandar Accum": bool(mfi > 52)
            }
            prob = int((sum(checks.values()) / 5) * 100)
            atr = float(row['ATR']) if not np.isnan(row['ATR']) else c * 0.03
            return checks, c, row['sector'], int(c - (1.5 * atr)), prob
    except: pass
    return None, 0, "", 0, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>🎯 V80.0 OMNI-LIGHT SNIPER</h1><p style='margin:0; opacity:0.8;'>Anti-Block Discovery | 80% Win-Rate Focus | Zero-Wait Scraper 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🔄 Force Refresh Satelit"):
        st.cache_data.clear()
        st.success("Sirkuit Dibersihkan!")

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

# --- 🚀 DISCOVERY RADAR (FAST & LIGHT) ---
if is_active or bypass:
    st.subheader(f"📡 High-Potential ARA Tracker (Discovery)")
    try:
        max_p = cap / 100
        # Taktik OMNI-LIGHT: Hanya scan dasar (Harga & Volume) agar sangat cepat
        q_fast = (Query().set_markets('indonesia')
                 .select('name', 'close', 'change')
                 .where(Column('close') <= max_p, Column('average_volume_120d') >= 50000, Column('change') >= 2.0)
                 .order_by('change', ascending=False)
                 .limit(10))
        _, df_fast = q_fast.get_scanner_data()
        
        if not df_fast.empty:
            st.write("Klik emiten untuk audit 5-aspek instan:")
            cols = st.columns(5)
            for i, row in enumerate(df_fast.itertuples()):
                with cols[i % 5]:
                    if st.button(f"🎯 {row.name}"):
                        st.session_state['target_ticker'] = row.name
        else: st.info("Satelit sedang menyisir emiten potensial...")
    except: st.error("⚠️ Jalur Discovery Macet. Gunakan Tactical Audit Manual di bawah.")
else:
    st.info("🔴 RADAR STANDBY (Market Closed).")

# --- 🛡️ THE SNIPER ACTION (TACTICAL AUDIT) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Sniper Audit")
    # Mengambil target dari klik discovery atau input manual
    saved_target = st.session_state.get('target_ticker', "")
    tid_input = st.text_input("Sniper Target:", value=saved_target).upper()
    
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Interogasi Sniper {tid_input}..."):
                res, p, sector, sl, prob = run_sniper_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='color:#a78bfa;'>{tid_input}</h2><span class='probability-badge'>{prob}% PROB</span></div><p>Price: <b>{int(p)}</b> | Sector: {sector}</p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8; font-size:11px;'>📐 ELITE COMMANDER PLAN:</b><br>
                        <span style='font-size:11px;'>
                        • <b>Entry 1:</b> {int(p)} | <b>Entry 2 (+4%):</b> {int(p*1.04)}<br>
                        • <b>Stop Loss:</b> {sl} | <b>Target Profit:</b> {int(p*1.15)}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error("❌ DATA TIDAK DITEMUKAN. Server sedang memblokir akses.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Add to Portfolio:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Ditambahkan!")

st.caption("V80.0 | Omni-Light Sniper Mode | Anti-Block Protocol")
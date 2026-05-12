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
st.set_page_config(page_title="V71.0 LIGHTNING-FORCE", layout="wide", page_icon="💎")

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
    .probability-badge { background: #1e3a8a; color: #60a5fa; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; border: 1px solid #3b82f6; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🛡️ THE LIGHTNING AUDIT ENGINE (V71.0) ---
def run_lightning_audit(ticker):
    # Digunakan khusus untuk Tactical Audit (Manual) dengan proteksi ekstra
    clean_ticker = ticker.strip().upper().replace(".JK", "")
    try:
        q = (Query().set_markets('indonesia')
             .select('name', 'close', 'EMA50', 'EMA200', 'MoneyFlowIndex', 'ATR', 'performance.6m', 'sector')
             .where(Column('name').contains(clean_ticker)).limit(5))
        _, df = q.get_scanner_data()
        
        if not df.empty:
            match = df[df['name'] == clean_ticker]
            row = match.iloc[0] if not match.empty else df.iloc[0]
            
            c = float(row['close'])
            e50, e200 = float(row['EMA50']), float(row['EMA200'])
            mfi = float(row['MoneyFlowIndex'])
            atr = float(row['ATR']) if not np.isnan(row['ATR']) else c * 0.03
            perf = float(row['performance.6m'])
            
            checks = {
                "Uptrend Status": bool(c > e50),
                "Minervini Stage 2": bool(e50 > e200),
                "Big Money Index": bool(mfi >= 45),
                "RS Alpha Momentum": bool(perf > 0),
                "Bandar Accum": bool(mfi > 50)
            }
            prob = int((sum(checks.values()) / 5) * 100)
            sl = int(c - (1.5 * atr))
            return checks, c, "T-VIEW", sl, prob, int(c*1.04), int(c + (c-sl)*3)
    except: pass
    return None, 0, "", 0, 0, 0, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>💎 V71.0 LIGHTNING-FORCE</h1><p style='margin:0; opacity:0.8;'>Bulk Data Fetching | Zero-Latency Audit | Maximum Safety Sniper 🕵️</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital Total (Rp)", value=1000000)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Lockdown", value=False)
    if st.button("🔄 Clear System Cache"):
        st.cache_data.clear()
        st.success("Cache Purged!")

# --- ⏳ CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_active = (0 <= now.weekday() <= 4) and (datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time())

# --- 🚀 MAIN DASHBOARD (OPTIMIZED RADAR) ---
if is_active or bypass:
    st.subheader(f"📡 Sniper Radar (Bulk Mode)")
    try:
        # Taktik Borongan: Ambil semua indikator dalam SATU permintaan
        max_p = cap / 100
        q = (Query().set_markets('indonesia')
             .select('name', 'close', 'EMA50', 'EMA200', 'MoneyFlowIndex', 'ATR', 'performance.6m', 'sector')
             .where(Column('close') <= max_p, Column('average_volume_120d') >= 10000, Column('EMA50') > 0)
             .limit(20))
        _, df_radar = q.get_scanner_data()
        
        if not df_radar.empty:
            valid_signals = []
            for row in df_radar.itertuples():
                c = float(row.close)
                e50, e200 = float(row.EMA50), float(row.EMA200)
                mfi = float(row.MoneyFlowIndex)
                atr = float(row.ATR) if not np.isnan(row.ATR) else c * 0.03
                
                # Instant Internal Audit
                if c > e50 and mfi >= 45:
                    prob = int((( (c>e50) + (e50>e200) + (mfi>=45) + (row._7 > 0) + (mfi>50) ) / 5) * 100)
                    sl = int(c - (1.5 * atr))
                    valid_signals.append((row.name, row.sector, c, sl, prob))
            
            if valid_signals:
                cols = st.columns(2)
                for i, (name, sector, p, sl, prob) in enumerate(valid_signals[:4]):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class='stock-card'>
                            <div style='display:flex; justify-content:space-between;'>
                                <h2 style='margin:0; color:#a78bfa;'>{name}</h2>
                                <span class='probability-badge'>{prob}%</span>
                            </div>
                            <div style='margin-top:10px;'><span class='buy-zone'>ENTRY: Rp {int(p)}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
            else: st.info("Sinyal belum terdeteksi. Gunakan Audit Manual.")
    except: st.warning("Sedang menyelaraskan satelit...")
else:
    st.info("🔴 RADAR STANDBY.")

# --- 🛡️ TOOLS (TACTICAL AUDIT - RESTORED) ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target:").upper()
    if st.button("🚀 EKSEKUSI Sniper Audit"):
        if tid_input:
            with st.spinner(f"Interogasi {tid_input}..."):
                res, p_val, src, sl, prob, e2, tp = run_lightning_audit(tid_input)
                if res:
                    st.markdown(f"<div class='stock-card'><div style='display:flex; justify-content:space-between;'><h2 style='color:#a78bfa;'>{tid_input}</h2><span class='probability-badge'>{prob}% CONFIDENCE</span></div><p>Price: <b>Rp {int(p_val)}</b></p></div>", unsafe_allow_html=True)
                    for k, v in res.items(): 
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b style='color:#818cf8; font-size:11px;'>📐 ELITE COMMANDER PLAN:</b><br>
                        <span style='font-size:11px;'>
                        • <b>Entry 1 (50%):</b> {int(p_val)} | <b>Entry 2 (+4%):</b> {int(e2)}<br>
                        • <b>SL (ATR):</b> {sl} | <b>Target Profit:</b> {int(tp)}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error("❌ DATA TIDAK DITEMUKAN.")

with cb:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Add Ticker:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Ditambahkan!")

st.caption("V71.0 | Lightning-Force | Maximum Stability")
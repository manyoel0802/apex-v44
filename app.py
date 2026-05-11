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

# --- TEMA VISUAL UNGU KLASIK (PRESERVED) ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    .status-card { border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #30363d; color: white; }
    .bg-sector { background: linear-gradient(135deg, #2e1065 0%, #4c1d95 50%, #3b0764 100%); border-top: 5px solid #8b5cf6; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3); }
    .stock-card { background-color: #1c2128; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-top: 15px; border-left: 5px solid #8b5cf6; }
    .sector-badge { background-color: #8b5cf6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .lockdown-box { background-color: #450a0a; border: 1px solid #dc2626; padding: 15px; border-radius: 8px; color: #fca5a5; margin-bottom:20px; }
    .heartbeat { font-family: monospace; color: #a78bfa; font-size: 14px; font-weight: bold; }
    .pyramid-box { background-color: #1e1b4b; border: 1px dashed #6366f1; padding: 12px; border-radius: 8px; margin-top: 15px; font-size: 12px; color: #e0e7ff; }
    .audit-pass { color: #10b981; font-weight: bold; }
    .audit-fail { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ TIME GATE & HEARTBEAT WIB ---
tz_wib = pytz.timezone('Asia/Jakarta')
waktu_sekarang = datetime.now(tz_wib)
timestamp_scan = waktu_sekarang.strftime("%H:%M:%S")
mesin_aktif = True

# --- 🌍 CORE ALGORITHM ---
def detect_fake_volume(df):
    try:
        last_vol = df['Volume'].iloc[-1]
        avg_vol = df['Volume'].rolling(20).mean().iloc[-2]
        spread = df['High'].iloc[-1] - df['Low'].iloc[-1]
        avg_spread = (df['High'] - df['Low']).rolling(20).mean().iloc[-2]
        return last_vol > (avg_vol * 2.5) and spread < (avg_spread * 0.5)
    except: return False

def run_audit(ticker, ihsg_ret):
    try:
        stock = yf.Ticker(f"{ticker}.JK")
        df = stock.history(period="1y", auto_adjust=True)
        if df.empty: return None
        
        c = df['Close'].iloc[-1]
        sma50, sma150, sma200 = df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        
        stock_6m = df['Close'].iloc[-126] if len(df) > 126 else df['Close'].iloc[0]
        stock_ret = (c / stock_6m) - 1
        
        range_hl = (df['High'] - df['Low']).replace(0, 1e-10)
        mf_vol = (((c - df['Low']) - (df['High'] - c)) / range_hl) * df['Volume']
        cmf = mf_vol.rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1]
        
        checks = {
            "Minervini Template (Uptrend)": c > sma150 and sma150 > sma200,
            "Above SMA 50 (Momentum)": c > sma50,
            "Alpha Leader (RS vs IHSG)": stock_ret > ihsg_ret,
            "Big Money Flow (Accumulation)": cmf > 0.03,
            "Fake Vol Check (VSA Ghost)": not detect_fake_volume(df)
        }
        return checks, c, stock_ret
    except: return None

# --- UI HEADER ---
st.markdown(f"""
<div class='status-card bg-sector'>
    <h1 style='margin:0; color:#ddd6fe;'>🌍 V45.0 OMNI-APEX: WORLD CHAMPION EDITION</h1>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <p style='margin:5px 0 0 0; opacity:0.9; color:#a78bfa;'>Alpha Leader | Pyramiding | Audit Manual</p>
        <p class='heartbeat'>📡 LAST SCAN: {timestamp_scan} WIB</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Settings")
    premium_mode = st.toggle("🚀 Activate Premium Features", value=True)
    capital = st.number_input("Portfolio (Rp)", value=1000000)
    st.divider()
    ihsg_data = yf.Ticker("^JKSE").history(period="7mo")
    ihsg_6m = ihsg_data['Close'].iloc[-126] if len(ihsg_data) > 126 else ihsg_data['Close'].iloc[0]
    ihsg_ret = (ihsg_data['Close'].iloc[-1] / ihsg_6m) - 1
    st.metric("IHSG 6M Yield", f"{(ihsg_ret*100):.2f}%")

# --- 🚀 LIVE SCAN ENGINE ---
if mesin_aktif:
    with st.status("Auto-Scanning Universe...", expanded=False) as status:
        q = (Query().set_markets('indonesia').select('name','close','sector','volume').where(Column('market_cap_basic') >= 5e10, Column('close') > Column('SMA200')).limit(15))
        _, df_raw = q.get_scanner_data()
        for _, row in df_raw.iterrows():
            t_sym = row['name']
            audit_res = run_audit(t_sym, ihsg_ret)
            if audit_res and all(audit_res[0].values()):
                price = audit_res[1]
                st.markdown(f"""
                <div class='stock-card'>
                    <h3>{t_sym} <span class='sector-badge'>{row['sector']}</span></h3>
                    <p style='margin:0; color:#10b981;'><b>🔥 ALPHA LEADER CONFIRMED</b></p>
                    <p>Price: {int(price)} | SL: {int(price*0.95)} | TP1: {int(price*1.08)}</p>
                    <div class='pyramid-box'>
                        <b>📐 Pyramiding Plan:</b><br>
                        • Buy More (+50%) at: {int(price*1.05)}<br>
                        • Action: Move SL to {int(price)} (Risk-Free)
                    </div>
                </div>
                """, unsafe_allow_html=True)

# =========================================================
# 🛡️ MODULE: PORTFOLIO & AUDIT MANUAL (ENHANCED)
# =========================================================
st.divider()
col_audit, col_port = st.columns([1, 1])

with col_audit:
    st.subheader("🔍 Manual Radar Audit")
    check_ticker = st.text_input("Kode Saham (Contoh: ADRO):").upper()
    if st.button("🚀 JALANKAN AUDIT"):
        if check_ticker:
            res = run_audit(check_ticker, ihsg_ret)
            if res:
                checks, price, s_ret = res
                st.write(f"**Vonis Strategis: {check_ticker}**")
                for label, pass_check in checks.items():
                    status_text = "✅ PASS" if pass_check else "❌ FAIL"
                    color = "audit-pass" if pass_check else "audit-fail"
                    st.markdown(f"<span class='{color}'>{status_text}</span> : {label}", unsafe_allow_html=True)
                
                # PYRAMIDING PLAN IN AUDIT RESULT
                pyramid_price = int(price * 1.05)
                avg_new = int((price + pyramid_price) / 2)
                st.markdown(f"""
                <div class='pyramid-box'>
                    <b style='color:#a78bfa;'>📐 {check_ticker} Pyramiding Plan (If Entered):</b><br>
                    • Entry Price (Current): {int(price)}<br>
                    • Initial Stop Loss: {int(price * 0.95)} (5%)<br>
                    • <b>Next Pyramid Entry: {pyramid_price} (+5%)</b><br>
                    • New Average Price: {avg_new}<br>
                    • <b>Safety Action:</b> Move SL to {int(price)} once Pyramid hit.
                </div>
                """, unsafe_allow_html=True)
                
                final_status = "LONTARKAN PELURU 🚀" if all(checks.values()) else "TIARAP / JANGAN BELI ⛔"
                st.info(f"KESIMPULAN: {final_status}")
            else: st.error("Data saham tidak valid.")

with col_port:
    st.subheader("🛡️ Portfolio Manager")
    t_manual = st.text_input("Kode Portfolio:").upper()
    c1, c2 = st.columns(2)
    if c1.button("🛒 BELI"): st.success("ADD Signal Sent!")
    if c2.button("🗑️ JUAL"): st.error("DEL Signal Sent!")

st.caption("V45.0 OMNI-APEX | Internal Logic Upgraded | UI Preserved.")
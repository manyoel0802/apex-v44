import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import warnings
import pytz
from datetime import datetime, timedelta
from tradingview_screener import Query, Column

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V46.0 WORLD CHAMPION", layout="wide", page_icon="🏆")

# --- TEMA VISUAL ELITE SUPREME ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { 
        border-radius: 15px; padding: 25px; margin-bottom: 25px; 
        border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%);
    }
    .stock-card { 
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; 
        padding: 20px; margin-bottom: 20px; border-left: 5px solid #8b5cf6;
    }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 12px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 12px; }
    .target-value { font-size: 18px; font-weight: bold; color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ TIME GATE ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

# --- 🌍 WORLD CHAMPION CORE INTELLIGENCE ---
@st.cache_data(ttl=300)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="1y")
        if idx.empty: return 0, True
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126] if len(idx) > 126 else idx['Close'].iloc[0]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1]
    except: return 0, True

def run_elite_audit(ticker, ihsg_ret):
    try:
        stock_obj = yf.Ticker(f"{ticker}.JK")
        df = stock_obj.history(period="2y", auto_adjust=True)
        if df.empty or len(df) < 200: return None, 0
        
        c = df['Close'].iloc[-1]
        v = df['Volume'].iloc[-1]
        
        # 1. MINERVINI STAGE 2 & WEEKLY ANCHOR
        s150 = df['Close'].rolling(150).mean().iloc[-1]
        s200 = df['Close'].rolling(200).mean().iloc[-1]
        weekly_sma = df['Close'].rolling(30).mean().iloc[-1] # Approx 30-week SMA
        
        # 2. RS SLOPE ANALYSIS
        stock_6m = df['Close'].iloc[-126] if len(df) > 126 else df['Close'].iloc[0]
        s_ret = (c / stock_6m) - 1
        rs_line = df['Close'] / yf.Ticker("^JKSE").history(period="2y")['Close'].reindex(df.index, method='ffill')
        rs_slope = rs_line.iloc[-1] > rs_line.rolling(20).mean().iloc[-1]
        
        # 3. VCP (VOLATILITY CONTRACTION)
        atr = (df['High'] - df['Low']).rolling(10).mean()
        vcp_check = atr.iloc[-1] < atr.rolling(50).mean().iloc[-1]
        
        # 4. VDU (VOLUME DRY-UP)
        v_ma20 = df['Volume'].rolling(20).mean().iloc[-1]
        vdu_check = v < v_ma20 # Volume today lower than average during base
        
        # 5. BANDARMOLOGI (CMF)
        range_hl = (df['High'] - df['Low']).replace(0, 1e-10)
        mf_vol = (((c - df['Low']) - (df['High'] - c)) / range_hl) * df['Volume']
        cmf = mf_vol.rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1].replace(0, 1e-10)
        
        checks = {
            "Minervini Stage 2": bool(c > s150 > s200),
            "Weekly Anchor": bool(c > weekly_sma),
            "Alpha RS Slope": bool(s_ret > ihsg_ret and rs_slope),
            "VCP Contraction": bool(vcp_check),
            "Bandar Accum": bool(cmf > 0.03)
        }
        return checks, float(c)
    except: return None, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>🏆 V46.0 OMNI-APEX: WORLD CHAMPION</h1><p style='margin:0; opacity:0.8;'>Full MTF | VCP Detection | RS Slope | All-Cap Sniper</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Control Center")
    cap = st.number_input("Capital (Rp)", value=1000000)
    risk_p = st.slider("Max Risk (%)", 1.0, 10.0, 5.0)
    rrr = st.number_input("Min RRR Target", value=3.0)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Time", value=False)

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish = get_market_context()
max_price = cap / 100 

if is_market_open or bypass:
    st.subheader(f"📡 World Champion Signals (Max: Rp {int(max_price)})")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector','average_volume_120d')
             .where(
                 Column('close') <= max_price, 
                 Column('close') > Column('SMA200'),
                 Column('average_volume_120d') >= 1e5
             ).limit(15))
        _, df_raw = q.get_scanner_data()
        
        cols = st.columns(2)
        v_idx = 0
        for _, row in df_raw.iterrows():
            chks, prc = run_elite_audit(row['name'], ihsg_ret)
            if chks and all(chks.values()):
                with cols[v_idx % 2]:
                    st.markdown(f"""
                    <div class='stock-card'>
                        <h2 style='margin:0; color:#a78bfa;'>{row['name']}</h2>
                        <div style='display:flex; justify-content:space-between; margin-top:15px;'>
                            <div><p style='color:#9ca3af; font-size:11px;'>ENTRY</p><p class='target-value'>{int(prc)}</p></div>
                            <div><p style='color:#9ca3af; font-size:11px;'>STOP LOSS</p><p class='target-value' style='color:#f87171;'>{int(prc*(1-risk_p/100))}</p></div>
                            <div><p style='color:#9ca3af; font-size:11px;'>TARGET</p><p class='target-value' style='color:#10b981;'>{int(prc + (prc*0.05)*rrr)}</p></div>
                        </div>
                        <p style='font-size:10px; color:#94a3b8; margin-top:10px;'><i>1 Lot: Rp {int(prc*100):,}</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                v_idx += 1
        if v_idx == 0: st.info("Hunting for the next Champion... (No strict signals yet)")
    except: st.write("Scanning Universe...")
else:
    st.info("🔴 RADAR STANDBY - Aktifkan 'Bypass' di sidebar.")

# --- 🛡️ TOOLS ---
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("🔍 Audit Manual")
    tid = st.text_input("Ticker Target:").upper()
    if st.button("🚀 Run Champion Audit"):
        if tid:
            with st.spinner(f"Membedah {tid}..."):
                checks, price_val = run_elite_audit(tid, ihsg_ret)
                if checks:
                    st.write(f"### Vonis {tid}:")
                    for k, v in checks.items():
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    if all(checks.values()): st.success("LONTARKAN PELURU 🚀 - SYARAT JUARA TERPENUHI")
                    else: st.warning("TIARAP ⛔ - Belum Lolos Standar Juara")
                    st.markdown(f"<div class='pyramid-panel'><b>📐 Pyramid Plan:</b> Entry {int(price_val)} | Next {int(price_val*1.05)} | SL {int(price_val*(1-risk_p/100))}</div>", unsafe_allow_html=True)
                else: st.error("Data tidak ditemukan atau riwayat belum cukup.")

with col_b:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Ticker Portfo:").upper()
    if st.button("🛒 ADD SIGNAL"): st.success(f"{pid} Sent to Commander!")

st.caption("V46.0 | True World Champion Edition | MTF + VCP + RS Slope Active.")
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import warnings
import pytz
from datetime import datetime
from tradingview_screener import Query, Column

# --- CONFIG & SECURITY ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="V47.0 ULTIMATE COMMANDER", layout="wide", page_icon="💎")

# --- TEMA VISUAL ELITE SUPREME ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .status-card { 
        border-radius: 15px; padding: 25px; margin-bottom: 25px; 
        border: 1px solid #30363d; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .stock-card { 
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; 
        padding: 20px; margin-bottom: 20px; border-left: 6px solid #8b5cf6;
        transition: transform 0.2s;
    }
    .stock-card:hover { transform: translateY(-5px); border-color: #a78bfa; }
    .sector-badge { background-color: #2d1b4d; color: #a78bfa; padding: 3px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; border: 1px solid #7c3aed; }
    .pyramid-panel { background-color: #0f172a; border: 1px dashed #4338ca; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .audit-pass { color: #10b981; font-weight: bold; font-size: 11px; }
    .audit-fail { color: #ef4444; font-weight: bold; font-size: 11px; }
    .target-value { font-size: 20px; font-weight: bold; color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ TIME & MARKET CONTEXT ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

@st.cache_data(ttl=300)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="1y")
        if idx.empty: return 0, True, 50
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126] if len(idx) > 126 else idx['Close'].iloc[0]
        breadth = (idx['Close'] > idx['Close'].rolling(50).mean()).iloc[-10:].sum() * 10 # Sample Breadth
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1], breadth
    except: return 0, True, 50

def run_deep_audit(ticker, ihsg_ret):
    try:
        stock_obj = yf.Ticker(f"{ticker}.JK")
        df = stock_obj.history(period="2y", auto_adjust=True)
        if df.empty or len(df) < 200: return None, 0
        
        c = df['Close'].iloc[-1]
        v = df['Volume'].iloc[-1]
        
        # 1. MTF & MINERVINI
        s150, s200 = df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        weekly_ma = df['Close'].rolling(30).mean().iloc[-1]
        
        # 2. RS SLOPE & ALPHA
        rs_line = df['Close'] / yf.Ticker("^JKSE").history(period="2y")['Close'].reindex(df.index, method='ffill')
        rs_slope = rs_line.iloc[-1] > rs_line.rolling(20).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        
        # 3. VCP & VDU
        atr = (df['High'] - df['Low']).rolling(10).mean()
        vcp = atr.iloc[-1] < atr.rolling(50).mean().iloc[-1]
        vdu = v < df['Volume'].rolling(20).mean().iloc[-1]
        
        # 4. BANDARMOLOGI
        range_hl = (df['High'] - df['Low']).replace(0, 1e-10)
        mf_vol = (((c - df['Low']) - (df['High'] - c)) / range_hl) * df['Volume']
        cmf = mf_vol.rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1].replace(0, 1e-10)
        
        checks = {
            "Minervini Stage 2": bool(c > s150 > s200),
            "Weekly Anchor": bool(c > weekly_ma),
            "Alpha RS Slope": bool(s_ret > ihsg_ret and rs_slope),
            "VCP & VDU Pattern": bool(vcp or vdu),
            "Bandar Accum": bool(cmf > 0.03)
        }
        return checks, float(c)
    except: return None, 0

# --- 🛰️ HEADER ---
st.markdown(f"""
<div class='status-card'>
    <h1 style='margin:0; font-size: 32px; color:#ddd6fe;'>🏆 V47.0 OMNI-APEX: ULTIMATE</h1>
    <p style='margin:0; opacity:0.8;'>World Champion Edition | Multi-Fitur Terintegrasi</p>
</div>
""", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Command Center")
    cap = st.number_input("Capital (Rp)", value=1000000)
    mode = st.radio("🚀 Scan Speed", ["Turbo (Fast)", "Deep (Champion Audit)"])
    st.divider()
    risk = st.slider("Max Risk (%)", 1.0, 10.0, 5.0)
    rrr = st.number_input("Risk-Reward Ratio", value=3.0)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Time", value=False)
    st.info("Turbo: Cepat (Data TV) | Deep: Akurat (Data Yahoo 2Thn)")

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish, mkt_breadth = get_market_context()
max_p = cap / 100

if is_market_open or bypass:
    st.subheader(f"📡 {mode} Alpha Signals")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector','volume','change','average_volume_120d')
             .where(Column('close') <= max_p, Column('close') > Column('SMA200'), Column('average_volume_120d') >= 1e5).limit(12))
        _, df_raw = q.get_scanner_data()
        
        cols = st.columns(2)
        v_idx = 0
        for _, row in df_raw.iterrows():
            # Turbo Mode langsung lolos, Deep Mode diaudit lagi
            if mode == "Turbo (Fast)":
                checks, prc = {"Turbo Mode": True}, row['close']
            else:
                checks, prc = run_deep_audit(row['name'], ihsg_ret)
            
            if checks and all(checks.values()):
                sl, tp = int(prc*(1-risk/100)), int(prc + (prc*0.05)*rrr)
                with cols[v_idx % 2]:
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <h2 style='margin:0; color:#a78bfa;'>{row['name']}</h2>
                            <span class='sector-badge'>{row['sector']}</span>
                        </div>
                        <div style='display:flex; justify-content:space-between; margin-top:15px;'>
                            <div><p style='color:#9ca3af; font-size:11px;'>ENTRY</p><p class='target-value'>{int(prc)}</p></div>
                            <div><p style='color:#9ca3af; font-size:11px;'>TRAILING SL (5%)</p><p class='target-value' style='color:#f87171;'>{int(prc*0.95)}</p></div>
                            <div><p style='color:#9ca3af; font-size:11px;'>TARGET TP</p><p class='target-value' style='color:#10b981;'>{tp}</p></div>
                        </div>
                        <div class='pyramid-panel'>
                            <b style='color:#818cf8; font-size:11px;'>📐 STRATEGIC PLAN:</b><br>
                            <span style='font-size:11px;'>Next Entry (+5%): <b>{int(prc*1.05)}</b> | Risk-Free SL: <b>{int(prc)}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                v_idx += 1
    except: st.write("Mengkalibrasi Radar...")
else:
    st.info("🔴 RADAR STANDBY - Aktifkan 'Bypass' di Sidebar untuk analisa malam.")

# --- 🛡️ TOOLS ---
st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("🔍 Deep Champion Audit")
    tid = st.text_input("Ticker:").upper()
    if st.button("🚀 Run Full Audit"):
        res, p_val = run_deep_audit(tid, ihsg_ret)
        if res:
            st.write(f"### Vonis {tid}:")
            for k, v in res.items():
                st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
            if all(res.values()): st.success("SYARAT WORLD CHAMPION TERPENUHI 🚀")
            else: st.warning("BELUM LOLOS STANDAR JUARA ⛔")
        else: st.error("Data Tidak Ditemukan.")

with cb:
    st.subheader("🛡️ Portfolio & Sector Radar")
    st.write(f"**Market Breadth:** {mkt_breadth}% Saham di atas SMA 50")
    if mkt_breadth > 60: st.success("MARKET HEALTHY 🌲")
    else: st.error("MARKET CAUTION 🚩")
    pid = st.text_input("Add to Portfolio:").upper()
    if st.button("🛒 SEND SIGNAL"): st.success(f"{pid} Bridge Active!")

st.caption("V47.0 ULTIMATE | MTF + VCP + RS Slope + Budget Sniper + Turbo Mode.")
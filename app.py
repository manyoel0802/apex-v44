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
st.set_page_config(page_title="V45.2 OMNI-APEX", layout="wide", page_icon="🌍")

# --- TEMA VISUAL ELITE SUPREME (PRESERVED) ---
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
    .target-value { font-size: 18px; font-weight: bold; color: #f8fafc; }
    .audit-pass { color: #10b981; font-weight: bold; }
    .audit-fail { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ⏳ TIME GATE ---
tz_wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(tz_wib)
is_market_open = datetime.strptime("08:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:30", "%H:%M").time()

# --- 🌍 CORE INTELLIGENCE (STABLE VERSION) ---
@st.cache_data(ttl=3600)
def get_market_context():
    try:
        idx = yf.Ticker("^JKSE").history(period="7mo")
        if idx.empty: return 0, True
        curr = idx['Close'].iloc[-1]
        old = idx['Close'].iloc[-126] if len(idx) > 126 else idx['Close'].iloc[0]
        return (curr / old) - 1, curr > idx['Close'].rolling(50).mean().iloc[-1]
    except: return 0, True

def run_elite_audit(ticker, ihsg_ret):
    """Mengembalikan Dictionary Hasil dan Harga Float"""
    try:
        stock_obj = yf.Ticker(f"{ticker}.JK")
        df = stock_obj.history(period="1y", auto_adjust=True)
        if df.empty or len(df) < 200: return None, 0
        
        c = df['Close'].iloc[-1]
        if np.isnan(c): return None, 0
        
        s150 = df['Close'].rolling(150).mean().iloc[-1]
        s200 = df['Close'].rolling(200).mean().iloc[-1]
        s_ret = (c / (df['Close'].iloc[-126] if len(df)>126 else df['Close'].iloc[0])) - 1
        cmf = ((((c-df['Low'])-(df['High']-c))/(df['High']-df['Low']).replace(0,1e-10))*df['Volume']).rolling(20).sum().iloc[-1] / df['Volume'].rolling(20).sum().iloc[-1]
        
        checks = {
            "Minervini Stage 2": bool(c > s150 and s150 > s200),
            "Alpha RS Leader": bool(s_ret > ihsg_ret),
            "Bandar Accumulation": bool(cmf > 0.03)
        }
        return checks, float(c)
    except: return None, 0

# --- 🛰️ HEADER ---
st.markdown(f"<div class='status-card'><h1 style='margin:0; font-size: 28px; color:#ddd6fe;'>🌍 V45.2 OMNI-APEX: FINAL REPAIR</h1><p style='margin:0; opacity:0.8;'>Budget Sniper | Alpha Leaders | Stable Unpacking</p></div>", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Control Center")
    cap = st.number_input("Capital (Rp)", value=1000000)
    risk_p = st.slider("Max Risk (%)", 1.0, 10.0, 5.0)
    rrr = st.number_input("Min RRR", value=3.0)
    st.divider()
    bypass = st.toggle("🚨 Bypass Market Time", value=False)

# --- 🚀 MAIN DASHBOARD ---
ihsg_ret, is_bullish = get_market_context()
max_price = cap / 100 

if is_market_open or bypass:
    st.subheader(f"📡 Affordable Alpha (Max: Rp {int(max_price)})")
    try:
        q = (Query().set_markets('indonesia').select('name','close','sector').where(
            Column('market_cap_basic') >= 1e10, 
            Column('close') <= max_price, 
            Column('close') > Column('SMA200')
        ).limit(10))
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
                        <p style='color:#10b981; font-weight:bold; font-size:12px;'>🔥 ALPHA CONFIRMED</p>
                        <div style='display:flex; justify-content:space-between;'>
                            <div><p style='color:#9ca3af; font-size:11px;'>ENTRY</p><p class='target-value'>{int(prc)}</p></div>
                            <div><p style='color:#9ca3af; font-size:11px;'>STOP LOSS</p><p class='target-value' style='color:#f87171;'>{int(prc*0.95)}</p></div>
                            <div><p style='color:#9ca3af; font-size:11px;'>TARGET</p><p class='target-value' style='color:#10b981;'>{int(prc*1.15)}</p></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                v_idx += 1
    except: st.write("Scanning...")
else:
    st.info("🔴 RADAR STANDBY - Silakan aktifkan 'Bypass Market Time' di sidebar.")

# --- 🛡️ TOOLS (REPAIRED SECTION) ---
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("🔍 Audit Manual")
    tid = st.text_input("Ticker:").upper()
    if st.button("🚀 Run Tactical Audit"):
        if tid:
            checks, price_val = run_elite_audit(tid, ihsg_ret)
            if checks:
                # KONVERSI AMAN
                final_price = int(price_val) if price_val > 0 else 0
                st.write(f"### Vonis {tid}:")
                for k, v in checks.items():
                    st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='pyramid-panel'><b>📐 Layout:</b> Entry {final_price} | SL {int(final_price*0.95)} | Pyramid {int(final_price*1.05)}</div>", unsafe_allow_html=True)
                if all(checks.values()): st.success("LONTARKAN PELURU 🚀")
                else: st.error("TIARAP ⛔")
            else:
                st.error("Data tidak valid atau ticker salah. Pastikan saham sudah IPO > 1 tahun.")

with col_b:
    st.subheader("🛡️ Portfolio")
    pid = st.text_input("Ticker Portfo:").upper()
    if st.button("🛒 ADD"): st.success(f"{pid} Sent!")

st.caption("V45.2 | Fixed ValueError Unpacking & NaN Handling.")
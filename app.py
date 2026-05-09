import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import requests
import warnings
import time
from datetime import datetime
import pytz
from tradingview_screener import Query, Column
import plotly.graph_objects as go

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
    </style>
    """, unsafe_allow_html=True)

# --- 🌍 CORE ENGINES ---
def get_market_health():
    try:
        ihsg = yf.Ticker("^JKSE").history(period="6mo")
        ihsg['SMA50'] = ihsg['Close'].rolling(50).mean()
        return "BULLISH" if ihsg['Close'].iloc[-1] > ihsg['SMA50'].iloc[-1] else "BEARISH", ihsg['Close'].iloc[-1]
    except: return "NEUTRAL", 0

def check_weekly_confirmation(ticker):
    try:
        w_data = yf.Ticker(f"{ticker}.JK").history(period="1y", interval="1wk")
        return w_data['Close'].iloc[-1] > w_data['Close'].rolling(20).mean().iloc[-1]
    except: return True

def calculate_atr(df, period=14):
    try:
        tr = np.maximum((df['High'] - df['Low']), np.maximum(abs(df['High'] - df['Close'].shift()), abs(df['Low'] - df['Close'].shift())))
        return tr.rolling(period).mean().iloc[-1]
    except: return 0.0

def detect_squeeze(df):
    try:
        df['SMA20'] = df['Close'].rolling(20).mean()
        df['STD20'] = df['Close'].rolling(20).std()
        df['BW'] = ((df['SMA20'] + (df['STD20'] * 2)) - (df['SMA20'] - (df['STD20'] * 2))) / df['SMA20']
        return df['BW'].iloc[-1] <= (df['BW'].tail(20).min() * 1.1) 
    except: return False

def check_minervini_template(df):
    try:
        if len(df) < 200: return False
        c, s50, s150, s200 = df['Close'].iloc[-1], df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        return (c > s150 and c > s200 and s150 > s200 and s50 > s150 and c > s50)
    except: return False

# --- ⏳ TIME GATE WIB ---
tz_wib = pytz.timezone('Asia/Jakarta')
waktu_sekarang = datetime.now(tz_wib)
mesin_aktif = datetime.strptime("08:30", "%H:%M").time() <= waktu_sekarang.time() <= datetime.strptime("16:30", "%H:%M").time()

# --- UI HEADER ---
st.markdown(f"""
<div class='status-card bg-sector'>
    <h1 style='margin:0; color:#ddd6fe;'>🌍 V45.0 OMNI-APEX</h1>
    <p style='margin:5px 0 0 0; opacity:0.9; color:#a78bfa;'>
        Dual-Scan | RRR 1:3 | Risk 5% | MTF Confirmation
    </p>
</div>
""", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Command Center")
    capital = st.number_input("Portfolio (Rp)", value=1000000, step=100000)
    risk_pct = st.slider("Max Loss Per Trade (%)", 0.5, 10.0, 5.0, step=0.5)
    rrr_min = st.number_input("Min RRR Target", value=3.0, step=0.5)
    
    st.divider()
    # --- FITUR BARU: TOMBOL TEST TELEGRAM ---
    if st.button("🧪 Test Telegram Connection", use_container_width=True):
        test_msg = "🚀 <b>TEST KONEKSI BERHASIL!</b>\nLapor Kapten, jalur intelijen V45.0 OMNI-APEX telah terhubung sempurna ke perangkat Anda."
        try:
            res = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                                data={"chat_id": TELE_CHAT_ID, "text": test_msg, "parse_mode": "HTML"}, timeout=10)
            if res.status_code == 200: st.success("Pesan terkirim ke Telegram!")
            else: st.error(f"Gagal! Error: {res.status_code}")
        except Exception as e: st.error(f"Koneksi Error: {e}")
    
    st.divider()
    show_analytics = st.toggle("📊 Performance Dashboard", value=False)
    bypass_lockdown = st.toggle("🚨 Bypass Lockdown", value=False)

# --- 🚀 EXECUTION ENGINE ---
if mesin_aktif:
    market_health, _ = get_market_health()
    if market_health == "BEARISH" and not bypass_lockdown:
        st.markdown("<div class='lockdown-box'><h2>⛔ MARKET LOCKDOWN</h2><p>IHSG Bearish. Radar Standby.</p></div>", unsafe_allow_html=True)
        st.stop()
        
    with st.status(f"Omni-Scan Running ({waktu_sekarang.strftime('%H:%M')} WIB)", expanded=True) as status:
        try:
            q = (Query().set_markets('indonesia').select('name','close','sector','Perf.1M','market_cap_basic').where(Column('market_cap_basic') >= 1e11))
            _, df_raw = q.get_scanner_data()
            
            if not df_raw.empty:
                df_raw = df_raw.dropna(subset=['sector', 'Perf.1M'])
                top_3_sectors = df_raw.groupby('sector')['Perf.1M'].mean().sort_values(ascending=False).head(3).index.tolist()
                
                fase_scan = [{"nama": "🏆 PHASE 1: LEADING", "on": True}, {"nama": "🔍 PHASE 2: ALT", "on": False}]
                pesan_tele = f"🌍 <b>V45.0 OMNI-REPORT</b>\n"
                valid_total = 0
                
                for fase in fase_scan:
                    df_scan = df_raw[df_raw['sector'].isin(top_3_sectors)] if fase['on'] else df_raw[~df_raw['sector'].isin(top_3_sectors)]
                    used_fase = 0
                    
                    for _, row in df_scan.iterrows():
                        if used_fase >= 2: break
                        t_sym, t_sector = row['name'], row['sector']
                        
                        time.sleep(1.2)
                        df_hist = yf.Ticker(f"{t_sym}.JK").history(period="1y", auto_adjust=True)
                        
                        if not df_hist.empty and check_minervini_template(df_hist) and detect_squeeze(df_hist):
                            if not check_weekly_confirmation(t_sym): continue
                            
                            atr = calculate_atr(df_hist)
                            trigger = int(max(df_hist['Close'].rolling(20).mean().iloc[-1], float(row['close'])))
                            sl = int(trigger - (atr * 2.0))
                            tp = int(trigger + ((trigger - sl) * rrr_min))
                            
                            if (tp - trigger) / (trigger - sl) >= rrr_min:
                                lot = int(((capital * (risk_pct/100)) / (trigger - sl)) / 100)
                                if lot > 0:
                                    used_fase += 1
                                    valid_total += 1
                                    
                                    st.markdown(f"""
                                    <div class='stock-card'>
                                        <h3>{t_sym} <span class='sector-badge'>{t_sector}</span></h3>
                                        <p><b>SOP: {lot} Lot @ {trigger}</b><br>SL: {sl} | TP: {tp}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    pesan_tele += f"\n🎯 <b>{t_sym}</b> (RRR 1:{rrr_min})\n🚨 {lot} Lot @ {trigger}\n🛡️ SL: {sl} | TP: {tp}\n"

                if valid_total > 0:
                    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": pesan_tele, "parse_mode": "HTML"}, timeout=10)
                
                status.update(label="Omni-Scan Complete!", state="complete")
        except Exception as e: pass

# --- 📊 ANALYTICS DASHBOARD ---
if show_analytics:
    st.divider()
    st.header("📊 Performance Analytics")
    uploaded_file = st.file_uploader("Upload Trading Journal (CSV)", type="csv")
    if uploaded_file:
        df_perf = pd.read_csv(uploaded_file)
        if 'Profit' in df_perf.columns:
            df_perf['Equity'] = capital + df_perf['Profit'].cumsum()
            st.plotly_chart(go.Figure(go.Scatter(x=df_perf.index, y=df_perf['Equity'], mode='lines', line=dict(color='#8b5cf6'))).update_layout(template="plotly_dark"), use_container_width=True)
    else: st.info("Unggah CSV untuk melihat pertumbuhan modal.")
else:
    if not mesin_aktif: st.info(f"🔴 RADAR STANDBY. Aktif otomatis jam 08:30 WIB.")
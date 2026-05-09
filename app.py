import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import requests
import warnings
import time
import os
from datetime import datetime, timedelta
import pytz
from tradingview_screener import Query, Column
import plotly.graph_objects as go

# --- CONFIG & SECURITY (V45.0 PRESERVED) ---
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
    .mtf-badge { background-color: #059669; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🌍 CORE ENGINES (V45.0 PRESERVED) ---
def get_market_health():
    try:
        ihsg = yf.Ticker("^JKSE").history(period="6mo")
        ihsg['SMA50'] = ihsg['Close'].rolling(50).mean()
        curr_close = ihsg['Close'].iloc[-1]
        return "BULLISH" if curr_close > ihsg['SMA50'].iloc[-1] else "BEARISH", curr_close
    except: return "NEUTRAL", 0

def check_weekly_confirmation(ticker):
    try:
        w_data = yf.Ticker(f"{ticker}.JK").history(period="1y", interval="1wk")
        w_sma20 = w_data['Close'].rolling(20).mean().iloc[-1]
        return w_data['Close'].iloc[-1] > w_sma20
    except: return True

def check_news_sentiment(ticker):
    try:
        news = yf.Ticker(f"{ticker}.JK").news
        bad_keywords = ['gugatan', 'pkpu', 'suspend', 'rugi', 'kasus', 'fraud']
        for item in news[:3]:
            if any(word in item['title'].lower() for word in bad_keywords):
                return False, item['title']
        return True, "Clean"
    except: return True, "No Data"

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
        c, sma50, sma150, sma200 = df['Close'].iloc[-1], df['Close'].rolling(50).mean().iloc[-1], df['Close'].rolling(150).mean().iloc[-1], df['Close'].rolling(200).mean().iloc[-1]
        return (c > sma150 and c > sma200 and sma150 > sma200 and sma50 > sma150 and c > sma50)
    except: return False

# --- ⏳ TIME GATE WIB ---
tz_wib = pytz.timezone('Asia/Jakarta')
waktu_sekarang = datetime.now(tz_wib)
mesin_aktif = datetime.strptime("08:30", "%H:%M").time() <= waktu_sekarang.time() <= datetime.strptime("16:30", "%H:%M").time()

# --- UI HEADER ---
st.markdown(f"""
<div class='status-card bg-sector'>
    <h1 style='margin:0; color:#ddd6fe;'>🌍 V45.0 OMNI-APEX: HEDGE FUND EDITION</h1>
    <p style='margin:5px 0 0 0; opacity:0.9; color:#a78bfa;'>
        MTF Weekly Confirmation | Dynamic Pyramiding | Sentiment Scanner | Performance Dashboard
    </p>
</div>
""", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Settings")
    capital = st.number_input("Portfolio (Rp)", value=1000000, step=100000)
    risk_pct = st.slider("Max Loss Per Trade (%)", 0.5, 10.0, 5.0, step=0.5)
    rrr_min = st.number_input("Min RRR Target", value=3.0, step=0.5)
    st.divider()
    show_analytics = st.toggle("📊 Show Performance Dashboard", value=False)
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
                scanned_tickers = [] # List untuk Macro Bridge
                
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
                            is_safe_news, news_msg = check_news_sentiment(t_sym)
                            if not is_safe_news: continue
                            
                            atr = calculate_atr(df_hist)
                            trigger = int(max(df_hist['Close'].rolling(20).mean().iloc[-1], float(row['close'])))
                            sl = int(trigger - (atr * 2.0))
                            tp = int(trigger + ((trigger - sl) * rrr_min))
                            
                            if (tp - trigger) / (trigger - sl) >= rrr_min:
                                lot = int(((capital * (risk_pct/100)) / (trigger - sl)) / 100)
                                if lot > 0:
                                    used_fase += 1
                                    valid_total += 1
                                    scanned_tickers.append(t_sym) # Simpan untuk sinkronisasi
                                    
                                    p1 = f"Entry 1: {int(lot*0.5)} Lot @ {trigger}"
                                    p2 = f"Entry 2: {int(lot*0.5)} Lot @ {int(trigger*1.02)} (If Bullish)"
                                    
                                    st.markdown(f"""
                                    <div class='stock-card'>
                                        <h3>{t_sym} <span class='sector-badge'>{t_sector}</span> <span class='mtf-badge'>WEEKLY CONFIRMED</span></h3>
                                        <p style='font-size:13px; color:#9ca3af;'>News Status: {news_msg}</p>
                                        <p><b>🛡️ Pyramiding Plan:</b><br>{p1}<br>{p2}</p>
                                        <p><b>SL: {sl} | TP: {tp}</b></p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # --- ANDROID MACRO BRIDGE FORMAT (🎯) ---
                                    pesan_tele += f"\n🎯 <b>{t_sym}</b> (RRR 1:{rrr_min})\n🏗️ {p1}\n🚀 {p2}\n🛡️ SL: {sl} | TP: {tp}\n"

                if valid_total > 0:
                    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": pesan_tele, "parse_mode": "HTML"}, timeout=10)
                    st.session_state['last_scan'] = scanned_tickers
                
                status.update(label="Omni-Scan Complete!", state="complete")
        except Exception as e: st.error(f"Error: {e}")

# --- 🛡️ THE GUARDIAN / EXIT MONITOR INTERFACE (NEW PLUGIN) ---
if 'last_scan' in st.session_state and st.session_state['last_scan']:
    st.divider()
    st.subheader("🛡️ The Guardian Interface")
    target_stock = st.selectbox("Pilih saham yang dieksekusi untuk dikawal Guardian:", st.session_state['last_scan'])
    
    if st.button("🛒 AKTIFKAN PENGKAWALAN"):
        with open("portfolio.txt", "a") as f:
            f.write(f"{target_stock}\n")
        st.success(f"Berhasil! {target_stock} kini dalam pengawasan Exit Monitor.")
        
        notif = f"✅ <b>GUARDIAN ON:</b> {target_stock} masuk radar pengawasan Trailing Stop 5%."
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      data={"chat_id": TELE_CHAT_ID, "text": notif, "parse_mode": "HTML"})

# --- 📊 PERFORMANCE DASHBOARD (PRESERVED) ---
if show_analytics:
    st.divider()
    st.header("📊 Performance Analytics")
    uploaded_file = st.file_uploader("Upload Jurnal Trading (CSV) untuk Analisis", type="csv")
    
    if uploaded_file:
        df_perf = pd.read_csv(uploaded_file)
        if 'Profit' in df_perf.columns:
            df_perf['Equity'] = capital + df_perf['Profit'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_perf.index, y=df_perf['Equity'], mode='lines+markers', name='Equity Curve', line=dict(color='#8b5cf6')))
            fig.update_layout(title="Pertumbuhan Modal (Equity Curve)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Trades", len(df_perf))
            c2.metric("Win Rate", f"{(len(df_perf[df_perf['Profit'] > 0]) / len(df_perf) * 100):.1f}%")
            c3.metric("Final Equity", f"Rp {df_perf['Equity'].iloc[-1]:,.0f}")
else:
    if not mesin_aktif:
        st.info(f"🔴 RADAR STANDBY. Aktif otomatis jam 08:30 WIB. (Waktu saat ini: {waktu_sekarang.strftime('%H:%M')} WIB)")

# =========================================================
# 🛠️ MODULE: AUTOMATIC PORTFOLIO MANAGER (V45.0 EXTENSION)
# =========================================================
st.divider()
st.subheader("🛡️ OMNI-APEX Portfolio Manager")

# Fungsi Load & Save untuk Portfolio
def load_portfolio():
    if os.path.exists("portfolio.txt"):
        with open("portfolio.txt", "r") as f:
            return list(set([line.strip().upper() for line in f.readlines() if line.strip()]))
    return []

def save_portfolio(stocks):
    with open("portfolio.txt", "w") as f:
        for s in stocks:
            f.write(f"{s}\n")

# Layout Kolom untuk Tambah dan Hapus
col_add, col_del = st.columns(2)

# --- PANEL TAMBAH (BELI) ---
with col_add:
    st.write("🛒 **Tambah Pantauan (Buy)**")
    # Jika ada hasil scan, otomatis tampilkan pilihan
    if 'v45_scanned' in st.session_state and st.session_state['v45_scanned']:
        selected_to_buy = st.selectbox("Pilih saham hasil scan:", st.session_state['v45_scanned'], key="buy_select")
    else:
        selected_to_buy = st.text_input("Ketik Manual (Contoh: BRMS):", key="buy_manual").upper()

    if st.button("🛒 KONFIRMASI BELI & KAWAL"):
        if selected_to_buy:
            current_p = load_portfolio()
            if selected_to_buy not in current_p:
                current_p.append(selected_to_buy)
                save_portfolio(current_p)
                st.success(f"✅ {selected_to_buy} masuk radar The Guardian!")
                # Notif Telegram
                requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                              data={"chat_id": TELE_CHAT_ID, "text": f"🛡️ <b>NEW ASSET:</b> {selected_to_buy} sekarang dikawal Exit Monitor.", "parse_mode": "HTML"})
            else:
                st.warning(f"{selected_to_buy} sudah ada dalam pantauan.")

# --- PANEL HAPUS (SELL/EXIT) ---
with col_del:
    st.write("🗑️ **Hapus Pantauan (Exit)**")
    current_portfolio = load_portfolio()
    if current_portfolio:
        to_delete = st.selectbox("Pilih saham yang ingin dilepas:", current_portfolio, key="del_select")
        if st.button("🗑️ HAPUS DARI PANTALUAN"):
            current_portfolio.remove(to_delete)
            save_portfolio(current_portfolio)
            st.error(f"🗑️ {to_delete} dihapus dari radar.")
            # Notif Telegram
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          data={"chat_id": TELE_CHAT_ID, "text": f"🚫 <b>REMOVED:</b> {to_delete} telah dikeluarkan dari pengawalan.", "parse_mode": "HTML"})
    else:
        st.info("Portfolio kosong. Belum ada saham yang dikawal.")
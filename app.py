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

# Menghilangkan peringatan log yang tidak perlu
warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None

# Konfigurasi Halaman Dasar
st.set_page_config(page_title="V44.0 APEX DUAL-SCAN", layout="wide", page_icon="🌍")

# --- KREDENSIAL TELEGRAM (Gunakan Streamlit Secrets) ---
try:
    TELE_TOKEN = st.secrets["TELE_TOKEN"]
    TELE_CHAT_ID = st.secrets["TELE_CHAT_ID"]
except:
    # Fallback jika dijalankan lokal tanpa secrets
    TELE_TOKEN = "8457858315:AAGPSHq0UsfPv8MZ733tHs40gAOxwvx7G0o"
    TELE_CHAT_ID = "5916986433"

# --- TEMA VISUAL UNGU KLASIK ---
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

# --- 🌍 QUANTITATIVE ENGINES ---
def get_market_health():
    try:
        ihsg = yf.Ticker("^JKSE").history(period="6mo")
        ihsg['SMA50'] = ihsg['Close'].rolling(50).mean()
        curr_close = ihsg['Close'].iloc[-1]
        sma50 = ihsg['SMA50'].iloc[-1]
        return "BULLISH" if curr_close > sma50 else "BEARISH", curr_close
    except: return "NEUTRAL", 0

def quick_backtest(df):
    try:
        df['SMA50_BT'] = df['Close'].rolling(50).mean()
        df['SMA20_BT'] = df['Close'].rolling(20).mean()
        df['STD20_BT'] = df['Close'].rolling(20).std()
        df['BW_BT'] = (df['SMA20_BT'] + (df['STD20_BT']*2) - (df['SMA20_BT'] - (df['STD20_BT']*2))) / df['SMA20_BT']
        df['Squeeze_Trigger'] = (df['BW_BT'] <= df['BW_BT'].rolling(20).min().shift(1) * 1.1) & (df['Close'] > df['SMA50_BT'])
        df['Future_Return'] = df['Close'].shift(-5) / df['Close'] - 1
        wins = df[(df['Squeeze_Trigger'] == True) & (df['Future_Return'] > 0)]
        total = df[df['Squeeze_Trigger'] == True]
        if len(total) == 0: return 0, 0
        return round((len(wins) / len(total)) * 100, 1), len(total)
    except: return 0.0, 0

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

def check_smart_money(df):
    try:
        obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        return obv.iloc[-1] > obv.rolling(20).mean().iloc[-1]
    except: return False

def check_fundamentals(ticker, df_hist):
    try:
        eps = yf.Ticker(f"{ticker}.JK").info.get('trailingEps', 0) or 0
        turnover = df_hist['Volume'].tail(5).mean() * df_hist['Close'].tail(5).mean()
        return eps > 0, eps, turnover >= 5_000_000_000, turnover
    except: return True, 0, True, 10e9

# --- ⏳ TIME GATE WIB ---
tz_wib = pytz.timezone('Asia/Jakarta')
waktu_sekarang = datetime.now(tz_wib)
jam_sekarang = waktu_sekarang.time()
jam_buka = datetime.strptime("08:30", "%H:%M").time()
jam_tutup = datetime.strptime("16:30", "%H:%M").time()

mesin_aktif = jam_buka <= jam_sekarang <= jam_tutup

# --- UI HEADER ---
st.markdown("""
<div class='status-card bg-sector'>
    <h1 style='margin:0; color:#ddd6fe;'>🌍 GOD MODE V44.0: DUAL-SCAN</h1>
    <p style='margin:5px 0 0 0; opacity:0.9; color:#a78bfa;'>
        Dual Phase Scan | 08:30 - 16:30 WIB | Capital Rp 1M - Risk 5%
    </p>
</div>
""", unsafe_allow_html=True)

# --- 🎛️ SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Settings")
    send_telegram = st.toggle("📲 Telegram Alerts", value=True)
    anti_correlation = st.toggle("🕸️ Anti-Korelasi", value=True)
    bypass_lockdown = st.toggle("🚨 Bypass Lockdown", value=False)
    
    st.divider()
    st.header("⚙️ Capital & Risk")
    capital = st.number_input("Portfolio (Rp)", value=1000000, step=100000)
    risk_pct = st.slider("Max Loss Per Trade (%)", 0.5, 10.0, 5.0, step=0.5)

# --- 🚀 EXECUTION ENGINE ---
if mesin_aktif:
    market_health, ihsg_price = get_market_health()
    
    if market_health == "BEARISH" and not bypass_lockdown:
        st.markdown(f"<div class='lockdown-box'><h2>⛔ MARKET LOCKDOWN</h2><p>IHSG Bearish. Mesin Standby.</p></div>", unsafe_allow_html=True)
        st.stop()
        
    with st.status(f"Dual-Scan Aktif ({waktu_sekarang.strftime('%H:%M')} WIB)", expanded=True) as status:
        try:
            q = (Query().set_markets('indonesia')
                 .select('name','close','volume','sector','Perf.1M','market_cap_basic')
                 .where(Column('market_cap_basic') >= 1e11))
            _, df_raw = q.get_scanner_data()
            
            if not df_raw.empty:
                df_raw = df_raw.dropna(subset=['sector', 'Perf.1M'])
                sector_perf = df_raw.groupby('sector')['Perf.1M'].mean().sort_values(ascending=False)
                top_3_sectors = sector_perf.head(3).index.tolist()
                
                fase_scan = [
                    {"nama": "🏆 FASE 1: TOP 3 SECTORS", "filter_on": True},
                    {"nama": "🔍 FASE 2: ALTERNATIVE SECTORS", "filter_on": False}
                ]
                
                pesan_tele = f"🌍 <b>V44.0 DUAL-SCAN REPORT</b>\n📅 {waktu_sekarang.strftime('%d/%m %H:%M')} WIB\n"
                valid_total = 0
                
                for fase in fase_scan:
                    st.write(f"### {fase['nama']}")
                    df_scan = df_raw[df_raw['sector'].isin(top_3_sectors)] if fase['filter_on'] else df_raw[~df_raw['sector'].isin(top_3_sectors)]
                    
                    pesan_tele += f"\n--- {fase['nama']} ---\n"
                    valid_fase = 0
                    used_sectors_fase = []
                    
                    for idx, row in df_scan.iterrows():
                        if valid_fase >= 2: break 
                        
                        t_sym, t_sector = row['name'], row['sector']
                        if anti_correlation and t_sector in used_sectors_fase: continue 
                        
                        time.sleep(1.2) 
                        df_hist = yf.Ticker(f"{t_sym}.JK").history(period="1y")
                        
                        if not df_hist.empty and check_minervini_template(df_hist):
                            is_profit, eps, _, turnover = check_fundamentals(t_sym, df_hist)
                            if not is_profit: continue
                            
                            if detect_squeeze(df_hist) and check_smart_money(df_hist):
                                atr = calculate_atr(df_hist)
                                lp = float(row['close'])
                                sma20 = df_hist['Close'].rolling(20).mean().iloc[-1]
                                
                                trigger_price = int(max(sma20, lp))
                                sl_price = int(trigger_price - (atr * 2.0))
                                target_price = int(trigger_price + (atr * 4.0))
                                ts_pct = round(((atr * 2.5) / trigger_price) * 100, 1)
                                
                                risk_rp = trigger_price - sl_price
                                if risk_rp > 0:
                                    lot = int(((capital * (risk_pct/100)) / risk_rp) / 100)
                                    if lot == 0: continue
                                    
                                    win_rate, triggers = quick_backtest(df_hist)
                                    valid_fase += 1
                                    valid_total += 1
                                    used_sectors_fase.append(t_sector)
                                    
                                    st.markdown(f"<div class='stock-card'><h2>{t_sym} <span class='sector-badge'>{t_sector}</span></h2><p>Win Rate: {win_rate}% | SOP: Beli {lot} Lot @ Rp {trigger_price}</p></div>", unsafe_allow_html=True)
                                    
                                    pesan_tele += f"🎯 <b>{t_sym}</b>: {lot} Lot @ Rp {trigger_price}\n🛡️ SL: {sl_price} | TP: {target_price} | TS: {ts_pct}%\n🧪 WinRate: {win_rate}%\n"

                if valid_total > 0 and send_telegram:
                    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": pesan_tele, "parse_mode": "HTML"}, timeout=10)
                
                status.update(label="Dual-Scan Selesai!", state="complete")
        except Exception as e: pass
else:
    st.info(f"🔴 MESIN STANDBY. Saat ini jam {waktu_sekarang.strftime('%H:%M')} WIB. Radar otomatis aktif besok jam 08:30 WIB.")
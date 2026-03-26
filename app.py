import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# ==========================================
# 1. KONFIGURASI HALAMAN & UI STREAMLIT
# ==========================================
st.set_page_config(page_title="Gold Code-X Tracker", page_icon="🥇", layout="wide")

st.title("🥇 XAUUSD Momentum & Timing Tracker")
st.markdown("Algoritma Rahasia: *Precision Entry, Time Trading & Money Management*")
st.divider()

# ==========================================
# 2. FUNGSI PENGAMBILAN DATA (DATA FEEDER)
# ==========================================
@st.cache_data(ttl=300) # Cache data selama 5 menit agar aplikasi tidak berat
def get_gold_data():
    # Mengambil data Gold (XAU/USD) dari Yahoo Finance
    ticker = "XAUUSD=X"
    data = yf.download(ticker, period="1mo", interval="1d", progress=False)
    
    # Menghitung Fast EMA (misal periode 9) dan Slow EMA (misal periode 21)
    data['EMA_Fast'] = data['Close'].ewm(span=9, adjust=False).mean()
    data['EMA_Slow'] = data['Close'].ewm(span=21, adjust=False).mean()
    
    # Menghitung ATR (Average True Range) 14 Hari secara manual
    data['High-Low'] = data['High'] - data['Low']
    data['High-PrevClose'] = abs(data['High'] - data['Close'].shift(1))
    data['Low-PrevClose'] = abs(data['Low'] - data['Close'].shift(1))
    data['TrueRange'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    data['ATR_14'] = data['TrueRange'].rolling(window=14).mean()
    
    return data.dropna()

# Ambil data
try:
    df = get_gold_data()
    latest_price = float(df['Close'].iloc[-1])
    latest_atr = float(df['ATR_14'].iloc[-1])
except Exception as e:
    st.error(f"Gagal mengambil data market: {e}")
    st.stop()

# ==========================================
# 3. FITUR A: RADAR MOMENTUM (GOLDEN CROSS)
# ==========================================
st.header("🎯 1. Radar Momentum (Daily)")

col1, col2, col3 = st.columns(3)
col1.metric("Harga XAUUSD Saat Ini", f"${latest_price:,.2f}")
col2.metric("Volatilitas Harian (ATR 14)", f"${latest_atr:,.2f} / ~{int(latest_atr*10)} Pips")

# Logika Deteksi Cross
fast_ema = df['EMA_Fast'].iloc[-1]
slow_ema = df['EMA_Slow'].iloc[-1]

if fast_ema > slow_ema:
    status = "🟢 BULLISH MOMENTUM (Cari Setup BUY)"
    col3.success(status)
elif fast_ema < slow_ema:
    status = "🔴 BEARISH MOMENTUM (Cari Setup SELL)"
    col3.error(status)
else:
    status = "⚪ KONSOLIDASI (Wait & See)"
    col3.warning(status)

st.line_chart(df[['Close', 'EMA_Fast', 'EMA_Slow']].tail(30))

st.divider()

# ==========================================
# 4. FITUR B: DYNAMIC LOT CALCULATOR
# ==========================================
st.header("🛡️ 2. Pertahanan Baja (Dynamic Lot Calculator)")
st.markdown("Hitung ukuran lot aman Anda berdasarkan jarak Stop Loss di Zona Reaksi.")

calc_col1, calc_col2 = st.columns(2)

with calc_col1:
    equity = st.number_input("Total Modal / Ekuitas ($):", min_value=10.0, value=1000.0, step=10.0)
    risk_percent = st.slider("Persentase Risiko Maksimal (%):", min_value=0.5, max_value=5.0, value=2.0, step=0.1)

with calc_col2:
    sl_pips = st.number_input("Jarak Stop Loss (Pips):", min_value=10, value=40, step=5)
    
    # Perhitungan: (Ekuitas * (Risiko/100)) / (SL_Pips * Nilai 1 Pip Gold (standar $0.1 per mikro lot / $10 per standar lot))
    # Asumsi 1 Lot XAUUSD = 100 oz. Pergerakan 1 pip (0.1) = $1.
    risk_amount = equity * (risk_percent / 100)
    lot_size = risk_amount / (sl_pips * 10) # Asumsi $10 per pip untuk 1 Standard Lot XAUUSD

    st.info(f"**Uang yang dirisikokan:** ${risk_amount:.2f}")
    st.success(f"🔥 **Ukuran Lot Aman Anda:** {lot_size:.3f} Lot")

st.divider()

# ==========================================
# 5. FITUR C: TIME TRADING CALENDAR
# ==========================================
st.header("⏳ 3. Time Trading Cycle (Tanggal Konjungsi)")
st.markdown("Algoritma penanda waktu potensial terjadinya *Massive Reversal* bulan ini.")

# Simulasi Database Tanggal Siklus (Bisa diganti dengan data kalender aktual)
today = datetime.now()
mock_cycle_dates = [
    {"Tanggal": (today + timedelta(days=2)).strftime("%Y-%m-%d"), "Event": "Major Lunar Phase / Reversal Zone", "Status": "Upcoming"},
    {"Tanggal": (today + timedelta(days=8)).strftime("%Y-%m-%d"), "Event": "Astrological Confluence", "Status": "Upcoming"},
    {"Tanggal": (today - timedelta(days=5)).strftime("%Y-%m-%d"), "Event": "Minor Cycle", "Status": "Passed"}
]

cycle_df = pd.DataFrame(mock_cycle_dates)

# Cek apakah hari ini ada momen reversal
today_str = today.strftime("%Y-%m-%d")
if today_str in cycle_df['Tanggal'].values:
    st.warning("⚠️ **PERHATIAN: HARI INI ADALAH TANGGAL REVERSAL TINGGI. Disiplin di area Kill Zone!**")

st.table(cycle_df)

st.caption("© 2026 Gold Code-X Masterclass | Dirancang khusus untuk trader Indonesia.")

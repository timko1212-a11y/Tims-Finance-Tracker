import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. KONFIGURATION: Hier kannst du deine Assets verwalten
# Format: "Ticker-Symbol": [Einstandspreis, "Name"]
MY_ASSETS = {
    "BTC-USD": [90000.0, "Bitcoin"],
    "ETH-USD": [2500.0, "Ethereum"],
    "XRP-USD": [1.90, "Ripple"],
    "AMZN": [180.0, "Amazon"],
    "NOVO-B.CO": [700.0, "Novo Nordisk"], # Kopenhagen Ticker
    "UNH": [540.0, "UnitedHealth"]
}

st.set_page_config(page_title="Family Finance Tracker", layout="wide")

st.title("🚀 Unser Familien-Finanz-Dashboard")
st.write("Aktuelle Kurse und Portfolio-Performance im Überblick.")

# 2. SIDEBAR: Einstellungen
st.sidebar.header("Einstellungen")
days_to_look_back = st.sidebar.slider("Zeitraum für Charts (Tage)", 7, 365, 30)

# 3. DATEN LADEN
@st.cache_data(ttl=600) # Daten werden 10 Min gespeichert
def get_data(tickers):
    data = yf.download(tickers, period=f"{days_to_look_back}d", interval="1d")
    return data['Close']

tickers = list(MY_ASSETS.keys())
prices_df = get_data(tickers)

# 4. BERECHNUNGEN & ÜBERSICHT
st.subheader("📊 Portfolio Übersicht")

rows = []
for ticker, info in MY_ASSETS.items():
    buy_price = info[0]
    name = info[1]
    
    # Aktueller Kurs (letzter verfügbarer Wert)
    current_price = prices_df[ticker].iloc[-1]
    
    # Performance seit Einstand
    perf_total = ((current_price - buy_price) / buy_price) * 100
    
    rows.append({
        "Asset": name,
        "Ticker": ticker,
        "Kaufpreis": f"{buy_price:,.2f}",
        "Aktuell": f"{current_price:,.2f}",
        "Performance (%)": round(perf_total, 2)
    })

df_display = pd.DataFrame(rows)

# Farbliches Hervorheben der Performance
def color_perf(val):
    color = 'green' if val > 0 else 'red'
    return f'color: {color}'

st.table(df_display.style.applymap(color_perf, subset=['Performance (%)']))

# 5. CHARTS (Performance-Entwicklung)
st.subheader(f"📈 Entwicklung (letzte {days_to_look_back} Tage)")

# Normalisierung auf 100% für besseren Vergleich
normalized_df = prices_df / prices_df.iloc[0] * 100
fig = px.line(normalized_df, labels={"value": "Index (Start=100)", "Date": "Datum"})
fig.update_layout(legend_title_text='Assets', hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.info("Hinweis: Die Daten werden automatisch von Yahoo Finance aktualisiert.")

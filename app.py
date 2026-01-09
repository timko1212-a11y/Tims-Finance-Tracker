import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. KONFIGURATION
# Ich habe die Ticker angepasst: AMZN und UNH brauchen meist kein ".US" bei Yahoo
MY_ASSETS = {
    "BTC-USD": [90000.0, "Bitcoin"],
    "ETH-USD": [2500.0, "Ethereum"],
    "XRP-USD": [1.90, "Ripple"],
    "AMZN": [180.0, "Amazon"],
    "NOVO-B.CO": [700.0, "Novo Nordisk"],
    "UNH": [540.0, "UnitedHealth"]
}

st.set_page_config(page_title="Family Finance", layout="wide")
st.title("🚀 Unser Familien-Finanz-Dashboard")

st.sidebar.header("Einstellungen")
days = st.sidebar.slider("Zeitraum (Tage)", 7, 365, 30)

# 2. DATEN LADEN (Optimiert für Zuverlässigkeit)
@st.cache_data(ttl=600)
def get_all_data(tickers, period_days):
    combined_data = pd.DataFrame()
    for t in tickers:
        ticker_obj = yf.Ticker(t)
        # Wir laden hier explizit die Historie für jedes Asset einzeln
        hist = ticker_obj.history(period=f"{period_days}d")
        if not hist.empty:
            combined_data[t] = hist['Close']
    return combined_data

tickers = list(MY_ASSETS.keys())
prices_df = get_all_data(tickers, days)

# 3. ÜBERSICHT ERSTELLEN
if not prices_df.empty:
    rows = []
    for ticker, info in MY_ASSETS.items():
        if ticker in prices_df.columns:
            buy_price = info[0]
            name = info[1]
            # Holen des aktuellsten Preises (letzter Wert ohne 'nan')
            valid_prices = prices_df[ticker].dropna()
            if not valid_prices.empty:
                current_price = valid_prices.iloc[-1]
                perf_total = ((current_price - buy_price) / buy_price) * 100
                
                rows.append({
                    "Asset": name,
                    "Kaufpreis": f"{buy_price:,.2f}",
                    "Aktuell": f"{current_price:,.2f}",
                    "Performance (%)": round(perf_total, 2)
                })

    df_display = pd.DataFrame(rows)

    def color_perf(val):
        return 'color: green' if val > 0 else 'color: red'

    st.subheader("📊 Portfolio Übersicht")
    st.table(df_display.style.applymap(color_perf, subset=['Performance (%)']))

    # 4. CHART
    st.subheader("📈 Relative Entwicklung")
    # Normalisierung (Start bei 100%), um Äpfel mit Birnen vergleichen zu können
    normalized_df = prices_df.copy()
    for col in normalized_df.columns:
        first_valid = normalized_df[col].dropna().iloc[0]
        normalized_df[col] = (normalized_df[col] / first_valid) * 100
    
    fig = px.line(normalized_df)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Keine Daten gefunden. Bitte Ticker-Symbole prüfen.")

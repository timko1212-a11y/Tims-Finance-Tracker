import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. KONFIGURATION
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

# 2. DATEN LADEN
@st.cache_data(ttl=600)
def get_all_data(tickers, period_days):
    combined_data = pd.DataFrame()
    for t in tickers:
        try:
            ticker_obj = yf.Ticker(t)
            hist = ticker_obj.history(period=f"{period_days}d")
            if not hist.empty:
                combined_data[t] = hist['Close']
        except:
            continue # Falls ein Ticker Fehler macht, einfach ignorieren
    return combined_data

tickers = list(MY_ASSETS.keys())
prices_df = get_all_data(tickers, days)

# 3. ÜBERSICHT
if not prices_df.empty:
    rows = []
    available_tickers = []
    
    for ticker, info in MY_ASSETS.items():
        if ticker in prices_df.columns:
            buy_price = info[0]
            name = info[1]
            valid_prices = prices_df[ticker].dropna()
            
            if not valid_prices.empty:
                current_price = valid_prices.iloc[-1]
                perf_total = ((current_price - buy_price) / buy_price) * 100
                available_tickers.append(ticker)
                
                rows.append({
                    "Asset": name,
                    "Kaufpreis": f"{buy_price:,.2f}",
                    "Aktuell": f"{current_price:,.2f}",
                    "Performance (%)": round(perf_total, 2)
                })

    if rows:
        df_display = pd.DataFrame(rows)
        st.subheader("📊 Portfolio Übersicht")
        st.table(df_display.style.applymap(lambda x: 'color: green' if x > 0 else 'color: red', subset=['Performance (%)']))

        # 4. CHART (Nur für Assets mit Daten)
        st.subheader("📈 Relative Entwicklung")
        chart_df = prices_df[available_tickers].dropna(how='all')
        
        # Normalisierung sicher durchführen
        normalized_df = pd.DataFrame()
        for col in chart_df.columns:
            series = chart_df[col].dropna()
            if not series.empty:
                normalized_df[col] = (series / series.iloc[0]) * 100
        
        if not normalized_df.empty:
            fig = px.line(normalized_df)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Es konnten keine aktuellen Kurse geladen werden. Bitte prüfe die Ticker-Symbole oder versuche es später erneut.")
else:
    st.error("Verbindung zu Finanzdaten fehlgeschlagen.")

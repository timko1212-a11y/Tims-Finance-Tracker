import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. KONFIGURATION (Deine Gesamtliste)
# Hier trägst du einmalig alles ein, was du besitzt oder beobachtest.
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

# 2. SEITENLEISTE (Interaktive Steuerung)
st.sidebar.header("Anzeige-Optionen")

# NEU: Direkt in der App Assets ein/ausblenden
selected_asset_names = st.sidebar.multiselect(
    "Welche Assets anzeigen?",
    options=[info[1] for info in MY_ASSETS.values()],
    default=[info[1] for info in MY_ASSETS.values()]
)

days = st.sidebar.slider("Zeitraum für Chart (Tage)", 7, 365, 30)

# Filtern der Ticker basierend auf der Auswahl
selected_tickers = [t for t, info in MY_ASSETS.items() if info[1] in selected_asset_names]

# 3. DATEN LADEN (Mit "Gedächtnis" für den letzten Kurs)
@st.cache_data(ttl=600)
def get_robust_data(tickers, period_days):
    combined_data = pd.DataFrame()
    for t in tickers:
        try:
            # Wir laden etwas mehr Daten, um sicher den letzten Kurs zu finden
            ticker_obj = yf.Ticker(t)
            hist = ticker_obj.history(period=f"{period_days + 5}d") 
            if not hist.empty:
                combined_data[t] = hist['Close']
        except:
            continue
    return combined_data

prices_df = get_robust_data(selected_tickers, days)

# 4. ÜBERSICHT
if not prices_df.empty:
    rows = []
    for ticker in selected_tickers:
        if ticker in prices_df.columns:
            buy_price = MY_ASSETS[ticker][0]
            name = MY_ASSETS[ticker][1]
            
            # Suche den letzten echten Wert (nicht nan)
            valid_series = prices_df[ticker].dropna()
            if not valid_series.empty:
                current_price = valid_series.iloc[-1]
                perf_total = ((current_price - buy_price) / buy_price) * 100
                
                rows.append({
                    "Asset": name,
                    "Kaufpreis": f"{buy_price:,.2f}",
                    "Aktuell": f"{current_price:,.2f}",
                    "Performance (%)": round(perf_total, 2)
                })

    if rows:
        df_display = pd.DataFrame(rows)
        st.subheader("📊 Aktuelle Portfolio Übersicht")
        st.table(df_display.style.applymap(lambda x: 'color: green' if x > 0 else 'color: red', subset=['Performance (%)']))

        # 5. CHART
        st.subheader("📈 Relative Entwicklung (Index 100)")
        chart_df = prices_df[selected_tickers].tail(days).copy()
        
        normalized_df = pd.DataFrame()
        for col in chart_df.columns:
            series = chart_df[col].dropna()
            if not series.empty:
                normalized_df[MY_ASSETS[col][1]] = (series / series.iloc[0]) * 100
        
        if not normalized_df.empty:
            fig = px.line(normalized_df)
            fig.update_layout(xaxis_title="Datum", yaxis_title="Wachstum in %", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Bitte wähle Assets in der Seitenleiste aus oder warte auf die Datenaktualisierung.")

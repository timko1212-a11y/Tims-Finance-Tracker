import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. KONFIGURATION
# Wichtig: Wir nutzen hier die stabilsten Ticker-Formate
MY_ASSETS = {
    "BTC-EUR": [90000.0, "Bitcoin"],
    "ETH-EUR": [2500.0, "Ethereum"],
    "XRP-EUR": [1.90, "Ripple"],
    "AMZN": [180.0, "Amazon"],
    "NOVO-B.CO": [700.0, "Novo Nordisk"],
    "UNH": [540.0, "UnitedHealth"]
}

st.set_page_config(page_title="Family Finance", layout="wide")
st.title("🚀 Familien-Dashboard (Multi-Currency)")

# 2. DATEN-FUNKTION (Sicherheits-Variante)
@st.cache_data(ttl=600)
def get_data_safe(tickers):
    data_dict = {}
    for t in tickers:
        try:
            # Wir holen nur den allerletzten verfügbaren Kurs
            ticker_obj = yf.Ticker(t)
            # '1mo' sorgt dafür, dass wir genug Historie haben, um Lücken zu füllen
            hist = ticker_obj.history(period="1mo")
            if not hist.empty:
                data_dict[t] = hist['Close']
        except:
            continue
    return pd.DataFrame(data_dict)

# Wechselkurse für die Anzeige-Umrechnung (Grobwerte als Backup)
@st.cache_data
def get_exchange_rates():
    try:
        usd_eur = yf.Ticker("EUR=X").history(period="1d")['Close'].iloc[-1] # Yahoo nutzt EUR=X für 1 USD in EUR
        dkk_eur = yf.Ticker("DKKEUR=X").history(period="1d")['Close'].iloc[-1]
        return 1/usd_eur, dkkeur # Korrektur für Yahoo-Logik
    except:
        return 0.92, 0.134 # Manuelle Backups falls API klemmt

# 3. LOGIK
tickers = list(MY_ASSETS.keys())
prices_df = get_data_safe(tickers)

st.sidebar.header("Optionen")
selected_names = st.sidebar.multiselect("Anzeigen:", [i[1] for i in MY_ASSETS.values()], [i[1] for i in MY_ASSETS.values()])

if not prices_df.empty:
    rows = []
    chart_data = pd.DataFrame()
    
    for ticker, info in MY_ASSETS.items():
        if info[1] in selected_names and ticker in prices_df.columns:
            # Letzten validen Preis finden
            series = prices_df[ticker].dropna()
            if len(series) > 0:
                current_val = series.iloc[-1]
                buy_val = info[0]
                
                # Performance-Berechnung (bleibt im Original-Verhältnis gleich)
                perf = ((current_val - buy_val) / buy_val) * 100
                
                rows.append({
                    "Asset": info[1],
                    "Kaufpreis": f"{buy_val:,.2f}",
                    "Aktuell": f"{current_val:,.2f}",
                    "Performance (%)": round(perf, 2)
                })
                # Daten für Chart (Normalisiert auf 100)
                chart_data[info[1]] = (series / series.iloc[0]) * 100

    # 4. AUSGABE
    if rows:
        st.subheader("📊 Portfolio Übersicht")
        st.table(pd.DataFrame(rows).style.applymap(lambda x: 'color: green' if x > 0 else 'color: red', subset=['Performance (%)']))
        
        if not chart_data.empty:
            st.subheader("📈 Relative Entwicklung")
            st.plotly_chart(px.line(chart_data.tail(30)), use_container_width=True)
    else:
        st.warning("Warte auf Daten von Yahoo Finance... (Börsen-Ticker werden geladen)")
else:
    st.error("Es konnten keine Daten geladen werden. Bitte Seite in 1 Minute neu laden.")

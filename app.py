import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. KONFIGURATION MIT WÄHRUNGEN
# Format: "Ticker": [Kaufpreis, "Name", "Währung des Kaufs"]
# Währungen: "USD", "EUR", "DKK" etc.
MY_ASSETS = {
    "BTC-EUR": [90000.0, "Bitcoin", "EUR"],
    "ETH-EUR": [2500.0, "Ethereum", "EUR"],
    "XRP-EUR": [1.90, "Ripple", "EUR"],
    "AMZN": [180.0, "Amazon", "USD"],
    "NOVO-B.CO": [700.0, "Novo Nordisk", "DKK"],
    "UNH": [540.0, "UnitedHealth", "USD"]
}

st.set_page_config(page_title="Family Finance", layout="wide")
st.title("🚀 Unser Familien-Finanz-Dashboard (in EUR)")

# 2. DATEN LADEN & WÄHRUNGSKURSE HOLEN
@st.cache_data(ttl=600)
def get_data_in_eur(assets_dict, period_days):
    df_final = pd.DataFrame()
    
    # Aktuelle Wechselkurse holen
    usdeur = yf.Ticker("USDEUR=X").history(period="1d")['Close'].iloc[-1]
    dkkeur = yf.Ticker("DKKEUR=X").history(period="1d")['Close'].iloc[-1]
    
    for ticker, info in assets_dict.items():
        try:
            data = yf.Ticker(ticker).history(period=f"{period_days+5}d")['Close']
            if data.empty: continue
            
            # Umrechnung in EUR basierend auf der Quellwährung bei Yahoo
            # Kryptos mit -EUR Suffix sind schon in Euro. 
            # US-Aktien (AMZN, UNH) kommen in USD -> mal usdeur
            # Novo (.CO) kommt in DKK -> mal dkkeur
            if ticker.endswith(".CO"):
                df_final[ticker] = data * dkkeur
            elif ticker.endswith("-EUR"):
                df_final[ticker] = data
            elif ticker.endswith("-USD") or ticker in ["AMZN", "UNH"]:
                df_final[ticker] = data * usdeur
            else:
                df_final[ticker] = data # Standardfall (z.B. schon EUR)
        except:
            continue
    return df_final

st.sidebar.header("Anzeige-Optionen")
selected_names = st.sidebar.multiselect("Assets", [i[1] for i in MY_ASSETS.values()], [i[1] for i in MY_ASSETS.values()])
days = st.sidebar.slider("Zeitraum", 7, 365, 30)

prices_eur = get_data_in_eur(MY_ASSETS, days)

# 3. DARSTELLUNG
if not prices_eur.empty:
    rows = []
    for ticker, info in MY_ASSETS.items():
        if info[1] in selected_names and ticker in prices_eur.columns:
            buy_price_eur = info[0] # Wir nehmen an, dein Kaufpreis war in EUR
            current_price_eur = prices_eur[ticker].dropna().iloc[-1]
            perf = ((current_price_eur - buy_price_eur) / buy_price_eur) * 100
            
            rows.append({
                "Asset": info[1],
                "Kauf (EUR)": f"{buy_price_eur:,.2f}",
                "Aktuell (EUR)": f"{current_price_eur:,.2f}",
                "Perf. (%)": round(perf, 2)
            })

    if rows:
        st.table(pd.DataFrame(rows).style.applymap(lambda x: 'color: green' if x > 0 else 'color: red', subset=['Perf. (%)']))
        
        # Chart
        chart_df = pd.DataFrame()
        for ticker, info in MY_ASSETS.items():
            if info[1] in selected_names and ticker in prices_eur.columns:
                series = prices_eur[ticker].dropna()
                chart_df[info[1]] = (series / series.iloc[0]) * 100
        
        st.plotly_chart(px.line(chart_df), use_container_width=True)

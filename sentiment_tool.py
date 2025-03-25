import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.title("📈 Sentiment Tracker")
st.write("Vul een tickersymbool in (zoals AAPL of ASML) om recent nieuws en sentiment te bekijken.")

ticker = st.text_input("🔍 Ticker:")

if ticker:
    try:
        st.subheader(f"Nieuws en sentiment voor {ticker.upper()}")
        stock = yf.Ticker(ticker)
        news = # Tijdelijke dummy-nieuwsdata
news = [
    {"title": "Apple beats expectations with strong Q4 results"},
    {"title": "iPhone sales slow down amid economic concerns"},
    {"title": "Apple announces new innovation in MacBooks"},
    {"title": "Tech stocks slide, Apple among biggest losers"},
    {"title": "Investors optimistic about Apple’s future"}
]


        if news:
            analyzer = SentimentIntensityAnalyzer()
            sentimenten = []

            for artikel in news[:5]:  # Alleen de laatste 5 artikelen
                titel = artikel['title']
                score = analyzer.polarity_scores(titel)['compound']

                if score >= 0.05:
                    oordeel = "✅ Positief"
                elif score <= -0.05:
                    oordeel = "❌ Negatief"
                else:
                    oordeel = "➖ Neutraal"

                st.write(f"📰 *{titel}*")
                st.write(f"→ Sentiment: {oordeel}")
                sentimenten.append(score)

            gemiddeld = sum(sentimenten) / len(sentimenten)
            st.markdown("---")
            st.subheader("📊 Gemiddeld sentiment:")
            if gemiddeld >= 0.05:
                st.success("Overwegend positief 📈")
            elif gemiddeld <= -0.05:
                st.error("Overwegend negatief 📉")
            else:
                st.info("Overwegend neutraal 🟰")
        else:
            st.warning("Geen nieuws gevonden voor dit ticker.")
    except Exception as e:
        st.error(f"Er is iets misgegaan bij het ophalen van het nieuws: {e}")


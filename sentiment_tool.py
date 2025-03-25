import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.graph_objects as go

# 🔑 Jouw NewsAPI-key (eventueel verplaatsbaar naar secrets)
NEWSAPI_KEY = st.secrets["newsapi"]["api_key"]

# 📊 Functie: Toon sentimentmeter
def toon_sentiment_meter(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={
            'axis': {'range': [-1, 1]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [-1.0, -0.6], 'color': "#ff4b4b"},      # Negatief
                {'range': [-0.6, -0.2], 'color': "#ffb347"},      # Licht negatief
                {'range': [-0.2,  0.2], 'color': "#ffe66d"},      # Neutraal
                {'range': [ 0.2,  0.6], 'color': "#a8e6cf"},      # Licht positief
                {'range': [ 0.6,  1.0], 'color': "#5cd65c"},      # Positief
            ],
        },
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "📊 Gemiddeld sentiment"}
    ))
    st.plotly_chart(fig, use_container_width=True)

# 🧠 Titel & uitleg
st.title("📊 Sentiment Tracker (Real-time & Gratis)")
st.markdown("### 📈 Analyseer automatisch het sentiment van beursnieuws (zonder GPT)")
st.write("Voer een ticker of bedrijfsnaam in zoals `Apple`, `Tesla` of `ASML`. We halen real-time nieuws op en analyseren het met VADER.")

# 🔍 Inputveld
ticker = st.text_input("🔍 Zoekterm:", value="Apple")

if ticker:
    st.markdown("---")
    st.subheader(f"📰 Nieuws & sentiment voor **{ticker.upper()}**")

    # 🔎 Haal nieuws op van NewsAPI
    try:
        url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&pageSize=5&apiKey={NEWSAPI_KEY}"
        r = requests.get(url)
        articles = r.json().get("articles", [])
    except Exception as e:
        st.error(f"Fout bij ophalen van nieuws: {e}")
        articles = []

    analyzer = SentimentIntensityAnalyzer()
    sentiments = []

    for artikel in articles:
        titel = artikel.get("title", "Geen titel")
        url = artikel.get("url", "")
        score = analyzer.polarity_scores(titel)["compound"]
        sentiments.append(score)

        with st.container():
            st.markdown("#### 📰 Nieuwsbericht")
            st.write(f"[{titel}]({url})")

            st.markdown("#### 💡 Sentimentanalyse (VADER)")
            if score <= -0.6:
                st.error(f"Negatief sentiment ({score:.2f})")
            elif score <= -0.2:
                st.warning(f"Licht negatief ({score:.2f})")
            elif score < 0.2:
                st.info(f"Neutraal ({score:.2f})")
            elif score < 0.6:
                st.success(f"Licht positief ({score:.2f})")
            else:
                st.success(f"Positief sentiment ({score:.2f})")
            st.markdown("---")

    # 📉 Toon gemiddelde
    if sentiments:
        gemiddeld = sum(sentiments) / len(sentiments)
        toon_sentiment_meter(gemiddeld)

# 📘 Footer
st.markdown("---")
st.caption("Gemaakt door Ewout • Gratis sentimentanalyse met VADER & NewsAPI")




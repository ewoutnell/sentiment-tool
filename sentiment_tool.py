import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.graph_objects as go
import math

# 🔐 Haal API-key uit secrets
NEWSAPI_KEY = st.secrets["newsapi"]["api_key"]

# 🧭 Klokstijl sentimentmeter
def toon_klokstijl_wijzer(score):
    angle = (1 - score) * math.pi  # -1 = 180°, +1 = 0°
    x = 0.5 + 0.4 * math.cos(angle)
    y = 0.5 + 0.4 * math.sin(angle)

    fig = go.Figure()

    # Wijzer (wit)
    fig.add_trace(go.Scatter(
        x=[0.5, x],
        y=[0.5, y],
        mode="lines+markers",
        line=dict(color="white", width=4),
        marker=dict(size=10, color="white"),
        showlegend=False
    ))

    # Stip (groen referentiepunt)
    fig.add_trace(go.Scatter(
        x=[0.5],
        y=[0.9],
        mode="markers",
        marker=dict(size=10, color="green"),
        showlegend=False
    ))

    # Stijl
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="black",
        paper_bgcolor="black",
        width=300,
        height=300,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig)

# 🧠 Titel & uitleg
st.title("📊 Sentiment Tracker (Realtime & Gratis)")
st.markdown("### 📈 Analyseer automatisch het sentiment van beursnieuws (zonder GPT)")
st.write("Voer een bedrijf of ticker in zoals `Apple`, `Tesla` of `ASML`. Wij tonen real-time nieuws en analyseren het met VADER.")

# 🔍 Zoekveld
zoekterm = st.text_input("🔍 Zoekterm:", value="Apple")

if zoekterm:
    st.markdown("---")

    # 📡 Nieuws ophalen van NewsAPI
    try:
        url = f"https://newsapi.org/v2/everything?q={zoekterm}&sortBy=publishedAt&pageSize=5&apiKey={NEWSAPI_KEY}"
        r = requests.get(url)
        articles = r.json().get("articles", [])
    except Exception as e:
        st.error(f"Fout bij ophalen van nieuws: {e}")
        articles = []

    analyzer = SentimentIntensityAnalyzer()
    sentiments = []

    # 🔢 VADER-score per artikel
    for artikel in articles:
        titel = artikel.get("title", "Geen titel")
        url = artikel.get("url", "")
        score = analyzer.polarity_scores(titel)["compound"]
        sentiments.append(score)

    # 📍 Sentimentmeter direct onder zoekveld
    if sentiments:
        gemiddeld = sum(sentiments) / len(sentiments)
        st.subheader("🧭 Gemiddeld sentiment")
        toon_klokstijl_wijzer(gemiddeld)

    # 🔁 Artikelen en analyses tonen
    st.subheader(f"📰 Nieuws & sentiment over **{zoekterm.upper()}**")

    for i, artikel in enumerate(articles):
        titel = artikel.get("title", "Geen titel")
        url = artikel.get("url", "")
        score = sentiments[i]

        with st.container():
            st.markdown("#### 📰 Nieuwsbericht")
            st.write(f"[{titel}]({url})")

            st.markdown("#### 💡 VADER-analyse")
            if score <= -0.6:
                st.error(f"Negatief ({score:.2f})")
            elif score <= -0.2:
                st.warning(f"Licht negatief ({score:.2f})")
            elif score < 0.2:
                st.info(f"Neutraal ({score:.2f})")
            elif score < 0.6:
                st.success(f"Licht positief ({score:.2f})")
            else:
                st.success(f"Positief ({score:.2f})")
            st.markdown("---")

# 📘 Footer
st.markdown("---")
st.caption("Gemaakt door Ewout • Realtime sentimentanalyse met VADER & NewsAPI")



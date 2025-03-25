import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.graph_objects as go
import math

# 🔐 NewsAPI-key uit secrets
NEWSAPI_KEY = st.secrets["newsapi"]["api_key"]

# 🕰️ Luxe klokstijl sentimentmeter
def toon_klokstijl_sentimentmeter(score):
    angle = (1 - score) * math.pi  # van -1 (links) tot +1 (rechts)
    x = 0.5 + 0.35 * math.cos(angle)
    y = 0.5 + 0.35 * math.sin(angle)

    fig = go.Figure()

    # Wijzerplaat (diepgroen)
    fig.add_shape(
        type="circle",
        x0=0.08, y0=0.08, x1=0.92, y1=0.92,
        fillcolor="#1f4f3d",
        line=dict(color="#cccccc", width=2)
    )

    # Indexstrepen zoals een klok (13 streepjes)
    for i in range(13):
        a = math.pi - i * (math.pi / 6)
        x0 = 0.5 + 0.38 * math.cos(a)
        y0 = 0.5 + 0.38 * math.sin(a)
        x1 = 0.5 + 0.42 * math.cos(a)
        y1 = 0.5 + 0.42 * math.sin(a)
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color="white", width=2))

    # Wijzer (wit)
    fig.add_trace(go.Scatter(
        x=[0.5, x],
        y=[0.5, y],
        mode="lines",
        line=dict(color="white", width=6),
        showlegend=False
    ))

    # Layout
    fig.update_layout(
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1]),
        plot_bgcolor="#1f4f3d",
        paper_bgcolor="#1f4f3d",
        width=350,
        height=350,
        margin=dict(l=0, r=0, t=10, b=10)
    )

    st.plotly_chart(fig)

# 🧠 Titel & uitleg
st.title("📊 Sentiment Tracker (Realtime & Gratis)")
st.markdown("### 📈 Analyseer automatisch het sentiment van beursnieuws")
st.write("Typ een bedrijf of ticker zoals `Apple`, `Tesla` of `ASML`. Wij halen live nieuws op en analyseren het met VADER.")

# 🔍 Zoekveld
zoekterm = st.text_input("🔍 Zoekterm:", value="Apple")

if zoekterm:
    st.markdown("---")

    # 📡 Nieuws ophalen
    try:
        url = f"https://newsapi.org/v2/everything?q={zoekterm}&sortBy=publishedAt&pageSize=5&apiKey={NEWSAPI_KEY}"
        r = requests.get(url)
        articles = r.json().get("articles", [])
    except Exception as e:
        st.error(f"Fout bij ophalen van nieuws: {e}")
        articles = []

    analyzer = SentimentIntensityAnalyzer()
    sentiments = []

    # 🔢 Analyseer elk artikel
    for artikel in articles:
        titel = artikel.get("title", "Geen titel")
        url = artikel.get("url", "")
        score = analyzer.polarity_scores(titel)["compound"]
        sentiments.append(score)

    # 🕰️ Toon klokstijl sentimentmeter
    if sentiments:
        gemiddeld = sum(sentiments) / len(sentiments)
        st.subheader("🧭 Gemiddeld sentiment")
        toon_klokstijl_sentimentmeter(gemiddeld)

    # 📄 Toon artikelen en scores
    st.subheader(f"📰 Nieuws & analyse voor **{zoekterm.upper()}**")

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
st.caption("Gemaakt door Ewout • Sentimentanalyse met VADER & NewsAPI")


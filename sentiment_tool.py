import streamlit as st
import requests
import feedparser
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import math

NEWSAPI_KEY = st.secrets["newsapi"]["api_key"]

def haal_newsapi_headlines(query, api_key):
    url = f"https://newsapi.org/v2/everything?q={query} stock&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
    r = requests.get(url)
    data = r.json()
    return [a["title"] for a in data.get("articles", [])]

def haal_yahoo_rss_headlines(ticker):
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(rss_url)
    return [entry["title"] for entry in feed.entries[:5]]

def analyseer_met_vader(titels):
    analyzer = SentimentIntensityAnalyzer()
    resultaten = []
    for titel in titels:
        score = analyzer.polarity_scores(titel)["compound"]
        resultaten.append((titel, score))
    return resultaten

def toon_klokstijl_sentimentmeter(score):
    angle = (1 - score) * math.pi
    x = 0.5 + 0.35 * math.cos(angle)
    y = 0.5 + 0.35 * math.sin(angle)

    fig = go.Figure()

    # Wijzerplaat
    fig.add_shape(type="circle", x0=0.08, y0=0.08, x1=0.92, y1=0.92,
                  fillcolor="#1f4f3d", line=dict(color="#cccccc", width=2))

    # Indexstrepen
    for i in range(13):
        a = math.pi - i * (math.pi / 6)
        x0 = 0.5 + 0.38 * math.cos(a)
        y0 = 0.5 + 0.38 * math.sin(a)
        x1 = 0.5 + 0.42 * math.cos(a)
        y1 = 0.5 + 0.42 * math.sin(a)
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color="white", width=2))

    # Wijzer
    fig.add_trace(go.Scatter(
        x=[0.5, x],
        y=[0.5, y],
        mode="lines",
        line=dict(color="white", width=6),
        showlegend=False
    ))

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

# UI
st.title("📊 Sentiment Tracker")
st.markdown("Gecombineerde sentimentanalyse via NewsAPI & Yahoo Finance RSS.")
zoekterm = st.text_input("🔍 Ticker of bedrijfsnaam:", value="Apple")

if zoekterm:
    st.markdown("---")

    # 📡 Haal nieuws op uit beide bronnen
    newsapi_titels = haal_newsapi_headlines(zoekterm, NEWSAPI_KEY)
    yahoo_titels = haal_yahoo_rss_headlines(zoekterm)

    alle_titels = newsapi_titels + yahoo_titels
    if not alle_titels:
        st.warning("Geen nieuws gevonden. Probeer een andere zoekterm.")
    else:
        resultaten = analyseer_met_vader(alle_titels)
        gemidd_score = sum([s for _, s in resultaten]) / len(resultaten)

        st.subheader("🧭 Gemiddeld sentiment")
        toon_klokstijl_sentimentmeter(gemidd_score)

        # 📰 Toon nieuwsitems met scores
        st.subheader("📄 Nieuwsberichten & scores")
        for titel, score in resultaten:
            with st.container():
                st.markdown(f"**{titel}**")
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


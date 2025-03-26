import streamlit as st
import requests
import feedparser
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Haal je NewsAPI-key uit secrets
NEWSAPI_KEY = st.secrets["newsapi"]["api_key"]

# 🧠 Sentimentzones
ZONES = [
    {"label": "Negatief", "min": -1.0, "max": -0.6, "color": "#d62728"},
    {"label": "Licht negatief", "min": -0.6, "max": -0.2, "color": "#ff7f0e"},
    {"label": "Neutraal", "min": -0.2, "max": 0.2, "color": "#ffdd57"},
    {"label": "Licht positief", "min": 0.2, "max": 0.6, "color": "#2ca02c"},
    {"label": "Positief", "min": 0.6, "max": 1.0, "color": "#1f77b4"},
]

# 📊 Teken de 5-zone sentimentmeter
def teken_sentimentmeter(score):
    fig = go.Figure()

    # Voeg de zones toe als rechthoeken
    for zone in ZONES:
        fig.add_shape(
            type="rect",
            x0=zone["min"], y0=0, x1=zone["max"], y1=0.2,
            fillcolor=zone["color"],
            line=dict(width=0)
        )
        fig.add_annotation(
            x=(zone["min"] + zone["max"]) / 2,
            y=0.25,
            text=zone["label"],
            showarrow=False,
            font=dict(size=12)
        )

    # Voeg de wijzer toe
    fig.add_shape(
        type="line",
        x0=score, x1=score,
        y0=0.25, y1=0.35,
        line=dict(color="white", width=4)
    )

    fig.update_layout(
        xaxis=dict(range=[-1, 1], visible=False),
        yaxis=dict(range=[0, 0.5], visible=False),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        width=600,
        height=180,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig)

# Nieuws ophalen
def haal_newsapi_headlines(query):
    url = f"https://newsapi.org/v2/everything?q={query} stock&sortBy=publishedAt&pageSize=5&apiKey={NEWSAPI_KEY}"
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

# 🧠 UI
st.title("📊 Sentiment Tracker")
st.markdown("Professionele 5-zone sentimentmeter met realtime nieuws.")

zoekterm = st.text_input("🔍 Ticker of bedrijfsnaam:", value="Apple")

if zoekterm:
    st.markdown("---")

    newsapi_titels = haal_newsapi_headlines(zoekterm)
    yahoo_titels = haal_yahoo_rss_headlines(zoekterm)
    alle_titels = newsapi_titels + yahoo_titels

    if not alle_titels:
        st.warning("Geen nieuws gevonden. Probeer een andere zoekterm.")
    else:
        resultaten = analyseer_met_vader(alle_titels)
        gemiddeld = sum([s for _, s in resultaten]) / len(resultaten)

        st.subheader("🧭 Gemiddeld sentiment")
        teken_sentimentmeter(gemiddeld)

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


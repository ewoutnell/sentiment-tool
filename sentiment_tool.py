import streamlit as st
import requests
import feedparser
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

# Haal je NewsAPI-key uit secrets
NEWSAPI_KEY = st.secrets["newsapi"]["api_key"]

# 📊 Gradient sentimentmeter met wijzer en schaal
def teken_sentimentmeter(score):
    fig = go.Figure()

    # Simuleer kleurverloop met dunne segmenten
    x_vals = np.linspace(-1, 1, 100)
    for i in range(len(x_vals)-1):
        x0, x1 = x_vals[i], x_vals[i+1]
        kleur = get_gradient_color(x0)
        fig.add_shape(
            type="rect",
            x0=x0, y0=0, x1=x1, y1=0.2,
            fillcolor=kleur,
            line=dict(width=0)
        )

    # Wijzer
    fig.add_shape(
        type="line",
        x0=score, x1=score,
        y0=0.22, y1=0.32,
        line=dict(color="white", width=4)
    )

    # Numerieke schaal onder de balk
    for val in np.linspace(-1, 1, 9):
        fig.add_annotation(
            x=val,
            y=-0.05,
            text=f"{val:.1f}",
            showarrow=False,
            font=dict(color="white", size=10)
        )

    fig.update_layout(
        xaxis=dict(range=[-1, 1], visible=False),
        yaxis=dict(range=[-0.1, 0.4], visible=False),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        width=650,
        height=200,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig)

# 🎨 Genereer kleurgradient (rood → geel → groen → blauw)
def get_gradient_color(x):
    if x <= -0.6:
        return "#d62728"  # rood
    elif x <= -0.2:
        return "#ff7f0e"  # oranje
    elif x <= 0.2:
        return "#ffdd57"  # geel
    elif x <= 0.6:
        return "#2ca02c"  # groen
    else:
        return "#1f77b4"  # blauw

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
st.markdown("Professionele sentimentmeter met kleurverloop & schaal (-1 tot +1)")

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


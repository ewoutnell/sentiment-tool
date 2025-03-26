import streamlit as st
import requests
import feedparser
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

# 🔐 API key
NEWSAPI_KEY = st.secrets["newsapi"]["api_key"]

# 🎯 Gauge met halve cirkel en kleurverloop

def draw_sentiment_gauge(score):
    fig = go.Figure()

    # Boog (semi-donut shape) met kleurverloop
    angles = np.linspace(-180, 0, 100)
    x0, y0 = 0.5, 0.5
    radius = 0.4

    for i in range(len(angles) - 1):
        theta0 = np.radians(angles[i])
        theta1 = np.radians(angles[i + 1])

        x_start = x0 + radius * np.cos(theta0)
        y_start = y0 + radius * np.sin(theta0)
        x_end = x0 + radius * np.cos(theta1)
        y_end = y0 + radius * np.sin(theta1)

        color = get_gauge_gradient((i + 1) / len(angles))

        fig.add_shape(
            type="line",
            x0=x_start, y0=y_start,
            x1=x_end, y1=y_end,
            line=dict(color=color, width=10)
        )

    # Wijzer
    angle = (1 - (score + 1) / 2) * np.pi
    x_pointer = x0 + 0.35 * np.cos(angle)
    y_pointer = y0 + 0.35 * np.sin(angle)
    fig.add_shape(
        type="line",
        x0=x0, y0=y0,
        x1=x_pointer, y1=y_pointer,
        line=dict(color="white", width=5)
    )

    # Labels
    fig.add_annotation(x=0.15, y=0.1, text="–", showarrow=False, font=dict(color="white", size=16))
    fig.add_annotation(x=0.85, y=0.1, text="+", showarrow=False, font=dict(color="white", size=16))

    fig.update_layout(
        xaxis=dict(range=[0, 1], visible=False),
        yaxis=dict(range=[0, 1], visible=False),
        plot_bgcolor="black",
        paper_bgcolor="black",
        width=500,
        height=300,
        margin=dict(l=0, r=0, t=10, b=10)
    )

    st.plotly_chart(fig)

# 🎨 Kleurverloop op basis van positie

def get_gauge_gradient(position):
    if position <= 0.25:
        return "#d62728"
    elif position <= 0.45:
        return "#ff7f0e"
    elif position <= 0.65:
        return "#ffdd57"
    elif position <= 0.85:
        return "#2ca02c"
    else:
        return "#1f77b4"

# 📡 Nieuws ophalen

def get_newsapi_headlines(query):
    url = f"https://newsapi.org/v2/everything?q={query} stock&sortBy=publishedAt&pageSize=5&apiKey={NEWSAPI_KEY}"
    r = requests.get(url)
    data = r.json()
    return [a["title"] for a in data.get("articles", [])]

def get_yahoo_rss_headlines(ticker):
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(rss_url)
    return [entry["title"] for entry in feed.entries[:5]]

def analyze_with_vader(titles):
    analyzer = SentimentIntensityAnalyzer()
    results = []
    for title in titles:
        score = analyzer.polarity_scores(title)["compound"]
        results.append((title, score))
    return results

# 🧠 UI
st.title("📊 Sentiment Tracker")
st.markdown("Visual sentiment gauge with curved gradient and live news analysis.")

query = st.text_input("🔍 Company name or ticker:", value="Apple")

if query:
    st.markdown("---")

    newsapi_titles = get_newsapi_headlines(query)
    yahoo_titles = get_yahoo_rss_headlines(query)
    all_titles = newsapi_titles + yahoo_titles

    if not all_titles:
        st.warning("No news found. Try a different company or ticker.")
    else:
        results = analyze_with_vader(all_titles)
        avg_score = sum([s for _, s in results]) / len(results)

        st.subheader("🧭 Average Sentiment")
        draw_sentiment_gauge(avg_score)

        st.subheader("📰 News & Sentiment Scores")
        for title, score in results:
            with st.container():
                st.markdown(f"**{title}**")
                if score <= -0.6:
                    st.error(f"Negative ({score:.2f})")
                elif score <= -0.2:
                    st.warning(f"Slightly Negative ({score:.2f})")
                elif score < 0.2:
                    st.info(f"Neutral ({score:.2f})")
                elif score < 0.6:
                    st.success(f"Slightly Positive ({score:.2f})")
                else:
                    st.success(f"Positive ({score:.2f})")
                st.markdown("---")


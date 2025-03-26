import streamlit as st
import requests
import feedparser
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

# 🔐 API key
NEWSAPI_KEY = st.secrets["newsapi"]["api_key"]

# 🎨 Gradient bar with sentiment pointer
def draw_sentiment_meter(score):
    fig = go.Figure()

    # Add a smooth gradient bar using an image
    fig.add_layout_image(
        dict(
            source=generate_gradient_image(),
            xref="x", yref="y",
            x=-1, y=0.2,
            sizex=2, sizey=0.2,
            sizing="stretch",
            opacity=1,
            layer="below"
        )
    )

    # Pointer line
    fig.add_shape(
        type="line",
        x0=score, x1=score,
        y0=0.25, y1=0.35,
        line=dict(color="white", width=4)
    )

    # Axis labels under the bar
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

# 🖼️ Generate gradient image using numpy + PIL
def generate_gradient_image():
    from PIL import Image
    width = 500
    height = 1
    img = Image.new("RGB", (width, height))

    for x in range(width):
        val = x / width  # 0 to 1
        if val <= 0.2:
            color = (214, 39, 40)  # red
        elif val <= 0.4:
            color = (255, 127, 14)  # orange
        elif val <= 0.6:
            color = (255, 221, 87)  # yellow
        elif val <= 0.8:
            color = (44, 160, 44)  # green
        else:
            color = (31, 119, 180)  # blue
        img.putpixel((x, 0), color)

    return img

# 📡 News functions
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
st.markdown("Visual sentiment meter with smooth gradient and live news analysis.")

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
        draw_sentiment_meter(avg_score)

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


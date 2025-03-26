import streamlit as st
import requests
import feedparser
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import streamlit.components.v1 as components
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import fitz  # pymupdf voor PDF extractie
from textblob import TextBlob

st.set_page_config(layout="centered")

# 🎯 Gauge met halve cirkel en kleurverloop
def draw_sentiment_gauge(score):
    fig = go.Figure()
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
        fig.add_shape(type="line", x0=x_start, y0=y_start, x1=x_end, y1=y_end,
                      line=dict(color=color, width=10))

    angle = (1 - (score + 1) / 2) * np.pi
    x_pointer = x0 + 0.35 * np.cos(angle)
    y_pointer = y0 + 0.35 * np.sin(angle)
    fig.add_shape(type="line", x0=x0, y0=y0, x1=x_pointer, y1=y_pointer,
                  line=dict(color="white", width=5))

    fig.add_annotation(x=0.15, y=0.1, text="–", showarrow=False, font=dict(color="white", size=16))
    fig.add_annotation(x=0.85, y=0.1, text="+", showarrow=False, font=dict(color="white", size=16))

    fig.update_layout(xaxis=dict(range=[0, 1], visible=False), yaxis=dict(range=[0, 1], visible=False),
                      plot_bgcolor="black", paper_bgcolor="black", width=500, height=300,
                      margin=dict(l=0, r=0, t=10, b=10))
    st.plotly_chart(fig)

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

def get_newsapi_headlines(query):
    NEWSAPI_KEY = st.secrets["newsapi"]["api_key"]
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

def calculate_rsi(data, period=14):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_sentiment_textblob(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        label = "positive"
    elif polarity < -0.2:
        label = "negative"
    else:
        label = "neutral"
    return label, polarity

# 🎯 UI
st.title("📊 Sentiment Tracker")
st.markdown("Visual sentiment gauge with RSI, news analysis, and PDF annual report sentiment upload.")

# 🎯 Placeholder animatie (zoekbalk)
components.html("""
<script>
  const tickers = ["AAPL", "TSLA", "MSFT", "NVDA", "ASML", "AMZN"];
  let i = 0;
  function typePlaceholder(text, el) {
    let j = 0;
    function typeChar() {
      if (j <= text.length) {
        el.placeholder = text.substring(0, j);
        j++;
        setTimeout(typeChar, 100);
      } else {
        setTimeout(() => erasePlaceholder(el), 2000);
      }
    }
    typeChar();
  }
  function erasePlaceholder(el) {
    let current = el.placeholder;
    let j = current.length;
    function eraseChar() {
      if (j >= 0) {
        el.placeholder = current.substring(0, j);
        j--;
        setTimeout(eraseChar, 50);
      } else {
        i = (i + 1) % tickers.length;
        setTimeout(() => typePlaceholder(tickers[i], el), 200);
      }
    }
    eraseChar();
  }
  const waitForInput = setInterval(() => {
    const input = window.parent.document.querySelector('input[type="text"]');
    if (input) {
      clearInterval(waitForInput);
      typePlaceholder(tickers[i], input);
    }
  }, 100);
</script>
""", height=0)

query = st.text_input("Enter a company name or ticker:", value="")

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

        st.subheader("🧠 RSI + Sentiment Analysis")
        df = yf.download(query, period="1mo", interval="1d")
        df.dropna(inplace=True)

        if not df.empty:
            df["RSI"] = calculate_rsi(df)
            latest_rsi = df["RSI"].dropna().iloc[-1] if not df["RSI"].dropna().empty else None

            if latest_rsi:
                st.write(f"Latest RSI: **{latest_rsi:.2f}**")

                st.subheader("🧩 Market Sentiment Summary")
                if latest_rsi < 30:
                    rsi_status = "oversold"
                elif latest_rsi > 70:
                    rsi_status = "overbought"
                else:
                    rsi_status = "neutral"

                if avg_score < -0.2:
                    sentiment_label = "negative"
                elif avg_score > 0.2:
                    sentiment_label = "positive"
                else:
                    sentiment_label = "neutral"

                st.info(f"📌 Based on recent price movement, the stock is currently **{rsi_status}**. Meanwhile, news sentiment appears to be **{sentiment_label}**. This offers insight into how investors are reacting to this stock.")

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

    st.subheader("📄 Upload Annual Report (PDF)")
    uploaded_file = st.file_uploader("Upload a company's annual report (.pdf)", type=["pdf"])

    if uploaded_file:
        with st.spinner("Analyzing report..."):
            text = extract_text_from_pdf(uploaded_file)
            label, polarity = analyze_sentiment_textblob(text[:5000])  # analyseer eerste stuk
            st.success("✅ Analysis complete!")
            st.markdown(f"**Detected sentiment in report:** `{label.upper()}` ({polarity:.2f})")

            with st.expander("📃 Show report preview"):
                st.write(text[:2000])


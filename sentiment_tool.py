import streamlit as st
import openai
import plotly.graph_objects as go

# 🔐 OpenAI sleutel ophalen uit secrets
openai.api_key = st.secrets["openai"]["api_key"]

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
st.title("📊 Sentiment Tracker")
st.markdown("### 📈 Analyseer automatisch het sentiment van beursnieuws")
st.write("Typ een tickersymbool zoals `AAPL`, `TSLA` of `ASML` om automatisch recente nieuwsberichten te laten analyseren door GPT.")

# 🔍 Inputveld
ticker = st.text_input("🔍 Ticker:", value="AAPL")

if ticker:
    st.markdown("---")
    st.subheader(f"🔎 GPT-analyse voor nieuws over **{ticker.upper()}**")

    # 📰 Dummy headlines
    news = [
        {"title": "Apple beats expectations with strong Q4 results"},
        {"title": "iPhone sales slow down amid economic concerns"},
        {"title": "Apple announces new innovation in MacBooks"},
        {"title": "Tech stocks slide, Apple among biggest losers"},
        {"title": "Investors optimistic about Apple’s future"}
    ]

    sentiments = []

    for artikel in news:
        titel = artikel["title"]

        # GPT-analyse
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een AI-beleggingsassistent. Analyseer het sentiment van dit nieuwsbericht in simpele taal (positief / negatief / neutraal) met korte uitleg. Geef ook een score tussen -1 (negatief) en 1 (positief) aan het einde, gescheiden door '||'."},
                    {"role": "user", "content": f"Nieuwsbericht: {titel}"}
                ]
            )
            full_response = response["choices"][0]["message"]["content"]
            # Splits GPT-output en score
            if "||" in full_response:
                uitleg, score_raw = full_response.split("||")
                uitleg = uitleg.strip()
                score = float(score_raw.strip())
            else:
                uitleg = full_response
                score = 0.0

        except Exception as e:
            uitleg = f"⚠️ GPT-analyse mislukt: {e}"
            score = 0.0

        sentiments.append(score)

        # 💬 Output per artikel
        with st.container():
            st.markdown("#### 📰 Nieuwsbericht")
            st.write(f"*{titel}*")

            st.markdown("#### 🤖 GPT Analyse")
            st.write(uitleg)
            st.markdown("---")

    # 📉 Toon gemiddelde meter
    if sentiments:
        gemiddeld = sum(sentiments) / len(sentiments)
        toon_sentiment_meter(gemiddeld)

# 📘 Footer
st.markdown("---")
st.caption("Gemaakt door Ewout • Powered by OpenAI, Plotly & Streamlit")





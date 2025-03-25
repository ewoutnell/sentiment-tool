import streamlit as st
import openai

# 🔐 Veilige API-key via secrets
openai.api_key = st.secrets["openai"]["api_key"]

# 🧠 Titel & uitleg
st.title("📊 Sentiment Tracker")
st.markdown("### 📈 Analyseer automatisch het sentiment van beursnieuws")
st.write("Typ een tickersymbool zoals `AAPL`, `TSLA` of `ASML` om automatisch recente nieuwsberichten te laten analyseren door GPT.")

# 🔍 Inputveld
ticker = st.text_input("🔍 Ticker:", value="AAPL")

if ticker:
    st.markdown("---")
    st.subheader(f"🔎 GPT-analyse voor nieuws over **{ticker.upper()}**")

    # 📰 Dummy headlines (kan later vervangen worden door live data)
    news = [
        {"title": "Apple beats expectations with strong Q4 results"},
        {"title": "iPhone sales slow down amid economic concerns"},
        {"title": "Apple announces new innovation in MacBooks"},
        {"title": "Tech stocks slide, Apple among biggest losers"},
        {"title": "Investors optimistic about Apple’s future"}
    ]

    for artikel in news:
        titel = artikel["title"]

        # GPT prompt
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een AI-beleggingsassistent. Analyseer het sentiment van het nieuwsbericht in simpele taal (positief / negatief / neutraal) met een korte uitleg."},
                    {"role": "user", "content": f"Nieuwsbericht: {titel}"}
                ]
            )
            antwoord = response["choices"][0]["message"]["content"]
        except Exception as e:
            antwoord = f"⚠️ GPT-analyse mislukt: {e}"

        # 💬 Visuele weergave per artikel
        with st.container():
            st.markdown("#### 📰 Nieuwsbericht")
            st.write(f"*{titel}*")

            st.markdown("#### 🤖 GPT Analyse")
            st.write(antwoord)
            st.markdown("---")

# 📘 Footer
st.markdown("---")
st.caption("Gemaakt door Ewout • Powered by OpenAI & Streamlit")





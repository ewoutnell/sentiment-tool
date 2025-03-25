import streamlit as st
import openai

# 🔐 Veilig ophalen van GPT-key uit Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

st.title("📊 Sentiment Tracker")
st.write("Typ een aandelen-ticker en zie hoe GPT het sentiment van recent nieuws beoordeelt.")

ticker = st.text_input("🔍 Ticker:")

if ticker:
    st.subheader(f"GPT-analyse voor nieuws over {ticker.upper()}")

    # 📰 Dummy nieuws (werkt op Streamlit Cloud)
    news = [
        {"title": "Apple beats expectations with strong Q4 results"},
        {"title": "iPhone sales slow down amid economic concerns"},
        {"title": "Apple announces new innovation in MacBooks"},
        {"title": "Tech stocks slide, Apple among biggest losers"},
        {"title": "Investors optimistic about Apple’s future"}
    ]

    for artikel in news:
        titel = artikel["title"]

        try:
            # 🔮 GPT-analyse
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een AI-beleggingsassistent. Analyseer het sentiment van het onderstaande nieuwsbericht in simpele taal: positief, negatief of neutraal, met korte uitleg."},
                    {"role": "user", "content": f"Nieuwsbericht: {titel}"}
                ]
            )
            antwoord = response["choices"][0]["message"]["content"]

        except Exception as e:
            antwoord = f"⚠️ GPT-analyse mislukt: {e}"

        st.write(f"📰 *{titel}*")
        st.write(f"💬 GPT zegt: {antwoord}")
        st.markdown("---")





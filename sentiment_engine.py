def normalize_rsi(rsi):
    if rsi is None:
        return 0.0
    if rsi < 30:
        return -1.0
    elif rsi > 70:
        return 1.0
    else:
        return 0.0

def classify_sentiment(score):
    if score <= -0.4:
        return "negative"
    elif score >= 0.4:
        return "positive"
    else:
        return "neutral"

def calculate_overall_sentiment(news_score, pdf_score, rsi):
    rsi_score = normalize_rsi(rsi)
    total = (0.4 * news_score) + (0.4 * pdf_score) + (0.2 * rsi_score)
    label = classify_sentiment(total)

    return {
        "total_score": round(total, 2),
        "label": label,
        "components": {
            "news": round(news_score, 2),
            "pdf": round(pdf_score, 2),
            "rsi_score": round(rsi_score, 2)
        }
    }

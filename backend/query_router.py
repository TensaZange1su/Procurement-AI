def classify(text):
    t = text.lower()
    if "аномал" in t:
        return "anomaly"
    if "справедлив" in t or "адекват" in t:
        return "fairness"
    return "analysis"
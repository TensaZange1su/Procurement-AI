import re

def extract_enstru(text):
    match = re.search(r"\b\d{6,}\b", text)
    return match.group(0) if match else None

def extract_year(text):
    match = re.search(r"\b20(2[4-6])\b", text)
    return int(match.group(0)) if match else 2025

def extract_region(text: str):

    if not text:
        return None

    # регион 711310000
    match = re.search(
        r'(?:регион|region|kato)[^\d]*(\d{9})',
        text.lower()
    )

    if match:
        return match.group(1)

    return None
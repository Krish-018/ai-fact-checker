def extract_claim(text: str) -> str:
    """
    Extracts a factual claim from input text.
    Currently treats any non-empty sentence as a claim.
    """

    text = text.strip()

    if not text:
        return "No factual claim detected"

    # If text ends with punctuation, keep it clean
    if text[-1] in ".!?":
        text = text[:-1]

    return text
import random
import os
import time
from .gemini_explainer import explain_with_gemini

# Template explanations as fallback
TEMPLATE_EXPLANATIONS = {
    "true": [
        "✅ Verified TRUE. This matches verified information.",
        "✅ True statement based on scientific consensus.",
        "✅ This claim is accurate according to reliable sources.",
    ],
    "false": [
        "❌ This claim is FALSE. Verified information contradicts it.",
        "❌ False claim. Please verify before sharing.",
        "❌ This misinformation has been debunked by experts.",
    ]
}

def explain_claim(user_claim, matched_claim, label):
    """
    Try Gemini first, fallback to templates if it fails
    Returns explanation and metrics
    """
    
    start_time = time.time()
    
    # Try Gemini if API key exists
    if os.getenv("GEMINI_API_KEY"):
        try:
            result = explain_with_gemini(user_claim, matched_claim, label)
            if not result["explanation"].startswith("⚠️"):  # If no error
                result["metrics"]["total_time_ms"] = round((time.time() - start_time) * 1000, 2)
                return result
        except Exception as e:
            print(f"Gemini failed, using template: {str(e)}")
    
    # Fallback to templates
    label_str = "true" if label is True or str(label).lower() == "true" else "false"
    explanations = TEMPLATE_EXPLANATIONS.get(label_str, [f"Result: {label}"])
    explanation = random.choice(explanations)
    
    total_latency = round((time.time() - start_time) * 1000, 2)
    
    return {
        "explanation": explanation,
        "metrics": {
            "method": "template",
            "total_latency_ms": total_latency,
            "note": "Used template fallback (Gemini unavailable)"
        }
    }
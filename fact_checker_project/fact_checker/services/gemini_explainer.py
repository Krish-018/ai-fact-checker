import os
import requests
import json
import time
from dotenv import load_dotenv
from .scaledown_compressor import compress_prompt

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def explain_with_gemini(user_claim, matched_claim, label):
    """
    Use Gemini API (with ScaleDown compression) to generate explanation
    Returns explanation and metrics
    """
    
    start_time = time.time()
    
    # Create the prompt
    context = f"Fact-checking task. Verified fact: '{matched_claim}' is {label}."
    prompt = f"Explain why the claim '{user_claim}' is {label} in 2-3 simple sentences."
    
    # Step 1: Compress with ScaleDown
    compression_result = compress_prompt(context, prompt)
    compressed_prompt = compression_result["compressed_prompt"]
    compression_metrics = compression_result["metrics"]
    
    # Step 2: Send compressed prompt to Gemini
    full_prompt = f"{context}\n\n{compressed_prompt}"
    
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 200
        }
    }
    
    try:
        print("⏳ Getting AI explanation from Gemini...")
        gemini_start = time.time()
        response = requests.post(url, json=payload, timeout=15)
        gemini_latency = round((time.time() - gemini_start) * 1000, 2)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract text from Gemini response
            candidates = result.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    explanation = parts[0].get('text', 'No explanation generated')
                    
                    total_latency = round((time.time() - start_time) * 1000, 2)
                    
                    return {
                        "explanation": explanation,
                        "metrics": {
                            "compression": compression_metrics,
                            "gemini_latency_ms": gemini_latency,
                            "total_latency_ms": total_latency,
                            "model": "gemini-1.5-flash"
                        }
                    }
        
        return {
            "explanation": f"⚠️ Gemini Error: {response.status_code}",
            "metrics": {
                "compression": compression_metrics,
                "gemini_latency_ms": gemini_latency,
                "error": f"API Error: {response.status_code}"
            }
        }
        
    except Exception as e:
        total_latency = round((time.time() - start_time) * 1000, 2)
        return {
            "explanation": f"⚠️ Error: {str(e)}",
            "metrics": {
                "compression": compression_metrics,
                "total_latency_ms": total_latency,
                "error": str(e)
            }
        }
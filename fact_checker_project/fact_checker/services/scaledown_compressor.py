import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

SCALEDOWN_API_KEY = os.getenv("SCALEDOWN_API_KEY")
SCALEDOWN_URL = "https://api.scaledown.xyz/compress/raw/"

def compress_prompt(context, prompt, compression_rate="auto"):
    """
    Compress a prompt using ScaleDown API and return metrics
    """
    
    headers = {
        'x-api-key': SCALEDOWN_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "context": context,
        "prompt": prompt,
        "scaledown": {
            "rate": compression_rate
        }
    }
    
    # Calculate original tokens (rough estimate - words as tokens)
    original_text = f"{context} {prompt}"
    original_tokens = len(original_text.split())
    
    start_time = time.time()
    
    try:
        print("⏳ Compressing prompt with ScaleDown...")
        response = requests.post(SCALEDOWN_URL, headers=headers, json=payload, timeout=10)
        
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        if response.status_code == 200:
            result = response.json()
            
            # Get compressed prompt
            compressed_prompt = result.get('compressed_prompt', prompt)
            
            # Calculate compressed tokens
            compressed_text = f"{context} {compressed_prompt}"
            compressed_tokens = len(compressed_text.split())
            
            # Calculate savings
            tokens_saved = original_tokens - compressed_tokens
            savings_percentage = (tokens_saved / original_tokens) * 100 if original_tokens > 0 else 0
            
            print(f"📊 COMPRESSION METRICS:")
            print(f"   Original tokens: {original_tokens}")
            print(f"   Compressed tokens: {compressed_tokens}")
            print(f"   Tokens saved: {tokens_saved}")
            print(f"   Savings: {savings_percentage:.1f}%")
            print(f"   Latency: {latency_ms}ms")
            
            return {
                "compressed_prompt": compressed_prompt,
                "metrics": {
                    "original_tokens": original_tokens,
                    "compressed_tokens": compressed_tokens,
                    "tokens_saved": tokens_saved,
                    "savings_percentage": round(savings_percentage, 1),
                    "latency_ms": latency_ms,
                    "compression_rate": compression_rate
                }
            }
        else:
            print(f"⚠️ ScaleDown API error: {response.status_code}")
            return {
                "compressed_prompt": prompt,
                "metrics": {
                    "original_tokens": original_tokens,
                    "compressed_tokens": original_tokens,
                    "tokens_saved": 0,
                    "savings_percentage": 0,
                    "latency_ms": latency_ms,
                    "error": f"API Error: {response.status_code}"
                }
            }
            
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        print(f"⚠️ Compression error: {str(e)}")
        return {
            "compressed_prompt": prompt,
            "metrics": {
                "original_tokens": original_tokens,
                "compressed_tokens": original_tokens,
                "tokens_saved": 0,
                "savings_percentage": 0,
                "latency_ms": latency_ms,
                "error": str(e)
            }
        }
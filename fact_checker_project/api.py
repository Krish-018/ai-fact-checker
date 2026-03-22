from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fact_checker.pipeline.claim_extractor import extract_claim
from fact_checker.pipeline.similarity_search import FactChecker
from fact_checker.services.llm_explainer import explain_claim
import uvicorn
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="AI Fact Checker API",
    description="Verify news claims instantly with AI - Pipeline Optimization Demo",
    version="2.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize fact checker
try:
    logger.info("Loading FactChecker with verified facts...")
    start_time = time.time()
    checker = FactChecker("fact_checker/data/verified_facts.csv")
    load_time = round((time.time() - start_time) * 1000, 2)
    logger.info(f"✅ FactChecker loaded in {load_time}ms")
except Exception as e:
    logger.error(f"❌ Failed to load FactChecker: {str(e)}")
    raise

# Define request/response models
class VerifyRequest(BaseModel):
    text: str

class VerifyResponse(BaseModel):
    extracted_claim: str
    matched_claim: str
    label: str
    similarity_score: float
    explanation: str
    confidence_percentage: float
    metrics: dict = None

@app.get("/")
def root():
    """Root endpoint - API status"""
    return {
        "message": "AI Fact Checker API is running!",
        "version": "2.0.0",
        "endpoints": {
            "GET /": "This info",
            "GET /health": "Health check",
            "GET /facts": "List all facts",
            "GET /stats": "Database statistics",
            "GET /metrics": "Performance metrics",
            "POST /verify": "Verify a claim"
        }
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "all-MiniLM-L6-v2",
        "facts_loaded": checker.index.ntotal,
        "database_size": len(checker.claims)
    }

@app.get("/metrics")
def get_metrics():
    """Get performance metrics"""
    return {
        "embedding_model": "all-MiniLM-L6-v2",
        "embedding_dimension": 384,
        "similarity_metric": "cosine (0-1, higher = better)",
        "default_threshold": 0.6,
        "compression_provider": "ScaleDown API",
        "llm_provider": "Gemini 1.5 Flash",
        "estimated_cost_reduction": "30-50% with compression"
    }

@app.get("/facts")
def list_facts():
    """List all verified facts in database"""
    facts = []
    for i, (claim, label) in enumerate(zip(checker.claims, checker.data["label"])):
        facts.append({
            "id": i,
            "claim": claim,
            "label": str(label)
        })
    
    return {
        "total_facts": len(facts),
        "facts": facts
    }

@app.get("/stats")
def get_stats():
    """Get database statistics"""
    true_count = sum(1 for label in checker.data["label"] if str(label).lower() == "true")
    false_count = sum(1 for label in checker.data["label"] if str(label).lower() == "false")
    
    return {
        "database_size": len(checker.claims),
        "true_facts": true_count,
        "false_facts": false_count,
        "model": "all-MiniLM-L6-v2",
        "similarity_metric": "cosine (0-1, higher = better)",
        "threshold": "0.6 (60%)"
    }

@app.post("/verify", response_model=VerifyResponse)
def verify_claim(request: VerifyRequest):
    """
    Verify a news claim with full metrics
    
    Args:
        request: {"text": "Your claim here"}
    
    Returns:
        Complete verification with performance metrics
    """
    total_start = time.time()
    
    try:
        logger.info(f"Received request: {request.text[:50]}...")
        
        # Step 1: Extract factual claim
        extract_start = time.time()
        claim = extract_claim(request.text)
        extract_time = round((time.time() - extract_start) * 1000, 2)
        
        logger.info(f"Extracted claim: {claim}")
        
        if claim == "No factual claim detected":
            raise HTTPException(
                status_code=400, 
                detail="No factual claim detected in text. Please provide a clear factual statement."
            )
        
        # Step 2: Search for similar fact
        search_result = checker.search(claim, threshold=0.6)
        
        # Step 3: Get AI explanation with metrics
        explanation_result = explain_claim(claim, search_result["claim"], search_result["label"])
        
        # Step 4: Calculate confidence percentage
        confidence_percentage = round(search_result["score"] * 100, 1)
        
        # Step 5: Compile all metrics
        total_time = round((time.time() - total_start) * 1000, 2)
        
        metrics = {
            "total_time_ms": total_time,
            "extraction_time_ms": extract_time,
            "similarity_search": search_result.get("metrics", {}),
            "explanation": explanation_result.get("metrics", {}),
            "token_reduction": explanation_result.get("metrics", {}).get("compression", {}).get("savings_percentage", 0),
            "optimization_summary": {
                "without_optimization_estimate": "Would cost 30-50% more tokens",
                "with_optimization": f"Saved {explanation_result.get('metrics', {}).get('compression', {}).get('savings_percentage', 0)}% tokens"
            }
        }
        
        # Step 6: Handle low confidence matches
        if search_result["label"] == "Unknown":
            return VerifyResponse(
                extracted_claim=claim,
                matched_claim="No closely matching fact found",
                label="Uncertain",
                similarity_score=search_result["score"],
                confidence_percentage=confidence_percentage,
                explanation=search_result.get("note", "No reliable match found"),
                metrics=metrics
            )
        
        # Step 7: Return complete response
        return VerifyResponse(
            extracted_claim=claim,
            matched_claim=search_result["claim"],
            label=search_result["label"],
            similarity_score=search_result["score"],
            confidence_percentage=confidence_percentage,
            explanation=explanation_result["explanation"],
            metrics=metrics
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/verify/batch")
def verify_batch(requests: list[VerifyRequest]):
    """Verify multiple claims at once with batch metrics"""
    batch_start = time.time()
    results = []
    
    for i, req in enumerate(requests):
        try:
            result = verify_claim(req)
            results.append({
                "id": i,
                "input": req.text[:50] + "...",
                "result": {
                    "label": result.label,
                    "confidence": result.confidence_percentage,
                    "matched": result.matched_claim[:50] + "..."
                },
                "success": True
            })
        except Exception as e:
            results.append({
                "id": i,
                "input": req.text[:50] + "...",
                "error": str(e),
                "success": False
            })
    
    batch_time = round((time.time() - batch_start) * 1000, 2)
    
    return {
        "total_requests": len(requests),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "batch_time_ms": batch_time,
        "average_time_per_request": round(batch_time / len(requests), 2) if requests else 0,
        "results": results
    }

# Run with: uvicorn api:app --reload
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 AI FACT CHECKER API v2.0 - PIPELINE OPTIMIZATION")
    print("="*60)
    print("\n📚 Loading fact checker...")
    print(f"✅ Loaded {checker.index.ntotal} verified facts")
    print("\n📊 OPTIMIZATION FEATURES:")
    print("   • Claim extraction (removes fluff)")
    print("   • FAISS vector search (cosine similarity)")
    print("   • ScaleDown compression (30-50% token reduction)")
    print("   • Gemini AI explanations")
    print("   • Full performance metrics tracking")
    print("\n🌐 Server starting at: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("="*60 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
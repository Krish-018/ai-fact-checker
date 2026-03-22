from fact_checker.pipeline.claim_extractor import extract_claim
from fact_checker.pipeline.similarity_search import FactChecker
from fact_checker.services.llm_explainer import explain_claim


def main():
    print("=== AI Fact Checker with Explanation ===\n")

    # Load fact checker
    checker = FactChecker("fact_checker/data/verified_facts.csv")

    # Get user input
    user_input = input("Enter news text:\n")

    # Step 1: Extract factual claim
    claim = extract_claim(user_input)

    print("\nExtracted Claim:")
    print(claim)

    if claim == "No factual claim detected":
        return

    # Step 2: Search for similar verified fact
    result = checker.search(claim)

    print("\n--- Verification Result ---")
    print("Matched Claim:", result["claim"])
    print("Label:", result["label"])
    print("Similarity Score:", round(result["score"], 4))

    # Step 3: Get AI explanation
    print("\n--- AI Explanation ---")
    explanation = explain_claim(
        user_claim=claim,
        matched_claim=result["claim"],
        label=result["label"]
    )
    print(explanation)


if __name__ == "__main__":
    main()
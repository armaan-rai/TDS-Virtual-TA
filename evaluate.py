# evaluate.py
import requests
import json
from typing import Dict, List

API_URL = "http://localhost:8000/api/"  # Replace with your deployed URL

test_cases = [
    {
        "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
        "expected_keywords": ["gpt-3.5-turbo", "OpenAI API", "required"]
    },
    {
        "question": "How do I submit my GA5 assignment?",
        "expected_keywords": ["submit", "portal", "deadline"]
    }
]

def run_tests():
    results = []
    for test in test_cases:
        try:
            response = requests.post(
                API_URL,
                json={"question": test["question"]},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            # Check if answer contains expected keywords
            answer = data.get("answer", "").lower()
            missing_keywords = [
                kw for kw in test["expected_keywords"]
                if kw.lower() not in answer
            ]
            
            results.append({
                "question": test["question"],
                "status": "PASS" if not missing_keywords else "FAIL",
                "missing_keywords": missing_keywords,
                "answer": answer[:200] + "..." if len(answer) > 200 else answer
            })
        
        except Exception as e:
            results.append({
                "question": test["question"],
                "status": "ERROR",
                "error": str(e)
            })
    
    print("\nTest Results:")
    for result in results:
        print(f"\nQuestion: {result['question']}")
        print(f"Status: {result['status']}")
        if result['status'] == "FAIL":
            print(f"Missing keywords: {result['missing_keywords']}")
        elif result['status'] == "ERROR":
            print(f"Error: {result['error']}")
        print(f"Answer: {result.get('answer', 'N/A')}")

if __name__ == "__main__":
    run_tests()
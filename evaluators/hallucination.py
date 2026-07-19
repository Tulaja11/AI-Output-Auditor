import os
import sys
import time
from dotenv import load_dotenv
from google import genai

# Allow importing test_subject.py from the parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_subject import ask_question, SOURCE_DOCUMENT

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def check_hallucination(question: str, answer: str, source_doc: str) -> dict:
    """
    Uses a second LLM call to grade whether the answer is fully 
    supported by the source document (LLM-as-judge technique).
    """
    grading_prompt = f"""
You are a strict fact-checker. Given a source document, a question, and an 
answer, determine if EVERY claim in the answer is directly supported by the 
document.

Respond in EXACTLY this format:
VERDICT: [SUPPORTED / UNSUPPORTED / PARTIAL]
REASONING: [one sentence explaining why]

Document:
{source_doc}

Question: {question}

Answer to check: {answer}
"""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=grading_prompt
    )
    result_text = response.text.strip()

    # Simple parsing of the verdict
    verdict = "UNKNOWN"
    if "VERDICT: SUPPORTED" in result_text:
        verdict = "SUPPORTED"
    elif "VERDICT: UNSUPPORTED" in result_text:
        verdict = "UNSUPPORTED"
    elif "VERDICT: PARTIAL" in result_text:
        verdict = "PARTIAL"

    return {
        "question": question,
        "answer": answer,
        "verdict": verdict,
        "full_grading_response": result_text
    }


# A set of test questions - mix of things clearly answerable from the document,
# and one deliberately tricky one
TEST_CASES = [
    "When was the RBI established?",
    "Where is the RBI headquartered?",
    "What act established the RBI?",
    "Who is the current Prime Minister of India?",  # not in document - tests refusal
    "What committee sets interest rates?",
]

if __name__ == "__main__":
    results = []

    for question in TEST_CASES:
        answer = ask_question(question)
        time.sleep(20)
        result = check_hallucination(question, answer, SOURCE_DOCUMENT)
        results.append(result)

        print(f"\nQ: {result['question']}")
        print(f"A: {result['answer']}")
        print(f"Verdict: {result['verdict']}")

        time.sleep(20)

    # Calculate hallucination rate
    total = len(results)
    unsupported = sum(1 for r in results if r['verdict'] == 'UNSUPPORTED')
    supported = sum(1 for r in results if r['verdict'] == 'SUPPORTED')
    partial = sum(1 for r in results if r['verdict'] == 'PARTIAL')

    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Total test cases: {total}")
    print(f"Supported: {supported}")
    print(f"Unsupported (hallucinated): {unsupported}")
    print(f"Partial: {partial}")
    print(f"Hallucination rate: {(unsupported/total)*100:.1f}%")
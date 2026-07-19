import os
from dotenv import load_dotenv
from google import genai

# Load the API key from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# A sample "source document" the bot will answer questions from (default fallback)
SOURCE_DOCUMENT = """
The Reserve Bank of India (RBI) was established on April 1, 1935, under the 
Reserve Bank of India Act, 1934. It is headquartered in Mumbai. The RBI is 
responsible for regulating the issue of banknotes, maintaining monetary 
stability in India, and operating the country's credit and currency system. 
The current Governor of the RBI is appointed by the Government of India for 
a term, and the institution plays a key role in India's economic policy, 
including setting interest rates through the Monetary Policy Committee.
"""


def ask_question(question: str, document: str = None) -> str:
    """
    Sends a question + source document to Gemini and returns 
    an answer that should be grounded ONLY in the source document.
    If no document is passed, falls back to the default SOURCE_DOCUMENT.
    """
    doc_to_use = document if document else SOURCE_DOCUMENT

    prompt = f"""
You are a helpful assistant. Answer the question using ONLY the information 
in the document below. If the answer is not in the document, say "I don't know 
based on the given document."

Document:
{doc_to_use}

Question: {question}

Answer:
"""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )
    return response.text.strip()


# Quick test - only runs when you execute this file directly
if __name__ == "__main__":
    test_question = "When was the RBI established?"
    answer = ask_question(test_question)
    print(f"Question: {test_question}")
    print(f"Answer: {answer}")
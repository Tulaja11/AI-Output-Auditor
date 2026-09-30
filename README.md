# AI-Output-Auditor

Tests whether an AI system's answers are actually grounded in its source document,
or making things up.

---

## What it does

You give it a source document and a set of test questions. It runs each question 
through the AI, then uses a second LLM as a judge to check if the answer is 
actually supported by the document.

Each answer gets a verdict:
- **Supported** — grounded in the document
- **Unsupported** — contradicts or ignores the document  
- **Partial** — partly correct, partly made up

At the end you get an overall hallucination rate, per-question reasoning, 
and a CSV export.

---

## How it works

Two separate modules. `test_subject.py` is the AI being tested. 
`evaluators/hallucination.py` is the judge. The judge only receives three strings — 
question, answer, document. It doesn't know how the answer was generated, 
so you can swap in any AI system and it still works.

The judge is forced to reply in this exact format:

VERDICT: [SUPPORTED / UNSUPPORTED / PARTIAL]
REASONING: [one sentence]

Parsing is then just a string search instead of messy NLP.

---

## Tech stack

- Python
- Google Gemini API — test subject and judge
- Streamlit — dashboard UI
- Pandas — results table and CSV export

---

## Numbers

| What | Value |
|------|-------|
| Test questions in demo | 5 |
| API calls per question | 2 (answer + judge) |
| LLM temperature | 0 |
| Verdict types | 3 |

---

## Limitations

- 5 questions is enough to demonstrate the tool, not enough to draw conclusions.
- The judge's own accuracy isn't measured — validated manually on the test set.
- Fixed sleep between calls, not exponential backoff.
- Only checks hallucination. Relevance and consistency not covered yet.

---

## What I'd add next

- Exponential backoff instead of fixed sleep
- More evaluator types in the evaluators/ folder
- SQLite to track hallucination rate across runs over time

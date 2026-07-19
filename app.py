import streamlit as st
import sys
import os
import pandas as pd

# Allow importing from evaluators folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_subject import ask_question, SOURCE_DOCUMENT
from evaluators.hallucination import check_hallucination

st.set_page_config(page_title="AI Output Auditor", layout="wide")

st.title("🔍 AI Output Auditor")
st.caption("A reliability testing dashboard for LLM-powered Q&A systems")

st.subheader("Source Document")

pasted_text = st.text_area(
    "Paste your document text here (or leave blank to use the default RBI sample):",
    height=200,
    placeholder="Paste any text document you'd like to test against..."
)

if pasted_text.strip():
    active_document = pasted_text
    st.success("Custom document loaded!")
else:
    active_document = SOURCE_DOCUMENT
    st.info("No text pasted — using the default RBI sample document.")

with st.expander("View the document being tested"):
    st.text(active_document)

st.subheader("Run Hallucination Tests")

default_questions = """When was the RBI established?
Where is the RBI headquartered?
What act established the RBI?
Who is the current Prime Minister of India?
What committee sets interest rates?"""

questions_input = st.text_area(
    "Enter test questions (one per line):",
    value=default_questions,
    height=150
)

if st.button("Run Audit", type="primary"):
    questions = [q.strip() for q in questions_input.split("\n") if q.strip()]

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, question in enumerate(questions):
        status_text.text(f"Testing question {i+1}/{len(questions)}: {question}")

        answer = ask_question(question, active_document)
        
        result = check_hallucination(question, answer, active_document)
        results.append(result)
        

        progress_bar.progress((i + 1) / len(questions))

    status_text.text("Audit complete!")

    # Summary metrics
    total = len(results)
    supported = sum(1 for r in results if r['verdict'] == 'SUPPORTED')
    unsupported = sum(1 for r in results if r['verdict'] == 'UNSUPPORTED')
    partial = sum(1 for r in results if r['verdict'] == 'PARTIAL')

    st.subheader("Results Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tests", total)
    col2.metric("Supported", supported)
    col3.metric("Hallucinated", unsupported)
    col4.metric("Hallucination Rate", f"{(unsupported/total)*100:.1f}%")

    # Detailed results table
    st.subheader("Detailed Results")
    for r in results:
        verdict_color = {"SUPPORTED": "🟢", "UNSUPPORTED": "🔴", "PARTIAL": "🟡", "UNKNOWN": "⚪"}
        icon = verdict_color.get(r['verdict'], "⚪")

        with st.expander(f"{icon} {r['question']} — {r['verdict']}"):
            st.write(f"**Answer:** {r['answer']}")
            st.write(f"**Grading reasoning:** {r['full_grading_response']}")

    # CSV Export
    st.subheader("Export Results")
    df = pd.DataFrame(results)
    csv = df.to_csv(index=False)

    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="audit_results.csv",
        mime="text/csv",
        key="download_csv_button"
    )
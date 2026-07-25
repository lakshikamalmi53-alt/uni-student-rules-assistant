# Horizon Campus - Student Rules & Regulations Assistant

A Streamlit-based AI assistant built to help Horizon Campus students quickly find information from the official Student Handbook using a Multi-Agent RAG setup.

Live Demo: https://uni-student-rules-assistant-mubkwp3qupmez3qqt5okar.streamlit.app/

---

## System Architecture

The application uses an Agentic RAG pattern with two main agents handling query routing and answer synthesis.

```mermaid
graph TD
    A[User Query] --> B[1. Query Router Agent <br/> Model: Llama 3.1 8B via Groq]
    B -->|Greeting| C[Direct Friendly Response]
    B -->|Rules Query| D[2. RAG Synthesizer Agent <br/> Model: Llama 3.3 70B via Groq]
    D --> E[(FAISS Vector Store <br/> HuggingFace Embeddings)]
    E --> D
    D --> F[Final Answer]


## Agentic Design Patterns

1. Router Pattern: The route_query() function checks user intent and splits requests into basic greetings (GREETING) or policy questions (RULES_QUERY) to optimize latency and token costs.
2. Tool-Use Pattern: The RAG Synthesizer agent queries the FAISS vector index dynamically to fetch context from data/STUDENT HANDBOOK.txt.
3. Reflection / Self-Critique Pattern: Strict system prompt rules force the model to verify context before responding, preventing hallucinated answers when information isn't in the handbook.

---

## Model Selection Comparison

| Sub-task | Model Selected | Provider | Justification (Latency, Cost, Reasoning) |
| :--- | :--- | :--- | :--- |
| **Intent Routing** | `llama-3.1-8b-instant` | Groq | **Ultra-low latency (~0.1s)**, extremely cheap/free tier usage, highly efficient for binary classification tasks. |
| **RAG Synthesis** | `llama-3.3-70b-versatile` | Groq | **Superior reasoning quality**, handles complex context synthesis reliably, fast execution speed via Groq LPUs. |

---

## RAG Pipeline Details & Evaluation

* **Corpus:** Horizon Campus Student Handbook (`.txt`)
* **Chunking Strategy:** `RecursiveCharacterTextSplitter` (Chunk Size: 1000, Overlap: 200)
* **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` 
* **Vector Store:** FAISS 

### Retrieval Evaluation 

| # | Test Query | Retrieved Relevant Context? | Result |
|---|---|---|---|
| 1 | What is the minimum attendance requirement? | Yes (Section on examination eligibility) | ✅ Relevant |
| 2 | What is the policy on academic integrity? | Yes (Section on misconduct & penalties) | ✅ Relevant |
| 3 | How can I request a resit exam? | Yes (Section on grading & re-examinations) | ✅ Relevant |
| 4 | What is the campus dress code policy? | Yes (Section on student conduct guidelines) | ✅ Relevant |
| 5 | Can I park my flight in the cafeteria? | No (Correctly states information is not available) | ✅ Passed (No Hallucination) |
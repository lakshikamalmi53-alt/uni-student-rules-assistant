# Horizon Campus - Student Rules & Regulations Assistant

A Streamlit-based AI assistant designed to help Horizon Campus students quickly find information from the official Student Handbook using a Multi-Agent RAG architecture.

Live Demo: [https://uni-student-rules-assistant-mubkwp3qupmez3qqt5okar.streamlit.app/](https://uni-student-rules-assistant-mubkwp3qupmez3qqt5okar.streamlit.app/)

---

## System Architecture

The application uses an Agentic RAG pattern where query routing and answer synthesis are handled by separate specialized agents.

```mermaid
graph TD
    A[User Query] --> B[1. Query Router Agent <br/> Model: Llama 3.1 8B via Groq]
    B -->|Greeting| C[Direct Friendly Response]
    B -->|Rules Query| D[2. RAG Synthesizer Agent <br/> Model: Llama 3.3 70B via Groq]
    D --> E[(FAISS Vector Store <br/> HuggingFace Embeddings)]
    E --> D
    D --> F[Final Answer]
Agentic Design PatternsRouter Pattern: The route_query() function inspects incoming questions and routes them to either a quick response branch (GREETING) or a knowledge lookup branch (RULES_QUERY). This reduces unnecessary context lookups and lowers latency.Tool-Use Pattern: The RAG Synthesizer agent interacts dynamically with the FAISS vector store to retrieve relevant document passages from data/STUDENT HANDBOOK.txt.Reflection / Self-Critique Pattern: System prompt constraints guide the synthesizer agent to verify context before answering, ensuring answers stay accurate and preventing hallucinations when rules are not found.Model Selection ComparisonSub-taskModel SelectedProviderJustification (Latency, Cost, Reasoning)Intent Routingllama-3.1-8b-instantGroqUltra-low latency (~0.1s), extremely cheap/free tier usage, highly efficient for binary classification tasks.RAG Synthesisllama-3.3-70b-versatileGroqSuperior reasoning quality, handles complex context synthesis reliably, fast execution speed via Groq LPUs.RAG Pipeline Details & EvaluationCorpus: Horizon Campus Student Handbook (.txt)Chunking Strategy: RecursiveCharacterTextSplitter (Chunk Size: 1000, Overlap: 200)Embedding Model: sentence-transformers/all-MiniLM-L6-v2Vector Store: FAISSRetrieval Evaluation#Test QueryRetrieved Relevant Context?Result1What is the minimum attendance requirement?Yes (Section on examination eligibility)✅ Relevant2What is the policy on academic integrity?Yes (Section on misconduct & penalties)✅ Relevant3How can I request a resit exam?Yes (Section on grading & re-examinations)✅ Relevant4What is the campus dress code policy?Yes (Section on student conduct guidelines)✅ Relevant5Can I park my flight in the cafeteria?No (Correctly states information is not available)✅ Passed (No Hallucination)Local Setup InstructionsClone Repository:Bashgit clone https://github.com/lakshikamalmi53-alt/uni-student-rules-assistant.git
cd uni-student-rules-assistant
Set up Virtual Environment:Bashpython -m venv venv
# On Windows:
venv\Scripts\activate
Install Dependencies:Bashpip install -r requirements.txt
Environment Variables:Create a .env file in the root folder:Code snippetGROQ_API_KEY=your_groq_api_key_here
Run Application:Bashstreamlit run app.py
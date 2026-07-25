import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# 1. Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Horizon Campus - Rules Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fetch Groq API Key dynamically from Streamlit Secrets or Local .env
groq_key = os.getenv("GROQ_API_KEY")

try:
    if "GROQ_API_KEY" in st.secrets:
        groq_key = st.secrets["GROQ_API_KEY"]
except Exception:
    # Fallback to .env when running locally without a secrets.toml file
    pass

if not groq_key:
    st.error("GROQ_API_KEY not found! Please configure it in Streamlit Cloud Secrets or your local .env file.")
    st.stop()

# Custom Styling
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 700; text-align: center; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1rem; color: #4B5563; text-align: center; margin-bottom: 2rem; }
    .agent-badge { background-color: #EFF6FF; color: #1D4ED8; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/graduation-cap.png", width=80)
    st.title("🎓 Assistant Panel")
    st.markdown("---")
    st.markdown("**Agentic Architecture Info:**")
    st.info("""
    - **Router Agent:** Llama-3.1-8b-instant (Groq)
    - **RAG Synthesizer Agent:** Llama-3.3-70b-versatile (Groq)
    - **Vector Store:** FAISS (HuggingFace)
    - **Design Patterns:** Router, Tool-Use, Reflection
    """)
    st.markdown("---")
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Header
st.markdown("<div class='main-header'>🎓 Horizon Campus Student Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Multi-Agent AI System for Horizon Campus Student Handbook & Regulations</div>", unsafe_allow_html=True)

# 2. Vector Store Setup
@st.cache_resource
def prepare_vector_store():
    data_path = "./data"
    if not os.path.exists(data_path) or not os.listdir(data_path):
        st.error("Data folder empty! Place STUDENT HANDBOOK.txt inside `./data`.")
        st.stop()
    
    loader = DirectoryLoader(data_path, glob="*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(final_documents, embeddings)

try:
    vectorstore = prepare_vector_store()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
except Exception as e:
    st.error(f"Error initializing knowledge base: {e}")
    st.stop()

# 3. Model Initialization (Multi-Model Strategy)
# Model 1: Fast & Cheap for Intent Routing
router_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0, groq_api_key=groq_key)

# Model 2: Deep Reasoning for RAG Synthesis
synthesis_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, groq_api_key=groq_key)

# Agent 1: Router Logic
def route_query(user_query):
    router_prompt = (
        "You are an Intent Classification Agent. Classify the user query into either 'GREETING' or 'RULES_QUERY'.\n"
        "Reply with ONLY one word: 'GREETING' if it is a general hello/greeting/thanks, "
        "or 'RULES_QUERY' if it is asking about university regulations, exams, attendance, dress code, etc.\n\n"
        f"Query: {user_query}"
    )
    response = router_llm.invoke(router_prompt)
    intent = response.content.strip().upper()
    return "GREETING" if "GREETING" in intent else "RULES_QUERY"

# Agent 2: RAG Pipeline Logic
system_prompt = (
    "You are an official Horizon Campus Student Handbook Assistant.\n"
    "Use the retrieved context to answer the student's question concisely.\n"
    "Perform a self-check: If the answer is not in the context, explicitly say you don't know based on the handbook.\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

question_answer_chain = create_stuff_documents_chain(synthesis_llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# 4. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# User Input Handling with Agent Workflow
if user_input := st.chat_input("Ask a question about Horizon Campus rules..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        # Step A: Intent Routing (Agent 1)
        with st.status("Agent Workflow Active...", expanded=True) as status:
            st.write("**Router Agent (Llama 3.1 8B):** Classifying user intent...")
            intent = route_query(user_input)
            
            if intent == "GREETING":
                st.write(" Intent: **Greeting**. Generating response...")
                answer = synthesis_llm.invoke(f"Respond politely as Horizon Campus Assistant to: {user_input}").content
                status.update(label="✅ Intent: Greeting processed!", state="complete")
            else:
                st.write("Intent: **Rules Query**. Activating RAG Synthesizer Agent (Llama 3.3 70B)...")
                st.write("Retrieving relevant chunks from Student Handbook FAISS Index...")
                response = rag_chain.invoke({"input": user_input})
                answer = response["answer"]
                status.update(label="✅ Intent: Handbook Search complete!", state="complete")

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
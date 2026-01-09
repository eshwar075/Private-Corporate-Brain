# --- 1. CLOUD DATABASE FIX ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# -----------------------------

import streamlit as st
import os
import tempfile

# --- 2. LIBRARIES ---
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- NEW SAFE IMPORTS (The Fix) ---
# We point to the specific sub-folders to avoid errors
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
# ----------------------------------

from langchain_core.prompts import ChatPromptTemplate

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="Private Brain", page_icon="🧠")
st.title("🧠 Private Corporate Brain")

# --- 4. THE BRAIN LOGIC ---
class RAGEngine:
    def __init__(self, api_key):
        self.llm = ChatGroq(groq_api_key=api_key, model_name="llama3-8b-8192")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.chain = None

    def process_document(self, pdf_path):
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        self.vector_store = Chroma.from_documents(documents=splits, embedding=self.embeddings)
        self._create_chain()
        return "✅ Document Processed Successfully!"

    def _create_chain(self):
        retriever = self.vector_store.as_retriever()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer strictly based on the context. If unknown, say 'I do not know'. Context: {context}"),
            ("human", "{input}"),
        ])
        chain = create_stuff_documents_chain(self.llm, prompt)
        self.chain = create_retrieval_chain(retriever, chain)

    def ask(self, query):
        if not self.chain: return "⚠️ Please upload a file first."
        return self.chain.invoke({"input": query})["answer"]

# --- 5. FRONTEND UI ---
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None

st.sidebar.header("Setup")
api_key = st.sidebar.text_input("Groq API Key", type="password")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type="pdf")
btn = st.sidebar.button("Analyze")

if btn:
    if not api_key or not uploaded_file:
        st.sidebar.error("⚠️ Missing Key or File")
    else:
        st.session_state.rag_engine = RAGEngine(api_key)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            path = tmp.name
        
        with st.spinner("Processing..."):
            status = st.session_state.rag_engine.process_document(path)
            st.sidebar.success(status)
            os.remove(path)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ready."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input("Ask question...")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    response = "⚠️ Please Analyze PDF first."
    if st.session_state.rag_engine:
        with st.spinner("Thinking..."):
            response = st.session_state.rag_engine.ask(prompt)
    
    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

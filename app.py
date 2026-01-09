# --- 1. CLOUD DATABASE FIX ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# -----------------------------

import streamlit as st
import os
import tempfile
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.docstore.document import Document

st.set_page_config(page_title="Private Brain", page_icon="🧠")
st.title("🧠 Private Corporate Brain")

# --- LOGIC CLASS ---
class RAGEngine:
    def __init__(self, api_key):
        clean_key = api_key.strip()
        self.llm = ChatGroq(groq_api_key=clean_key, model_name="llama-3.1-8b-instant")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.chain = None

    def process_text(self, text):
        docs = [Document(page_content=text)]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        self.vector_store = Chroma.from_documents(documents=splits, embedding=self.embeddings)
        self._create_chain()
        return "✅ Text Processed Successfully!"

    def process_document(self, pdf_path):
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        self.vector_store = Chroma.from_documents(documents=splits, embedding=self.embeddings)
        self._create_chain()
        return "✅ PDF Processed Successfully!"

    def _create_chain(self):
        retriever = self.vector_store.as_retriever()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer strictly based on the context. If unknown, say 'I do not know'. Context: {context}"),
            ("human", "{input}"),
        ])
        chain = create_stuff_documents_chain(self.llm, prompt)
        self.chain = create_retrieval_chain(retriever, chain)

    def ask(self, query):
        if not self.chain: return "⚠️ Please upload data first."
        return self.chain.invoke({"input": query})["answer"]

# --- FRONTEND UI ---
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None

st.sidebar.header("Setup")

# --- AUTO-LOGIN LOGIC ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
    st.sidebar.success("✅ API Key Loaded from Cloud Secrets")
else:
    api_key = st.sidebar.text_input("Groq API Key", type="password")
# ------------------------

input_method = st.sidebar.radio("Choose Input Method:", ["📂 Upload PDF", "📝 Paste Text (Backup)"])

if input_method == "📂 Upload PDF":
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type="pdf")
    if st.sidebar.button("Analyze PDF"):
        if not api_key:
            st.sidebar.error("Missing API Key")
        elif not uploaded_file:
            st.sidebar.error("Missing File")
        else:
            st.session_state.rag_engine = RAGEngine(api_key)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                path = tmp.name
            with st.spinner("Processing PDF..."):
                status = st.session_state.rag_engine.process_document(path)
                st.sidebar.success(status)
                os.remove(path)

elif input_method == "📝 Paste Text (Backup)":
    user_text = st.sidebar.text_area("Paste content here:")
    if st.sidebar.button("Analyze Text"):
        if not api_key:
            st.sidebar.error("Missing API Key")
        elif not user_text:
            st.sidebar.error("Missing Text")
        else:
            with st.spinner("Processing Text..."):
                st.session_state.rag_engine = RAGEngine(api_key)
                status = st.session_state.rag_engine.process_text(user_text)
                st.sidebar.success(status)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ready."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input("Ask question...")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    response = "⚠️ Please Analyze data first."
    if st.session_state.rag_engine:
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.rag_engine.ask(prompt)
            except Exception as e:
                response = f"⚠️ Error: {str(e)}"
    
    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

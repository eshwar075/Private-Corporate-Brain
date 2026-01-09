# --- 1. CLOUD COMPATIBILITY FIX (MUST BE AT THE VERY TOP) ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ------------------------------------------------------------

import streamlit as st
import tempfile
import os
from rag_engine import RAGEngine

# 2. Page Config
st.set_page_config(page_title="Private Brain", page_icon="🧠")
st.title("🧠 Private Corporate Brain")

# 3. Session State
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None

# 4. Sidebar
st.sidebar.header("Setup")
api_key = st.sidebar.text_input("Groq API Key", type="password")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type="pdf")
btn = st.sidebar.button("Analyze")

# 5. Logic
if btn:
    if not api_key:
        st.sidebar.error("⚠️ Missing API Key")
    elif not uploaded_file:
        st.sidebar.error("⚠️ Missing File")
    else:
        # Initialize Engine
        st.session_state.rag_engine = RAGEngine(api_key)
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            path = tmp.name
        
        # Process
        with st.spinner("Processing..."):
            status = st.session_state.rag_engine.process_document(path)
            st.sidebar.success(status)
            os.remove(path)

# 6. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ready. Upload PDF to start."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input("Ask a question...")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    response = "⚠️ Please Analyze PDF first."
    if st.session_state.rag_engine:
        with st.spinner("Thinking..."):
            response = st.session_state.rag_engine.ask(prompt)
    
    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

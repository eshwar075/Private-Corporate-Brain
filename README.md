# 🧠 Private Corporate Brain
### A Secure, Cloud-Native Retrieval-Augmented Generation (RAG) Application

<!-- LIVE APP BADGE -->
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://app-corporate-brain.streamlit.app/)

![Status](https://img.shields.io/badge/Status-Deployed-success)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Cloud](https://img.shields.io/badge/Cloud-Groq%20API-orange)

---

## 👥 Project Team & Roles
**Department:** BCA Data Science & AI  
**Subject:** Cloud Application Development (2025-2026)

This project was developed using a microservices-style collaboration, with specific technical responsibilities assigned to each member:

| Member Name | Role | Key Technical Responsibilities |
| :--- | :--- | :--- |
| **Vishwa** | **Frontend Engineer** (UI/UX) | Designed the **Streamlit Web Interface**, implemented user session management, and created the "Paste Text" fallback module for mobile compatibility. |
| **Gowtham** | **DevOps & QA Engineer** | Managed **GitHub Version Control**, set up the CI/CD pipeline for **Streamlit Cloud deployment**, and performed cross-device testing. |
| **Chandru** | **Cloud Architect** (AI) | Managed the **Groq Cloud API** interconnection, optimized the **Llama 3** inference model, and implemented API security protocols. |
| **Eshwar** | **Data Engineer** (ETL) | Built the data ingestion pipeline, implemented **Recursive Text Chunking**, and managed **Vector Embeddings** using ChromaDB. |

---

## 📖 Project Abstract
In the modern enterprise, using public AI tools (like ChatGPT) for internal documents poses severe **Data Privacy** risks and compliance violations. Furthermore, generic models suffer from **hallucinations** (inventing facts) when they lack specific internal knowledge.

**"Private Corporate Brain"** is a Hybrid Cloud application that solves this by implementing **RAG (Retrieval-Augmented Generation)**. It allows users to chat with their private documents securely. The system processes data locally for privacy while leveraging high-speed Cloud LPUs for inference, ensuring accurate, cited answers without data leakage.

---

## ⚙️ Technology Stack

*   **Frontend:** Streamlit (Web Framework)
*   **Language:** Python 3.10+
*   **Orchestration:** LangChain
*   **Database:** ChromaDB (Vector Store)
*   **AI Model:** Meta Llama 3 (via Groq Cloud)
*   **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)

---

## 🚀 How to Run the Project

The application is deployed live on Streamlit Cloud.

### [Click Here to Launch App 🚀](https://app-corporate-brain.streamlit.app/)

**User Guide:**
1.  **Configure:** Open the Sidebar (Left Menu).
2.  **API Key:** Enter your Groq API Key.
3.  **Input Method:** 
    *   **Option A (Desktop):** Upload a PDF document.
    *   **Option B (Mobile/Low Bandwidth):** Select **"Paste Text"** to bypass network restrictions.
4.  **Analyze:** Click the Analyze button.
5.  **Chat:** Ask any question related to the document.

---

## 🧠 System Architecture Diagram

```mermaid
graph LR
    A[User Input] --> B{Input Router}
    B -- PDF Upload --> C(PyPDF Loader)
    B -- Paste Text --> D(Direct String)
    C --> E[Recursive Chunking]
    D --> E
    E --> F[Vector Embeddings]
    F --> G[(ChromaDB)]
    H[User Question] --> G
    G --> I[Retrieved Context]
    I --> J[Groq Cloud API]
    J --> K[Llama 3 Response]
    K --> L[Streamlit UI]

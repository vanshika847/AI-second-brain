# 🧠 AI Second Brain

> Chat with your documents using RAG. Free, fast, and privacy-first.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# SET ENVIRONMENT
python -m venv venv

venv\Scripts\activate.bat

streamlit run app.py

**AI Second Brain** Stop searching through PDFs manually. Your personal knowledge base powered by RAG. Upload documents, ask questions, get instant answers with source citations. 100% free with Groq API. Privacy-first with local embeddings. 

Transforms your document collection into an interactive knowledge base. Upload PDFs, DOCX, PPTX, TXT, or MD files and ask questions in natural language. Get instant, source-backed answers with page citations and confidence scores.

---

## ✨ Features

- **💬 Natural Language Q&A** - Ask questions, get cited answers from your documents
- **🎤 Voice Input** - Hands-free querying with speech-to-text (Chrome/Edge)
- **📊 Document Comparison** - Compare multiple documents side-by-side
- **💡 Smart Suggestions** - AI-generated question suggestions based on your content
- **🔗 Source Attribution** - Every answer includes filename, page number, and relevance score
- **💭 Conversation Memory** - Contextual follow-up questions with chat history
- **🆓 100% FREE** - Uses Groq API (free tier) or local Ollama
- **🔒 Privacy-First** - Local embeddings, your data stays yours


# Architecture
Upload Document → Parse & Clean → Chunk Text → Generate Embeddings
                                                      ↓
User Question → Embed Query → Search Vector DB → Retrieve Top 5 Chunks
                                                      ↓
                              Build Context → Send to Groq LLM → Generate Answer
                                                      ↓
                              Display Answer + Sources + Page Numbers


# Tech Stack:
LlamaIndex - RAG framework
ChromaDB - Vector database (persistent)
FastEmbed - Local embeddings (BGE-small-en)
Groq API - LLM inference (Llama 3.1 8B)
Streamlit - Web UI


# 💰 Cost Analysis
- **With Groq (Default)
- **Cost: $0 (free tier)
- **Limits: 30 requests/min, 14,400 requests/day
- **Sufficient for: Personal use, small teams

# Acknowledgments
- **LlamaIndex - RAG framework
- **Groq - Free LLM API
- **ChromaDB - Vector database
- **Streamlit - UI framework
- **FastEmbed - Local embeddings
---

## 🎯 Use Cases

### 👨‍🎓 For Students

**Scenario:** You're reviewing contracts, proposals, and meeting notes

**How AI Second Brain Helps:**
You: "What's the deadline in Project X proposal?" AI: "The deadline is March 15, 2024, with Phase 1 due by Feb 1. [Source: ProjectX_Proposal_v2.docx, Page 3, 94% relevance]"

You: "Compare the pricing in both vendor proposals" AI: "Vendor A: $50,000 (includes maintenance) Vendor B: $45,000 (maintenance extra $5,000/year)

 Key Differences:
 - Vendor A offers 24/7 support
 - Vendor B has faster delivery (2 weeks vs 4 weeks)"

**Features You'll Love:**
- ⚡ Quick contract review
- 📊 Compare proposals side-by-side
- 🎤 Voice input during meetings
- 🔒 Secure local storage for sensitive docs

---

### 👨‍⚖️ For Legal Professionals

**Scenario:** Analyzing case files, precedents, and legal documents

**How AI Second Brain Helps:**
You: "Find all mentions of liability clauses in the contract" AI: "Found 3 liability clauses: 1. Section 8.2 - Limited liability to $100,000 2. Section 12.4 - Indemnification clause 3. Appendix C - Insurance requirements [Sources with exact page numbers and sections]"

You: "How does this contract compare to the template we used last year?" AI: "Differences: - Payment terms: Net 30 (this) vs Net 45 (template) - Termination notice: 60 days (this) vs 90 days (template) - Jurisdiction: Delaware (this) vs New York (template)"


**Features You'll Love:**
- 🔍 Find specific clauses instantly
- 📊 Compare contracts and precedents
- 📄 Source citations with page numbers
- 🔒 Privacy-first (no data leaves your machine with Ollama)

---
### 🏫 For Teachers & Educators
Managing curriculum, lesson plans, student materials

### 🏠 For Personal Knowledge Management
Managing recipes, travel plans, notes, articles

# FUTURE ENHANCEMENTS
Export Chat History
Smart Summarization
Advanced Search Filters
Multi-User Workspace
Cloud Integration
Flashcard Generator
Knowledge Graph

# ⭐ Star History
If you find this project helpful, please consider giving it a star! ⭐

# Built with ❤️ by vanshika

Transform your documents into an AI-powered knowledge base in minutes.
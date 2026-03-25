# 🤖 AI Chat Assistant (Streamlit + LangChain + Ollama)

A clean, fast, and local AI chatbot built using **Streamlit**, **LangChain**, and **Ollama**.
Supports conversation history, token tracking, and a responsive chat UI.

---

## 🚀 Features

* 💬 Chat-based interface (like ChatGPT)
* 🧠 Context-aware responses using conversation history
* ⚡ Runs **locally** using Ollama (no API cost)
* 📊 Token usage tracking (input / output / total)
* 🧹 Clear chat & reset tokens
* ⏳ Smooth UX with loading spinner
* 🧩 Modular architecture (easy to extend)

---

## 🛠️ Tech Stack

* **Frontend**: Streamlit
* **LLM Orchestration**: LangChain
* **Model**: Ollama (`gemma3:1b`)
* **Language**: Python

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-chat-assistant.git
cd ai-chat-assistant
```

---

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install & run Ollama

Download Ollama from: https://ollama.com

Then pull the model:

```bash
ollama pull gemma3:1b
```

---

### 5. Run the app

```bash
streamlit run main.py
```

---

## 🧠 How It Works

* Uses **LangChain prompt templates** with:

  * system message
  * chat history
  * user input
* Maintains conversation via `st.session_state`
* Uses `st.cache_resource` to load model once
* Extracts token usage from `usage_metadata`
* Falls back to manual token estimation when needed

---

## 📊 Token Tracking

The app tracks:

* Input tokens
* Output tokens
* Total tokens

If the model doesn't return usage metadata, it estimates tokens using word count.

---

## 📁 Project Structure

```
.
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚠️ Notes

* Designed for **local inference** using Ollama
* Token counts are approximate if metadata is unavailable
* Best used with Python **3.10–3.12** (LangChain compatibility)

---

## 🔮 Future Improvements

* 🔴 Streaming responses (token-by-token output) (done)
* 🧠 Memory summarization (long chat handling) (donw)
* 📂 Save/load conversations (done)
* 🎯 Prompt customization UI
* 🌐 Deployment (Streamlit Cloud / Docker)

---

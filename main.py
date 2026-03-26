import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
import time

from utils import (
    calculate_tokens,
    format_history_for_llm,
    build_footer,
    trim_history,
    save_session,
    load_session,
)

# ------------------ Page Config ------------------
st.set_page_config(page_title="AI Chat", page_icon="🤖", layout="wide")

# ------------------ Session State ------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "tokens" not in st.session_state:
    st.session_state.tokens = {"total": 0, "input": 0, "output": 0}

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful AI assistant"

# ------------------ Sidebar ------------------
with st.sidebar:
    st.title("⚙️ Controls")
    # --- System prompt editor ---
    st.markdown("### 🧠 System Prompt")

    system_prompt = st.text_area(
        "Define AI behavior",
        value=st.session_state.system_prompt,
        height=120,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Apply prompt"):
            st.session_state.system_prompt = system_prompt
    with col2:
        if st.button("Reset Prompt"):
            st.session_state.system_prompt = "You are a helpful AI assistant."
            st.rerun()

    st.divider()

    # --- Chat Controls ---
    st.markdown("### 💬 Chat")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧹 Clear history", use_container_width=True):
            st.session_state.history = []

    with col2:
        if st.button("🔄 Reset Tokens", use_container_width=True):
            st.session_state.tokens = {"total": 0, "input": 0, "output": 0}

    st.divider()

    # --- Session Controls ---
    st.markdown("### 💾 Session")

    st.download_button(
        label="⬇️ Download",
        data=save_session(st.session_state.history, st.session_state.tokens),
        file_name="session_data.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_file = st.file_uploader(
        "📤 Upload", type=["json"], label_visibility="collapsed"
    )

    if st.button("Load Session", use_container_width=True):
        if uploaded_file is None:
            st.warning("Upload a file first")
        else:
            st.session_state.history, st.session_state.tokens = load_session(
                uploaded_file
            )
            st.success("Loaded")

    st.divider()

    # --- Token Usage ---
    st.markdown("### 📊 Token Usage")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", st.session_state.tokens["total"])
    col2.metric("Input", st.session_state.tokens["input"])
    col3.metric("Output", st.session_state.tokens["output"])


# ------------------ Model ------------------
@st.cache_resource
def load_model():
    prompt_template = ChatPromptTemplate(
        [
            ("system", "{system_prompt}"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    llm = ChatOllama(model="gemma3:1b")  # type:ignore
    print("using ollama model: gemma3:1b")
    return prompt_template | llm


llm_chain = load_model()


# ------------------ LLM Call ------------------
def call_llm_stream(text: str) -> tuple[str, float, int]:
    print("-----Calling LLM-----")
    start_time = time.time()

    full_response = ""
    usage = {}

    with st.chat_message("ai"):
        placeholder = st.empty()
        # trimming history if it becomes too large
        trimmed_history = trim_history(st.session_state.history)

        for chunk in llm_chain.stream(
            {
                "system_prompt": st.session_state.system_prompt,
                "input": text,
                "history": format_history_for_llm(trimmed_history),
            }
        ):
            if chunk.content:
                full_response += chunk.content  # type:ignore
                placeholder.markdown(full_response + "▌")

            usage_meta = chunk.response_metadata.get("usage_metadata")

            if usage_meta:
                usage = usage_meta

        # ---- metrics ----
        end_time = time.time()
        latency = round(end_time - start_time, 2)

        input_tokens = usage.get("input_tokens") or calculate_tokens(text)
        output_tokens = usage.get("output_tokens") or calculate_tokens(full_response)
        total_tokens = usage.get("total_tokens") or (input_tokens + output_tokens)

        # update state
        st.session_state.tokens["input"] += input_tokens
        st.session_state.tokens["output"] += output_tokens
        st.session_state.tokens["total"] += total_tokens

        # ---- final render (text + footer) ----
        footer = build_footer(latency=latency, total_tokens=total_tokens)

        placeholder.markdown(f"{full_response}\n\n{footer}", unsafe_allow_html=True)

    return full_response, latency, total_tokens


# ------------------ Header ------------------
st.title("💬 AI Chat Assistant")
st.caption("Fast • Local • Streamlit + LangChain + Ollama")

# ------------------ Show History ------------------
with st.container():
    for message in st.session_state.history:
        with st.chat_message(message.get("role", "human")):
            content = message.get("content", "")
            st.markdown(content)

            # only for AI messages
            if message.get("role") == "ai":
                footer = build_footer(
                    latency=message.get("latency", 0),
                    total_tokens=message.get("total_tokens", 0),
                )
                st.markdown(footer, unsafe_allow_html=True)

# ------------------ Input ------------------
prompt = st.chat_input("Type your message...")
if prompt:
    # User message
    with st.chat_message("human"):
        st.markdown(prompt)

    st.session_state.history.append({"role": "human", "content": prompt})

    # stream llm
    try:
        response, latency, tokens_used = call_llm_stream(prompt)
        st.session_state.history.append(
            {
                "role": "ai",
                "content": response,
                "latency": latency,
                "total_tokens": tokens_used,
            }
        )
    except Exception as e:
        print(f"Got Error:\n{e}")
    finally:
        st.rerun()

import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

# ------------------ Page Config ------------------
st.set_page_config(page_title="AI Chat", page_icon="🤖", layout="wide")

# ------------------ Session State ------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "tokens" not in st.session_state:
    st.session_state.tokens = {"total": 0, "input": 0, "output": 0}

# ------------------ Sidebar ------------------
with st.sidebar:
    st.title("⚙️ Controls")

    if st.button("🧹 Clear Chat"):
        st.session_state.history = []

    if st.button("🔄 Reset Tokens"):
        st.session_state.tokens = {"total": 0, "input": 0, "output": 0}

    st.divider()

    st.subheader("📊 Token Usage")
    st.metric("Total", st.session_state.tokens["total"])
    st.metric("Input", st.session_state.tokens["input"])
    st.metric("Output", st.session_state.tokens["output"])


# ------------------ Model ------------------
@st.cache_resource
def load_model():
    prompt_template = ChatPromptTemplate(
        [
            ("system", "You are a helpful AI assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    llm = ChatOllama(model="gemma3:1b", num_gpu=0)

    return prompt_template | llm


llm_chain = load_model()
parser = StrOutputParser()


# ------------------ Token Estimation ------------------
def calculate_tokens(text: str):
    return len(text.split())


# ------------------ LLM Call ------------------
def call_llm(text):
    response_raw = llm_chain.invoke(
        {"input": text, "history": st.session_state.history}
    )

    usage = getattr(response_raw, "usage_metadata", {}) or {}

    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    total_tokens = usage.get("total_tokens")

    # fallback if missing
    if input_tokens is None:
        input_tokens = calculate_tokens(text)

    if output_tokens is None:
        output_tokens = calculate_tokens(response_raw.content)  # type:ignore

    if total_tokens is None:
        total_tokens = input_tokens + output_tokens

    # update state
    st.session_state.tokens["input"] += input_tokens
    st.session_state.tokens["output"] += output_tokens
    st.session_state.tokens["total"] += total_tokens

    return parser.invoke(response_raw)


# ------------------ Header ------------------
st.title("💬 AI Chat Assistant")
st.caption("Fast • Local • Streamlit + LangChain + Ollama")

# ------------------ Chat History ------------------
chat_container = st.container()

with chat_container:
    for message in st.session_state.history:
        with st.chat_message(message.type):
            st.markdown(message.content)

# ------------------ Input ------------------
if prompt := st.chat_input("Type your message..."):
    # User message
    with st.chat_message("human"):
        st.markdown(prompt)

    st.session_state.history.append(HumanMessage(content=prompt))

    # AI response (with spinner)
    with st.chat_message("ai"):
        placeholder = st.empty()
        with st.spinner("Thinking..."):
            response = call_llm(prompt)
            placeholder.markdown(response)

    st.session_state.history.append(AIMessage(content=response))

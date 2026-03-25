from langchain_core.messages import HumanMessage, AIMessage
import json


# ------------------ Token Estimation ------------------
def calculate_tokens(text: str) -> int:
    return len(text.split())


# ------------------ Format history for LLM ------------------
def format_history_for_llm(history: list[dict]) -> list[dict]:
    formatted_history = []
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "human":
            formatted_history.append(HumanMessage(content=content))
        elif role == "ai":
            formatted_history.append(AIMessage(content=content))

    return formatted_history


# ------------------ build footer to print tokens ------------------
def build_footer(latency: float, total_tokens: int) -> str:
    return f"""
<sub>
⏱ {latency}s | 🔤 {total_tokens} tokens | 💰 ${calculate_cost(total_tokens):.5f}
</sub>
"""


# ------------------ calculate cost ------------------
def calculate_cost(total_tokens: int, price_per_1k: float = 0.002) -> float:
    """
    total_tokens: int
    price_per_1k: cost per 1000 tokens
    """

    return round((total_tokens / 1000) * price_per_1k, 6)


# ------------------ trim_hstory ------------------
def trim_history(history: list[dict]) -> list[dict]:
    return history[-16:]


# ------------------ save_session ------------------
def save_session(history: list[dict], tokens: dict) -> str:
    print("save session called")

    return json.dumps(
        {"history": history, "tokens_used": tokens}, indent=2, ensure_ascii=False
    )


# ------------------ load_session ------------------
def load_session(uploaded_file) -> tuple[list[dict], dict]:
    print("load_session called")
    data = json.load(uploaded_file)
    history = data.get("history", [])
    tokens = data.get("tokens_used", {"total": 0, "input": 0, "output": 0})
    return (history, tokens)

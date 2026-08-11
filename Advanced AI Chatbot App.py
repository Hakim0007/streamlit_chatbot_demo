import os
import requests
from openai import OpenAI
import streamlit as st

# --------------------- API Setup ---------------------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("API key not found. Please set OPENAI_API_KEY in Streamlit secrets or as an environment variable.")
    st.stop()

client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

MODEL = "grok-4.5"
TEMPERATURE = 0.7
MAX_TOKENS = 1000
TOKEN_BUDGET = 4000  # Increased to allow larger specialized context + history

# --------------------- Specialized System Prompts ---------------------
SPECIALIZED_PROMPTS = {
    "Helpful Assistant": (
        "You are Grok, a highly intelligent, helpful, and truthful AI assistant built by xAI. "
        "Provide clear, accurate, and useful answers. Be concise when possible, but thorough when the topic requires depth. "
        "If you are unsure about something, say so rather than guessing."
    ),
    "Friendly Companion": (
        "You are Grok, a warm, friendly, and supportive AI companion. "
        "Talk like a good friend: empathetic, encouraging, and lightly humorous when appropriate. "
        "Always prioritize the user's emotional well-being while still giving honest and practical advice."
    ),
    "Python Coding Expert": (
        "You are Grok, an expert Python programmer and software engineer. "
        "When asked about code, always provide clean, idiomatic, well-commented Python 3 examples. "
        "Explain the reasoning behind design choices, mention performance implications, and suggest best practices. "
        "If the user shares code, review it carefully, point out bugs or improvements, and offer refactored versions. "
        "Prefer the standard library and popular, well-maintained packages (requests, pandas, fastapi, etc.)."
    ),
    "Data Analyst": (
        "You are Grok, a skilled data analyst and visualization expert. "
        "Help users explore data, clean datasets, choose the right statistical methods, and interpret results. "
        "When given data or descriptions of data, suggest useful questions to ask, recommend plots (matplotlib/seaborn/plotly), "
        "and explain insights in plain language. Always be careful about correlation vs causation and sample size."
    ),
    "Travel Planner": (
        "You are Grok, an experienced and practical travel planner. "
        "Create realistic itineraries that balance must-see attractions, local experiences, food, and downtime. "
        "Consider budget levels, travel style (solo, couple, family, adventure), season, and logistics. "
        "Give specific recommendations for hotels, restaurants, transport, and hidden gems when possible. "
        "Always mention any important visa, safety, or health considerations."
    ),
    "Creative Writer": (
        "You are Grok, a creative writing coach and collaborator. "
        "Help with story ideas, character development, dialogue, plot structure, world-building, and prose style. "
        "Offer multiple options when brainstorming. When editing, be constructive and specific. "
        "Match the user's requested tone and genre (sci-fi, fantasy, literary, thriller, etc.)."
    ),
    "Custom": None,  # Handled separately via text area
}

# --------------------- Helper Functions ---------------------
def count_tokens(text: str) -> int:
    if not text:
        return 0
    url = "https://api.x.ai/v1/tokenize-text"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": MODEL, "text": text}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("token_count", len(data.get("tokens", [])))
    except Exception:
        return len(text) // 4  # Fallback estimate


def total_tokens_used(messages) -> int:
    try:
        return sum(count_tokens(msg["content"]) for msg in messages)
    except Exception as e:
        print(f"[token count error]: {e}")
        return 0


def enforce_token_budget(messages, budget=TOKEN_BUDGET):
    try:
        while total_tokens_used(messages) > budget:
            if len(messages) <= 2:  # Keep system + at least one other message
                break
            messages.pop(1)  # Drop oldest non-system message
    except Exception as e:
        print(f"[token budget error]: {e}")


def extract_text_from_file(uploaded_file) -> str:
    """Extract text content from common text-based file types."""
    try:
        content = uploaded_file.read()
        # Try UTF-8 first, fall back to latin-1
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1", errors="ignore")
        return text.strip()
    except Exception as e:
        st.warning(f"Could not read file: {e}")
        return ""


def build_system_prompt(base_prompt: str, knowledge: str = "") -> str:
    """Combine base persona with optional uploaded knowledge for specialized context."""
    if not knowledge:
        return base_prompt
    return (
        f"{base_prompt}\n\n"
        "=== ADDITIONAL KNOWLEDGE / CONTEXT PROVIDED BY THE USER ===\n"
        "Use the following information as authoritative context when answering. "
        "Prefer this knowledge over your general training when there is a conflict.\n\n"
        f"{knowledge}\n"
        "=== END OF ADDITIONAL KNOWLEDGE ==="
    )


def chat(user_input: str, temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS):
    messages = st.session_state.messages
    messages.append({"role": "user", "content": user_input})
    enforce_token_budget(messages)

    with st.spinner("Grok is thinking..."):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply


# --------------------- Streamlit UI ---------------------
st.set_page_config(page_title="Grok AI Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Grok AI Chatbot")
st.caption("Powered by xAI • Specialized personas + file knowledge injection")

# Sidebar
with st.sidebar:
    st.header("⚙️ Options")

    # Generation parameters
    max_tokens = st.slider("Max Tokens", 100, 4000, 1000, step=100)
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, step=0.05)

    st.divider()

    # System prompt / persona
    st.subheader("Persona / System Prompt")
    persona = st.selectbox(
        "Choose a specialized persona",
        list(SPECIALIZED_PROMPTS.keys()),
        index=0,
    )

    if persona == "Custom":
        custom_prompt = st.text_area(
            "Custom System Message",
            value="You are Grok, a highly intelligent AI assistant. Answer helpfully and truthfully.",
            height=150,
        )
        base_prompt = custom_prompt
    else:
        base_prompt = SPECIALIZED_PROMPTS[persona]
        with st.expander("View current system prompt"):
            st.markdown(base_prompt)

    st.divider()

    # File upload for specialized knowledge
    st.subheader("📎 Knowledge Upload")
    uploaded_file = st.file_uploader(
        "Upload a text file to give Grok specialized context",
        type=["txt", "md", "py", "csv", "json", "log"],
        help="The content will be injected into the system prompt as authoritative knowledge.",
    )

    knowledge_text = ""
    if uploaded_file is not None:
        knowledge_text = extract_text_from_file(uploaded_file)
        if knowledge_text:
            preview = knowledge_text[:500] + ("..." if len(knowledge_text) > 500 else "")
            st.success(f"Loaded {len(knowledge_text)} characters from `{uploaded_file.name}`")
            with st.expander("Preview uploaded content"):
                st.text(preview)
        else:
            st.warning("File appears empty or could not be read.")

    # Build the final system prompt (persona + optional knowledge)
    final_system_prompt = build_system_prompt(base_prompt, knowledge_text)

    st.divider()

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply Persona / Knowledge", use_container_width=True):
            st.session_state.messages = [{"role": "system", "content": final_system_prompt}]
            st.success("System prompt updated!")
            st.rerun()

    with col2:
        if st.button("Reset Conversation", use_container_width=True):
            st.session_state.messages = [{"role": "system", "content": final_system_prompt}]
            st.success("Conversation reset!")
            st.rerun()

    st.divider()

    # Token usage display
    if "messages" in st.session_state:
        tokens = total_tokens_used(st.session_state.messages)
        st.metric("Current Context Tokens", f"{tokens} / {TOKEN_BUDGET}")
        if tokens > TOKEN_BUDGET * 0.85:
            st.warning("Approaching token budget — older messages will be trimmed soon.")

    # Download conversation
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        conversation_text = ""
        for msg in st.session_state.messages:
            role = msg["role"].upper()
            conversation_text += f"{role}:\n{msg['content']}\n\n"
        st.download_button(
            label="📥 Download Conversation",
            data=conversation_text,
            file_name="grok_conversation.txt",
            mime="text/plain",
            use_container_width=True,
        )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": final_system_prompt}]

# Chat input
if prompt := st.chat_input("Type your message here..."):
    chat(prompt, temperature=temperature, max_tokens=max_tokens)

# Display chat history (skip the system message in the visible chat)
for message in st.session_state.messages:
    if message["role"] == "system":
        continue  # System prompt is not shown as a chat bubble
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

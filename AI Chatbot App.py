import os
import requests
from openai import OpenAI
import streamlit as st

api_key = st.secrets["OPENAI_API_KEY"] or os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

MODEL = "grok-4.5"
TEMPERATURE = 0.7
MAX_TOKENS = 1000
SYSTEM_PROMPT = "You are Grok, a highly intelligent, helpful AI assistant."
TOKEN_BUDGET = 1000

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

def count_tokens(text: str) -> int:    
    if not text:
        return 0

    url = "https://api.x.ai/v1/tokenize-text"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "text": text
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()        
        return data.get("token_count", len(data.get("tokens", [])))

    except Exception as e:        
        return len(text) // 4  # Rough estimate: 1 token ≈ 4 characters

def total_tokens_used(messages):    
    try:
        return sum(count_tokens(msg["content"]) for msg in messages)
    except Exception as e:
        print(f"[token count error]: {e}")
    return 0

def enforce_token_budget(messages, budget=TOKEN_BUDGET):    
    try:
        while total_tokens_used (messages) > budget:
            # Remove the oldest user message (index 1) to free up tokens
            if len(messages) <= 2:
                break
            messages.pop(1)
    except Exception as e:
        print(f"[token budget error]: {e}")

def chat(user_input, temperature=TEMPERATURE, max_tokens=MAX_TOKENS):
    messages = st.session_state.messages
    messages.append({"role": "user", "content": user_input})

    enforce_token_budget(messages)
    
    with st.spinner("Grok is thinking..."):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply

### Streamlit UI ###

st.title("Grok AI Chatbot")
st.sidebar.header("Options")
st.sidebar.write("This is a demo")

max_tokens = st.sidebar.slider("Max Tokens", 100, 2000, 1000)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
system_message_type = st.sidebar.selectbox("System Message", ("Helpful Assistant", "Friendly Companion", "Custom"))

if system_message_type == "Helpful Assistant":
    SYSTEM_PROMPT = "You are Grok, a helpful and informative AI assistant."
elif system_message_type == "Friendly Companion":
    SYSTEM_PROMPT = "You are Grok, a friendly and supportive AI companion."
elif system_message_type == "Custom":
    SYSTEM_PROMPT = st.sidebar.text_area("Custom System Message", "Enter your custom system message here.")
else:
    SYSTEM_PROMPT = "You are Grok, a highly intelligent AI assistant."

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if st.sidebar.button("Apply New System Message"):
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.success("System message updated!")

if st.sidebar.button("Reset Conversation"):
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.success("Conversation reset!")

if prompt := st.chat_input("Type your message here..."):
    reply = chat(prompt, temperature=temperature, max_tokens=max_tokens)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

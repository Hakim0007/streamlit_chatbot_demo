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

def chat(user_input):
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS
    )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    enforce_token_budget(messages)
    return reply

while True:
    user_input = input("You: ")
    if user_input.lower().strip() in {"exit", "quit", "bye"}:
        print("Exiting the chat. Goodbye!")
        break

    if not user_input.strip():
        continue  # Skip empty inputs
    
    reply = chat(user_input)
    print(f"Assistant: {reply}")
    print(f"Total tokens used: {total_tokens_used(messages)}")
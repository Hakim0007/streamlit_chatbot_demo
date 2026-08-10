# Grok AI Chatbot (Streamlit)

A modern web-based chatbot powered by **Grok** (xAI) built with Streamlit.  
It features a clean chat interface, adjustable generation parameters, multiple system prompt personas, conversation reset, and automatic token-budget management.

The project also includes the original CLI version (`starter_code.py`) for reference.

## Features

- **Interactive Streamlit Chat UI** with message history
- **Sidebar Controls**
  - Max Tokens slider (100–2000)
  - Temperature slider (0.0–1.0)
  - System Message presets: Helpful Assistant, Friendly Companion, or Custom
  - Apply New System Message button
  - Reset Conversation button
- **Token Budget Enforcement** – automatically drops older messages when the context exceeds the limit
- **Official xAI Tokenizer** (with character-based fallback)
- **Session State** – conversation persists during the Streamlit session
- Loading spinner while Grok is thinking

## Project Structure

```
.
├── AI Chatbot App.py      # Main Streamlit application
├── starter_code.py        # Original CLI version (for reference / learning)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Requirements

- Python 3.8+
- Packages listed in `requirements.txt`:
  - `openai`
  - `streamlit`
  - `requests`

## Installation

1. Clone or download the project.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup (API Key)

1. Get an API key from the [xAI Console](https://console.x.ai/).
2. **Strongly recommended**: Use an environment variable instead of hard-coding the key.

```bash
export XAI_API_KEY="your-xai-api-key-here"
```

3. Update the code to read the key properly:

```python
api_key = os.getenv("XAI_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
```

> **Security Warning**: The current code hard-codes the API key. Never commit real keys to version control. Always use environment variables or a secrets manager in production.

## How to Run

### Streamlit Web App (recommended)

```bash
streamlit run "AI Chatbot App.py"
```

The app will open in your browser (usually at `http://localhost:8501`).

### CLI Version (optional)

```bash
python starter_code.py
```

Type messages and press Enter. Use `exit`, `quit`, or `bye` to leave.

## Configuration

| Setting          | Default / Range          | Description                              |
|------------------|--------------------------|------------------------------------------|
| Model            | `grok-4.5`               | xAI model used                           |
| Temperature      | 0.7 (slider 0.0–1.0)     | Controls randomness                      |
| Max Tokens       | 1000 (slider 100–2000)   | Maximum length of each reply             |
| Token Budget     | 1000                     | Hard limit on total conversation tokens  |
| System Prompts   | Helpful / Friendly / Custom | Persona of the assistant              |

## How It Works

1. Conversation history is stored in `st.session_state.messages`.
2. On each user message:
   - The message is appended.
   - Token budget is enforced (oldest messages after the system prompt are dropped if needed).
   - The full history is sent to the Grok API.
   - The assistant reply is appended and displayed.
3. Sidebar options let you change temperature, max tokens, and the system prompt on the fly.
4. “Reset Conversation” clears the history (keeps the current system prompt).

Token counting uses xAI’s official `/tokenize-text` endpoint. If the request fails, it falls back to a simple `len(text) // 4` estimate.

## Notes & Limitations

- The API key is currently hard-coded — fix this before sharing or deploying.
- Token counting happens on every turn (can be optimized with caching for longer conversations).
- Token budget trimming is simple (drops oldest user messages first).
- No conversation persistence across Streamlit restarts.
- No streaming responses, tool calling, or multimodal support in this version.
- The `os.getenv` line in the original code is incorrect (it passes the key string itself instead of the variable name).

## License

MIT

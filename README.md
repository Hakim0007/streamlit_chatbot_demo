# Grok Chat Client

A simple interactive command-line chat client for **Grok** (xAI) using the OpenAI-compatible API.

The client maintains conversation history, counts tokens with xAI’s official tokenizer, and automatically trims older messages to stay within a configurable token budget.

## Features

- Interactive CLI chat with Grok (`grok-4.5`)
- Persistent conversation history within a session
- Exact token counting via xAI’s `/tokenize-text` endpoint (with character-based fallback)
- Automatic context trimming when the token budget is exceeded
- Configurable temperature, max tokens, and token budget
- Clean exit commands (`exit`, `quit`, `bye`)

## Requirements

- Python 3.8+
- Packages:
  - `openai`
  - `requests`

Install dependencies:

```bash
pip install openai requests
```

## Setup

1. Obtain an API key from [xAI Console](https://console.x.ai/).
2. **Recommended**: Set the key as an environment variable:

   ```bash
   export XAI_API_KEY="your-xai-api-key"
   ```

3. Update the script if needed so it reads the key from the environment instead of hard-coding it.

> **Security note**: Never commit API keys to version control. Prefer environment variables or a secrets manager.

## Usage

Run the script:

```bash
python grok_chat.py
```

Example session:

```
You: Hello, who are you?
Assistant: I'm Grok, built by xAI...
Total tokens used: 87

You: Explain quantum entanglement simply
Assistant: ...
Total tokens used: 312

You: exit
Exiting the chat. Goodbye!
```

## Configuration

Key constants at the top of the script:

| Variable        | Default     | Description                              |
|-----------------|-------------|------------------------------------------|
| `MODEL`         | `grok-4.5`  | Model to use                             |
| `TEMPERATURE`   | `0.7`       | Sampling temperature                     |
| `MAX_TOKENS`    | `1000`      | Maximum tokens in each reply             |
| `TOKEN_BUDGET`  | `1000`      | Hard limit on total context tokens       |
| `SYSTEM_PROMPT` | `"You are Grok..."` | System message always kept in context |

## How It Works

1. Conversation starts with a system prompt.
2. Each user message is appended to the history.
3. The full history is sent to the Grok API.
4. The assistant reply is appended.
5. Token usage of the entire history is recalculated.
6. If the total exceeds `TOKEN_BUDGET`, the oldest user messages (after the system prompt) are removed until the budget is satisfied.
7. The next turn continues with the trimmed context.

Token counting prefers the official xAI tokenizer endpoint. On failure it falls back to a simple `len(text) // 4` estimate.

## Project Structure

```
.
├── grok_chat.py      # Main chat client
└── README.md         # This file
```

## Limitations

- Single-file, session-only (no conversation persistence across runs)
- Aggressive trimming strategy (oldest user messages are dropped first)
- Token counting is performed on every turn (can be optimized with caching)
- No streaming, tool calling, or multimodal support
- API key handling should be improved for production use

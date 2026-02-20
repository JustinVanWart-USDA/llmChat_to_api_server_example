# Chat Website API Wrapper

An OpenAI-compatible API wrapper for chat websites without official APIs.

**Problem**: Many AI chat websites don't have official APIs, limiting integration with tools.  
**Solution**: This server acts as a local API wrapper, allowing you to use any chat website with tools that expect OpenAI-compatible APIs (CrewAI, LangGraph, etc.).

## ⚠️ Disclaimer

**This tool is for educational purposes and personal use only.** By using this software, you agree to:
- Only access systems you are authorized to use
- Comply with the target website's Terms of Service
- Not use this for unauthorized access or circumventing security controls
- Respect rate limits and usage policies

**This is a generic wrapper framework. Ensure you have permission before automating any website.**

## Quick Start

### Prerequisites
- Python 3.8+
- Chrome browser (for Selenium fallback)

### Installation

```bash
cd govchat_api_server
pip install -r requirements.txt
```

### Configuration

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` with your target chat website:
```env
CHAT_WEBSITE_URL=https://your-chat-website.com
USE_SELENIUM=false
PORT=8000
```

**Example configurations provided:**
- `.env.example` - Generic template (start here)
- `.env.govchat` - For GovChat (USDA authorized users only)

### Configuring for Your Chat Website

The wrapper needs to know:
1. **Base URL**: The main URL of your chat website
2. **API Endpoint** (optional): The specific API path if known
3. **Mode**: HTTP (faster) or Selenium (more reliable)

**Finding the API Endpoint:**
1. Open your chat website in Chrome
2. Open DevTools (F12) → Network tab
3. Send a test message
4. Look for API calls (usually to `/api/chat` or similar)
5. Add the endpoint path to `.env` as `CHAT_API_ENDPOINT=/api/chat`

If you can't find the endpoint, leave it empty and the wrapper will try common patterns.

### Run the Server

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
bash run.sh
```

**Or directly:**
```bash
python run.py
```

Server will start at: `http://127.0.0.1:8000`

### Test the Server

```bash
python test_client.py
```

## How It Works

### Option 1: HTTP Mode (Recommended)
- Reverse-engineers the chat website's API calls
- Makes direct HTTP requests instead of automating the browser
- Fast and efficient

### Option 2: Selenium Mode (Fallback)
- Automates a Chrome browser to interact with the chat website
- More reliable but slower
- Use if HTTP mode doesn't work

To use Selenium mode:
```env
USE_SELENIUM=true
```

## Using with CrewAI

```python
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew

# Point to local server
llm = ChatOpenAI(
    model_name="gpt-4",
    openai_api_base="http://127.0.0.1:8000/v1",
    openai_api_key="not-needed",
    temperature=0.7
)

# Create your agents
researcher = Agent(
    role="Researcher",
    goal="Research topics",
    llm=llm
)

# Create tasks and crew as normal...
```

## Using with LangGraph

```python
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

llm = ChatOpenAI(
    model_name="gpt-4",
    openai_api_base="http://127.0.0.1:8000/v1",
    openai_api_key="not-needed"
)

# Use with LangGraph...
```

## API Documentation

Interactive API docs available at: `http://127.0.0.1:8000/docs`

### Main Endpoints

#### POST /v1/chat/completions
OpenAI-compatible chat completion endpoint.

**Request:**
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7
}
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677649420,
  "model": "gpt-4",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 10,
    "total_tokens": 20
  }
}
```

#### GET /v1/models
List available models.

#### GET /conversations/{conversation_id}
Get conversation history.

#### DELETE /conversations/{conversation_id}
Delete a conversation.

## Architecture

```
Client Code (CrewAI/LangGraph)
    ↓
FastAPI Server (127.0.0.1:8000)
    ↓
Chat Website Client (HTTP or Selenium)
    ↓
Target Chat Website (configured in .env)
```

## Conversation Management

Each chat request creates or uses a conversation. Conversation IDs are automatically managed, but you can specify one:

```python
# In system message
"system": "conversation_id: abc123def456"
```

## Troubleshooting

See [CONFIG.md](CONFIG.md) for detailed troubleshooting guide.

## Next Steps

1. ✅ Start the server
2. ✅ Test with `python test_client.py`
3. ✅ Check API docs at `http://127.0.0.1:8000/docs`
4. ✅ Integrate with CrewAI/LangGraph

## Project Structure

```
govchat_api_server/
├── .env.example            # Example configuration
├── .env.govchat            # GovChat-specific config
├── app/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   └── clients/
│       ├── chat_http_client.py      # HTTP mode
│       └── chat_selenium_client.py  # Selenium mode
├── run.py                   # Server launcher
├── run.bat                  # Windows launcher
├── run.sh                   # Linux/Mac launcher
├── test_client.py           # Test script
├── requirements.txt         # Python dependencies
├── CONFIG.md               # Configuration guide
└── README.md               # This file
```

## Notes

- The server maintains conversation history with the target chat website
- Currently implements HTTP mode first, falls back to Selenium
- Timeouts default to 120 seconds (configurable via .env)
- Token counts are estimated (4 chars ≈ 1 token)
- No authentication required (local access only)

## Future Improvements

- [ ] Implement streaming responses
- [ ] Better endpoint auto-discovery
- [ ] Persistent conversation storage
- [ ] Rate limiting
- [ ] Multiple backend support

## Example Use Cases

This wrapper can work with many chat websites, including:
- Internal enterprise AI chat tools
- Custom deployed chat UIs
- Educational AI platforms
- Research prototypes

**Always ensure you have authorization before using automation tools.**

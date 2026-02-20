# GovChat API Server - Getting Started

## What You Now Have

A complete local API server that wraps the GovChat website and exposes it as an OpenAI-compatible API. This allows you to use GovChat (unlimited GPT-4 tokens) with CrewAI, LangGraph, and other tools that expect OpenAI-compatible interfaces.

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd c:\JVW\VS\govchat_api_server
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
# Windows
run.bat

# or directly
python run.py
```

You should see:
```
============================================================
  🚀 GovChat API Server
============================================================
Mode: HTTP (reverse-engineered)
Host: 127.0.0.1
Port: 8000
OpenAPI Docs: http://127.0.0.1:8000/docs
============================================================
```

### Step 3: Test It
In a new terminal:
```bash
python test_client.py
```

## What Just Happened

The server is now running and ready to accept API requests. It will:
1. Receive requests in OpenAI format at `http://127.0.0.1:8000/v1/chat/completions`
2. Forward them to GovChat using HTTP calls or browser automation
3. Return responses in OpenAI format

## Using with CrewAI

```python
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Configure to use local GovChat server
llm = ChatOpenAI(
    model_name="gpt-4",
    openai_api_base="http://127.0.0.1:8000/v1",
    openai_api_key="not-needed"
)

# Create agents as normal - they'll use GovChat!
agent = Agent(role="Analyst", llm=llm)
task = Task(description="Analyze this", agent=agent)
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
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

# Use LangGraph as normal...
```

## Project Structure

```
govchat_api_server/
├── app/                               # Main application
│   ├── __init__.py
│   ├── main.py                       # FastAPI server (the heart)
│   ├── models.py                     # Request/response models
│   └── clients/                      # Communication layer
│       ├── govchat_http_client.py   # HTTP mode (preferred)
│       └── govchat_selenium_client.py # Selenium fallback
├── run.py                            # Server launcher
├── run.bat                           # Windows launcher
├── test_client.py                    # Test script
├── examples.py                       # CrewAI/LangGraph examples
├── requirements.txt                  # Python dependencies
├── README.md                         # Full documentation
├── CONFIG.md                         # Configuration guide
└── GETTING_STARTED.md               # This file
```

## How It Works (Architecture)

```
Your Code (CrewAI/LangGraph)
         ↓
    HTTP POST to /v1/chat/completions
         ↓
    FastAPI Server (127.0.0.1:8000)
         ↓
    GovChat Client (HTTP or Selenium)
         ↓
    GovChat Website (https://govchat.ars.usda.gov)
         ↓
    Response back through the chain
```

## Two Operating Modes

### Mode 1: HTTP (Default & Recommended)
- Reverse-engineers the GovChat website's API calls
- Fast and efficient
- Used automatically by default
- If this fails, the server will help debug

### Mode 2: Selenium (Fallback)
- Automates a Chrome browser
- More reliable but slower
- Use if HTTP mode doesn't work:
```bash
set USE_SELENIUM=true
python run.py
```

## Important Next Steps

1. **Run the server**: `python run.py`
2. **Test it**: `python test_client.py`
3. **Check the logs**: You'll see if HTTP mode works or if it needs Selenium

### If HTTP Mode Doesn't Work:
1. Open the GovChat website in Chrome DevTools
2. Look at the Network tab when you send a message
3. Find the API endpoint being called
4. Update `govchat_http_client.py` with the correct endpoint
5. Or just use Selenium mode (slightly slower but reliable)

## API Endpoints You Can Use

All requests go through the server at `http://127.0.0.1:8000`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health info |
| `/v1/models` | GET | List models |
| `/v1/chat/completions` | POST | Chat endpoint (OpenAI format) |
| `/conversations/{id}` | GET | Get conversation history |
| `/conversations/{id}` | DELETE | Delete conversation |
| `/docs` | GET | Interactive API documentation |

## Troubleshooting

### "Connection refused" error
- The server isn't running. Start it: `python run.py`

### Requests timeout
- GovChat website might be slow
- Try: `CHAT_TIMEOUT=300 python run.py` (5 min timeout)

### "No response received"
- HTTP mode might not have the right endpoint
- Try Selenium: `USE_SELENIUM=true python run.py`

### Port 8000 already in use
- Use different port: `PORT=8001 python run.py`

See **CONFIG.md** for more troubleshooting.

## Key Features

✅ OpenAI-compatible API format
✅ Conversation history tracking
✅ Multi-turn conversations
✅ Works with CrewAI, LangGraph, LangChain
✅ Automatic HTTP/Selenium fallback
✅ Interactive API docs (`/docs`)
✅ No authentication needed (local only)
✅ Unlimited tokens (via GovChat)

## Next: Multi-Agent with CrewAI

Once the server is working, you can create multi-agent systems:

```python
python examples.py --example 1
```

See `examples.py` for:
1. Basic CrewAI setup
2. LangGraph workflows
3. Multi-agent collaboration

## That's It!

Your GovChat API server is ready. Start it with `python run.py` and begin integrating with CrewAI or LangGraph.

**Questions?** Check:
- `README.md` - Full documentation
- `CONFIG.md` - Configuration & troubleshooting
- `examples.py` - Usage examples

Happy building! 🚀

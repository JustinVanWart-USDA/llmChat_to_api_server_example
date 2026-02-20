# GovChat API Server Configuration

## Environment Variables
# Use HTTP mode (reverse-engineered API) or Selenium (browser automation)
# Default: false (uses HTTP)
USE_SELENIUM=false

# Server host and port
HOST=127.0.0.1
PORT=8000

# Timeout for chat responses (seconds)
CHAT_TIMEOUT=120

## Usage

### Start the server (HTTP mode - recommended first try):
```bash
python run.py
# or Windows:
run.bat
```

### Start with Selenium (if HTTP mode doesn't work):
```bash
USE_SELENIUM=true python run.py
```

### Test the server:
```bash
python test_client.py
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat endpoint (OpenAI-compatible)
- `GET /conversations/{conversation_id}` - Get conversation history
- `DELETE /conversations/{conversation_id}` - Delete a conversation

## OpenAI API Compatibility

This server implements the following OpenAI API endpoints:
- `/v1/chat/completions`
- `/v1/models`

You can use it as a drop-in replacement for OpenAI API in your code.

## Usage with CrewAI

```python
from crewai import Agent, Task, Crew
from crewai_tools import tool
from langchain.llms.base import BaseLLM
from langchain_openai import ChatOpenAI

# Point to local server instead of OpenAI
llm = ChatOpenAI(
    model_name="gpt-4",
    openai_api_base="http://127.0.0.1:8000/v1",
    openai_api_key="not-needed",
    temperature=0.7
)

# Now use with CrewAI agents...
```

## Troubleshooting

### Server won't start
- Make sure port 8000 is available: `netstat -an | grep 8000` (Windows) or `lsof -i :8000` (Unix)
- Try a different port: `PORT=8001 python run.py`

### HTTP mode not working
- Check the GovChat website network calls in browser DevTools
- Update the endpoint URLs in `app/clients/govchat_http_client.py`
- Fall back to Selenium: `USE_SELENIUM=true python run.py`

### Selenium mode is slow
- This is normal - it's automating a browser
- Consider running in headful mode for debugging: `headless=False`

### Chat requests timeout
- The website might be slow or rate-limiting
- Increase timeout: `CHAT_TIMEOUT=300 python run.py`
- Check if the GovChat website is accessible in your browser

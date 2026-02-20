# Configuration Guide - Making It Work for GovChat

This repository is now **generic** and can work with any chat website, including GovChat.

## For GovChat Users

To use with GovChat:

1. **Copy the GovChat configuration:**
   ```bash
   copy .env.govchat .env
   ```

2. **Start the server:**
   ```bash
   python run.py
   ```

3. **Test it:**
   ```bash
   python test_client.py
   ```

## For Other Chat Websites

1. **Create your .env file:**
   ```bash
   copy .env.example .env
   ```

2. **Configure your target website:**
   ```env
   CHAT_WEBSITE_URL=https://your-chat-website.com
   CHAT_API_ENDPOINT=
   USE_SELENIUM=false
   ```

3. **Find the API endpoint (if using HTTP mode):**
   - Open your chat website in Chrome
   - Press F12 to open DevTools
   - Go to Network tab
   - Send a test message
   - Look for API calls (usually `/api/chat`, `/api/completions`, etc.)
   - Add the path to `.env`: `CHAT_API_ENDPOINT=/api/chat`

4. **If HTTP doesn't work, use Selenium:**
   ```env
   USE_SELENIUM=true
   SELENIUM_HEADLESS=false  # Set to true for background operation
   ```

## Environment Variables Reference

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CHAT_WEBSITE_URL` | Base URL of chat website | `https://example-chat.com` | `https://govchat.ars.usda.gov` |
| `CHAT_API_ENDPOINT` | Specific API endpoint path | (empty - auto-discover) | `/api/chat` |
| `USE_SELENIUM` | Use browser automation | `false` | `true` |
| `HOST` | Server bind address | `127.0.0.1` | `0.0.0.0` |
| `PORT` | Server port | `8000` | `8080` |
| `CHAT_TIMEOUT` | Response timeout (seconds) | `120` | `60` |
| `SELENIUM_HEADLESS` | Run browser in background | `false` | `true` |

## How the Generic Wrapper Works

### HTTP Mode (Faster)
1. Loads `CHAT_WEBSITE_URL` from `.env`
2. If `CHAT_API_ENDPOINT` is specified, uses it directly
3. Otherwise, tries common patterns:
   - `/api/chat`
   - `/api/chat/completions`
   - `/api/messages`
   - `/v1/chat/completions`
4. Sends requests in common formats
5. Parses responses in multiple formats

### Selenium Mode (More Reliable)
1. Opens Chrome browser (headless or visible)
2. Navigates to `CHAT_WEBSITE_URL`
3. Finds input field using common selectors
4. Sends message and waits for response
5. Extracts response text from page

## Troubleshooting

### HTTP Mode Not Working?
- Check if website requires authentication
- Try Selenium mode instead
- Use DevTools to find the actual API endpoint
- Check if website uses WebSockets (not supported yet)

### Selenium Mode Not Working?
- Check Chrome is installed
- Try with `SELENIUM_HEADLESS=false` to see what's happening
- Website might have anti-automation protection
- May need custom selectors for the specific website

## Security Notes

- `.env` file is in `.gitignore` - your configuration won't be committed
- No credentials are stored in code
- Selenium mode uses your browser's logged-in session
- HTTP mode may need to handle authentication separately

## What's Safe to Share Publicly

✅ **Safe:**
- Generic wrapper code
- Configuration templates (`.env.example`)
- Documentation
- HTTP/Selenium client logic

❌ **Don't Share:**
- Your `.env` file
- Session cookies or tokens
- Specific internal system details
- Organization-specific configurations

## Example: Using with GovChat

The `.env.govchat` file contains:
```env
CHAT_WEBSITE_URL=https://govchat.ars.usda.gov
CHAT_API_ENDPOINT=
USE_SELENIUM=false
```

This works because:
1. GovChat's API follows standard patterns
2. The wrapper auto-discovers `/api/chat` endpoint
3. HTTP mode is fast and reliable
4. Uses your browser's existing authentication

**Note:** You must be authorized to use GovChat. This tool just makes it accessible via API.

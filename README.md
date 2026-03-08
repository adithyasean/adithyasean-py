# adithyasean

Drop-in `ollama` wrapper that auto-injects Cloudflare Access headers and falls back to local ollama when credentials are absent.

## Installation

```bash
pip install git+https://github.com/adithyasean/adithyasean-py.git
# or
uv pip install git+https://github.com/adithyasean/adithyasean-py.git
```

## How it works

| Condition | Mode | Host used |
|---|---|---|
| `OLLAMA_CF_CLIENT_ID` + `OLLAMA_CF_CLIENT_SECRET` set | **CF (cloud)** | `OLLAMA_HOST` from env |
| Credentials absent | **Local fallback** | `OLLAMA_LOCAL_HOST` (default: `http://localhost:11434`) |

No code changes needed — switching between cloud and local is purely a `.env` concern.

## `.env` variables

```env
# Cloud (CF) mode — all three required together
OLLAMA_CF_CLIENT_ID=<your-cf-client-id>
OLLAMA_CF_CLIENT_SECRET=<your-cf-client-secret>
OLLAMA_HOST=https://<your-ollama-host>

# Local fallback — optional override (default: http://localhost:11434)
OLLAMA_LOCAL_HOST=http://localhost:11434
```

## Usage

### Top-level `chat()` helper

```python
import adithyasean

# Mode is detected automatically from environment
print(adithyasean.mode())  # 'cf' or 'local'

response = adithyasean.chat(
    model="gemma3:1b",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.message.content)
```

### Synchronous `Client`

```python
import adithyasean

client = adithyasean.Client()          # host resolved from env
response = client.chat(
    model="gemma3:1b",
    messages=[{"role": "user", "content": "Write a haiku"}],
)
print(response.message.content)

# Or override host explicitly
client = adithyasean.Client(host="http://localhost:11434")
```

### Async `AsyncClient`

```python
import asyncio
import adithyasean

async def main():
    client = adithyasean.AsyncClient()
    response = await client.chat(
        model="gemma3:1b",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print(response.message.content)

asyncio.run(main())
```

## API

| Symbol | Description |
|---|---|
| `adithyasean.chat(*args, **kwargs)` | Top-level helper — creates `Client()` and calls `.chat()` |
| `adithyasean.Client(host=None, **kwargs)` | Sync client — CF or local depending on env |
| `adithyasean.AsyncClient(host=None, **kwargs)` | Async client — CF or local depending on env |
| `adithyasean.mode()` | Returns `'cf'` or `'local'` |

All `Client` / `AsyncClient` methods (`generate`, `chat`, `embeddings`, etc.) are inherited unchanged from `ollama.Client` / `ollama.AsyncClient`.

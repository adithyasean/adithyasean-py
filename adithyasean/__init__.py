"""Drop-in ollama wrapper that auto-injects Cloudflare Access headers.

Automatically falls back to local ollama when CF credentials are absent.

CF mode (cloud)
---------------
    Set in .env or environment:
        OLLAMA_CF_CLIENT_ID      Cloudflare Access service token client ID
        OLLAMA_CF_CLIENT_SECRET  Cloudflare Access service token client secret

    Optional overrides:
        OLLAMA_HOST              CF remote host (required — no default)

Local fallback mode
-------------------
    Leave OLLAMA_CF_CLIENT_ID / OLLAMA_CF_CLIENT_SECRET unset.
    Optional override:
        OLLAMA_LOCAL_HOST        Local host      (default: http://localhost:11434)

Usage
-----
    import adithyasean

    # Detects mode automatically:
    response = adithyasean.chat(model="gemma3:1b", messages=[{"role": "user", "content": "hi"}])
    print(response.message.content)
"""

import os

import ollama
from dotenv import load_dotenv

load_dotenv()

_LOCAL_HOST = "http://localhost:11434"


def _cf_creds() -> dict | None:
    """Return CF Access headers dict when both env vars are set, else None."""
    client_id     = os.environ.get("OLLAMA_CF_CLIENT_ID")
    client_secret = os.environ.get("OLLAMA_CF_CLIENT_SECRET")
    if client_id and client_secret:
        return {
            "CF-Access-Client-Id":     client_id,
            "CF-Access-Client-Secret": client_secret,
        }
    return None


def _resolve_host(host: str | None, cf_mode: bool) -> str:
    if host:
        return host
    if cf_mode:
        return os.environ.get("OLLAMA_HOST") or None
    return os.environ.get("OLLAMA_LOCAL_HOST", _LOCAL_HOST)


def mode() -> str:
    """Return 'cf' when CF credentials are present, 'local' otherwise."""
    return "cf" if _cf_creds() is not None else "local"


class Client(ollama.Client):
    """ollama.Client — CF Access mode when credentials are present, local otherwise."""

    def __init__(self, host: str | None = None, **kwargs) -> None:
        creds = _cf_creds()
        resolved_host = _resolve_host(host, cf_mode=creds is not None)
        if creds:
            existing = kwargs.pop("headers", {})
            super().__init__(host=resolved_host, headers={**creds, **existing}, **kwargs)
        else:
            super().__init__(host=resolved_host, **kwargs)


class AsyncClient(ollama.AsyncClient):
    """ollama.AsyncClient — CF Access mode when credentials are present, local otherwise."""

    def __init__(self, host: str | None = None, **kwargs) -> None:
        creds = _cf_creds()
        resolved_host = _resolve_host(host, cf_mode=creds is not None)
        if creds:
            existing = kwargs.pop("headers", {})
            super().__init__(host=resolved_host, headers={**creds, **existing}, **kwargs)
        else:
            super().__init__(host=resolved_host, **kwargs)


def chat(*args, **kwargs):
    """Top-level chat helper — CF mode when credentials present, local ollama otherwise."""
    return Client().chat(*args, **kwargs)

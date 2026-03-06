"""Drop-in replacement for ollama.Client that auto-injects Cloudflare Access credentials.

Loads CF credentials from .env so callers don't need to manage headers manually.

Usage
-----
    import adithyasean

    client = adithyasean.Client(host="https://ollama.adithyasean.com")
    response = client.generate(model="gemma3:4b", prompt="Write a small poem")
    print(response.response)

Required .env variables
------------------------
    OLLAMA_CF_CLIENT_ID      Cloudflare Access service token client ID
    OLLAMA_CF_CLIENT_SECRET  Cloudflare Access service token client secret
"""

import os
import sys

import ollama
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Error: environment variable {name} is not set.", file=sys.stderr)
        sys.exit(1)
    return value


class Client(ollama.Client):
    """ollama.Client with Cloudflare Access headers injected from .env."""

    def __init__(self, host: str | None = None, **kwargs) -> None:
        cf_headers = {
            "CF-Access-Client-Id": _require_env("OLLAMA_CF_CLIENT_ID"),
            "CF-Access-Client-Secret": _require_env("OLLAMA_CF_CLIENT_SECRET"),
        }
        existing = kwargs.pop("headers", {})
        super().__init__(host=host, headers={**cf_headers, **existing}, **kwargs)


class AsyncClient(ollama.AsyncClient):
    """ollama.AsyncClient with Cloudflare Access headers injected from .env."""

    def __init__(self, host: str | None = None, **kwargs) -> None:
        cf_headers = {
            "CF-Access-Client-Id": _require_env("OLLAMA_CF_CLIENT_ID"),
            "CF-Access-Client-Secret": _require_env("OLLAMA_CF_CLIENT_SECRET"),
        }
        existing = kwargs.pop("headers", {})
        super().__init__(host=host, headers={**cf_headers, **existing}, **kwargs)

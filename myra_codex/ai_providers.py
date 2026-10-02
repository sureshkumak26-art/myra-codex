"""Multi-provider AI client for Myra Codex.

Supports OpenAI-compatible endpoints: OpenAI, OpenRouter, Groq, Together,
and a local Ollama server. Local Ollama can run without a paid API key.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    model: str
    api_key_env: str | None = None
    default_key: str | None = None


PROVIDERS = {
    "openai": Provider("OpenAI", "https://api.openai.com/v1", "gpt-4.1-mini", "OPENAI_API_KEY"),
    "openrouter": Provider("OpenRouter", "https://openrouter.ai/api/v1", "openai/gpt-4o-mini", "OPENROUTER_API_KEY"),
    "groq": Provider("Groq", "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile", "GROQ_API_KEY"),
    "together": Provider("Together", "https://api.together.xyz/v1", "meta-llama/Llama-3.3-70B-Instruct-Turbo", "TOGETHER_API_KEY"),
    "ollama": Provider("Ollama (local/free)", "http://localhost:11434/v1", "qwen2.5-coder:7b", None, "ollama"),
}


class AIProviderError(RuntimeError):
    pass


class MultiAI:
    def __init__(self, provider: str | None = None, model: str | None = None):
        self.provider_id = (provider or os.getenv("MYRA_AI_PROVIDER", "ollama")).lower()
        if self.provider_id not in PROVIDERS:
            raise AIProviderError(f"Unknown provider '{self.provider_id}'. Choose: {', '.join(PROVIDERS)}")
        self.provider = PROVIDERS[self.provider_id]
        self.model = model or os.getenv("MYRA_AI_MODEL") or self.provider.model
        self.base_url = os.getenv("MYRA_AI_BASE_URL", self.provider.base_url).rstrip("/")
        self.api_key = (
            os.getenv(self.provider.api_key_env, "") if self.provider.api_key_env
            else self.provider.default_key or ""
        )

    @staticmethod
    def available_providers() -> list[dict[str, str]]:
        return [
            {"id": key, "name": value.name, "default_model": value.model,
             "requires_api_key": str(bool(value.api_key_env)).lower()}
            for key, value in PROVIDERS.items()
        ]

    def chat(self, prompt: str, system: str = "You are Myra Codex, a careful software engineering assistant.") -> str:
        if not prompt.strip():
            raise AIProviderError("Prompt cannot be empty.")
        if self.provider.api_key_env and not self.api_key:
            raise AIProviderError(f"Set {self.provider.api_key_env} to use {self.provider.name}.")
        payload = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "temperature": 0.1,
        }).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=payload, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode())
            return data["choices"][0]["message"]["content"]
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
            raise AIProviderError(f"{self.provider.name} request failed: {exc}") from exc

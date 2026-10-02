# Myra Codex

A local-first coding assistant starter with pluggable AI providers, project diagnostics, and human-approved auto-fixes.

## AI providers

Supported OpenAI-compatible providers:

- **Ollama (local, no API fee):** install Ollama, then `ollama pull qwen2.5-coder:7b`. This runs on your own hardware.
- OpenAI
- OpenRouter
- Groq
- Together AI
- Any compatible endpoint through `MYRA_AI_BASE_URL`

Set one provider in your environment:

```bash
export MYRA_AI_PROVIDER=ollama
export MYRA_AI_MODEL=qwen2.5-coder:7b
# For hosted providers, set the matching key:
# OPENAI_API_KEY=...
# OPENROUTER_API_KEY=...
# GROQ_API_KEY=...
# TOGETHER_API_KEY=...
```

Free hosted model availability, quotas, and pricing are controlled by each provider and can change. Ollama is the local option that does not require a hosted API subscription; it still uses your computer's resources.

## Detect errors

The diagnostics module runs checks and extracts error-like output:

```python
from myra_codex.diagnostics import run_check
result = run_check("python -m pytest -q", ".")
print(result.to_dict())
```

Run project checks yourself; common check suggestions are available through `common_checks()`.

## AI-assisted auto-fix

Generate a proposed patch from diagnostics:

```python
from myra_codex.ai_providers import MultiAI
from myra_codex.diagnostics import run_check
from myra_codex.autofix import propose_fix, apply_fix

diagnostic = run_check("python -m pytest -q", ".")
if diagnostic.exit_code:
    patch = propose_fix(diagnostic, ".", MultiAI())
    print(patch)  # review the diff first
    # Only after reviewing and committing/stashing your work:
    # apply_fix(patch, ".", approve=True)
```

**Safety:** Myra never silently overwrites code. A generated diff is validated with `git apply --check` and requires explicit approval before application. Commit or stash existing work first. Run tests again after applying.

## Limitations

This is a developer starter module, not a fully autonomous IDE yet. Error detection depends on checks you run (compiler, linter, tests, or build); it does not monitor every process in real time. AI provider keys belong in environment variables, never in source control.

"""Explicit subscription-CLI and API provider adapters.

Subscription mode never reads API keys and never silently falls back to an API.
Provider success is not a Legal Governor decision.
"""
from __future__ import annotations

import json
import os
import signal
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class ProviderMode(str, Enum):
    SUBSCRIPTION_CLI = "subscription_cli"
    API = "api"


class ProviderStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


class ProviderResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    TIMEOUT = "TIMEOUT"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    CLI_NOT_FOUND = "CLI_NOT_FOUND"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    PROVIDER_LIMIT_REACHED = "PROVIDER_LIMIT_REACHED"
    API_KEY_MISSING = "API_KEY_MISSING"
    UNAVAILABLE = "UNAVAILABLE"


class ProviderUnavailable(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _hash(value: object) -> str:
    import hashlib
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


@dataclass
class ProviderHealth:
    provider: str
    mode: str
    status: str
    cli_found: bool = False
    authenticated: bool | None = None
    version: str | None = None
    api_fallback_enabled: bool = False
    error_code: str | None = None
    error_message: str | None = None


@dataclass
class ProviderResult:
    provider: str
    mode: str
    status: str
    raw_output: str | None
    parsed_output: dict | None
    stderr: str | None
    exit_code: int | None
    started_at: str
    completed_at: str
    model: str | None
    cli_version: str | None
    authenticated: bool | None
    fallback_used: bool
    error_code: str | None = None
    error_message: str | None = None
    usage: dict | None = None


class ReasoningProvider:
    name = "unconfigured"
    mode = ProviderMode.SUBSCRIPTION_CLI

    def health(self) -> ProviderHealth:
        return ProviderHealth(self.name, self.mode.value, ProviderStatus.UNAVAILABLE.value, error_code="NOT_IMPLEMENTED")

    def analyze(self, prompt: str | dict, *, matter_id: str = "", agent_id: str = "", output_schema: dict | None = None) -> ProviderResult | dict:
        raise ProviderUnavailable(f"{self.name} reasoning provider is not configured")


def _prompt_text(prompt: str | dict) -> str:
    return prompt if isinstance(prompt, str) else json.dumps(prompt, sort_keys=True, ensure_ascii=False)


def _redacted_env(*remove: str) -> dict[str, str]:
    env = dict(os.environ)
    for key in remove:
        env.pop(key, None)
    return env


def _run(args: list[str], *, prompt: str, timeout: int, env: dict[str, str], cwd: str | None = None) -> tuple[str, str, int, bool]:
    process = None
    try:
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, cwd=cwd, start_new_session=True)
        stdout, stderr = process.communicate(input=prompt, timeout=timeout)
        return stdout, stderr, process.returncode, False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        if process is not None:
            try: os.killpg(process.pid, signal.SIGKILL)
            except OSError: pass
            try: process.wait(timeout=2)
            except subprocess.TimeoutExpired: pass
        return stdout, stderr, -1, True
    except OSError as exc:
        return "", str(exc), -1, False


def _parse_json_text(raw: str) -> dict | None:
    text = raw.strip()
    if not text:
        return None
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    # Claude may wrap the final JSON in a result object; Codex --json emits JSONL.
    for line in reversed(text.splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        for key in ("result", "output_text", "text", "message"):
            nested = value.get(key)
            if isinstance(nested, dict):
                return nested
            if isinstance(nested, str):
                try:
                    parsed = json.loads(nested)
                    if isinstance(parsed, dict): return parsed
                except json.JSONDecodeError:
                    continue
    return None


def _validate_structured(parsed: dict | None, schema: dict | None) -> tuple[bool, str | None]:
    if not isinstance(parsed, dict): return False, "JSON_OBJECT_REQUIRED"
    if not schema: return True, None
    required = schema.get("required", [])
    missing = [key for key in required if key not in parsed]
    return (not missing, None if not missing else "MISSING_REQUIRED_FIELDS:" + ",".join(missing))


def _strict_schema(schema: dict) -> dict:
    """Normalize the subset required by current CLI/API strict JSON schemas."""
    result = dict(schema)
    if result.get("type") == "object":
        result["additionalProperties"] = False
        result["properties"] = {key: _strict_schema(value) if isinstance(value, dict) else value for key, value in result.get("properties", {}).items()}
        if result.get("properties"):
            result["required"] = list(result["properties"].keys())
    if result.get("type") == "array" and isinstance(result.get("items"), dict):
        result["items"] = _strict_schema(result["items"])
    if result.get("type") == "array" and "items" not in result:
        result["items"] = {"type": "object", "properties": {}, "additionalProperties": False}
    return result


class ClaudeCodeProvider(ReasoningProvider):
    name = "claude"
    mode = ProviderMode.SUBSCRIPTION_CLI

    def __init__(self, command: str | None = None, model: str | None = None, timeout: int | None = None):
        self.command = command or os.environ.get("CLAUDE_CLI_COMMAND", "claude")
        self.model = model or os.environ.get("CLAUDE_MODEL") or None
        self.timeout = timeout or int(os.environ.get("PROVIDER_TIMEOUT_SECONDS", "180"))
        self.fallback_enabled = os.environ.get("ALLOW_API_FAILOVER", "false").lower() == "true"

    def health(self) -> ProviderHealth:
        path = shutil.which(self.command)
        if not path: return ProviderHealth(self.name, self.mode.value, ProviderStatus.UNAVAILABLE.value, error_code="CLI_NOT_FOUND", error_message=self.command)
        version = _version(path, [path, "--version"])
        out, err, code, timed_out = _run([path, "auth", "status"], prompt="", timeout=min(self.timeout, 20), env=_redacted_env("ANTHROPIC_API_KEY"))
        if timed_out: return ProviderHealth(self.name, self.mode.value, ProviderStatus.UNAVAILABLE.value, True, False, version, self.fallback_enabled, "AUTH_STATUS_FAILED", err[-500:])
        try: auth = json.loads(out)
        except json.JSONDecodeError: auth = None
        if auth is None and code != 0: return ProviderHealth(self.name, self.mode.value, ProviderStatus.UNAVAILABLE.value, True, False, version, self.fallback_enabled, "AUTH_STATUS_FAILED", err[-500:])
        auth = auth or {}
        authenticated = bool(auth.get("loggedIn")) and auth.get("authMethod") not in {"api_key", "none"}
        return ProviderHealth(self.name, self.mode.value, ProviderStatus.AVAILABLE.value if authenticated else ProviderStatus.UNAVAILABLE.value, True, authenticated, version, self.fallback_enabled, None if authenticated else "AUTH_REQUIRED", None if authenticated else out[-500:])

    def analyze(self, prompt: str | dict, *, matter_id: str = "", agent_id: str = "", output_schema: dict | None = None) -> ProviderResult:
        started, path = _now(), shutil.which(self.command)
        if not path: return _result(self.name, self.mode, ProviderResultStatus.CLI_NOT_FOUND, started, error_code="CLI_NOT_FOUND", error_message=self.command)
        health = self.health()
        if not health.authenticated: return _result(self.name, self.mode, ProviderResultStatus.AUTH_REQUIRED, started, cli_version=health.version, authenticated=False, error_code="AUTH_REQUIRED", error_message=health.error_message)
        args = [path, "--print", "--output-format", "json", "--no-session-persistence", "--tools", "", "--permission-mode", "plan"]
        if self.model: args += ["--model", self.model]
        if output_schema: args += ["--json-schema", json.dumps(output_schema, separators=(",", ":"))]
        stdout, stderr, code, timed_out = _run(args, prompt=_prompt_text(prompt), timeout=self.timeout, env=_redacted_env("ANTHROPIC_API_KEY"))
        if timed_out: return _result(self.name, self.mode, ProviderResultStatus.TIMEOUT, started, stdout, stderr, code, health.version, True, "TIMEOUT")
        parsed = _parse_json_text(stdout)
        valid, error = _validate_structured(parsed, output_schema)
        if code != 0: return _result(self.name, self.mode, _classify_error(stderr), started, stdout, stderr, code, health.version, True, "CLI_ERROR", stderr[-1000:])
        if not valid: return _result(self.name, self.mode, ProviderResultStatus.INVALID_OUTPUT, started, stdout, stderr, code, health.version, True, error, error)
        return _result(self.name, self.mode, ProviderResultStatus.SUCCESS, started, stdout, stderr, code, health.version, True, parsed_output=parsed)


class CodexCLIProvider(ReasoningProvider):
    name = "codex"
    mode = ProviderMode.SUBSCRIPTION_CLI

    def __init__(self, command: str | None = None, model: str | None = None, timeout: int | None = None):
        self.command = command or os.environ.get("CODEX_CLI_COMMAND", "codex")
        self.model = model or os.environ.get("CODEX_MODEL") or None
        self.timeout = timeout or int(os.environ.get("PROVIDER_TIMEOUT_SECONDS", "180"))
        self.fallback_enabled = os.environ.get("ALLOW_API_FAILOVER", "false").lower() == "true"

    def health(self) -> ProviderHealth:
        path = shutil.which(self.command)
        if not path: return ProviderHealth(self.name, self.mode.value, ProviderStatus.UNAVAILABLE.value, error_code="CLI_NOT_FOUND", error_message=self.command)
        version = _version(path, [path, "--version"])
        out, err, code, timed_out = _run([path, "login", "status"], prompt="", timeout=min(self.timeout, 20), env=_redacted_env("OPENAI_API_KEY"))
        text = (out + "\n" + err).lower()
        authenticated = code == 0 and "logged in using chatgpt" in text
        return ProviderHealth(self.name, self.mode.value, ProviderStatus.AVAILABLE.value if authenticated else ProviderStatus.UNAVAILABLE.value, True, authenticated, version, self.fallback_enabled, None if authenticated else "AUTH_REQUIRED", None if authenticated else (out + err)[-500:])

    def analyze(self, prompt: str | dict, *, matter_id: str = "", agent_id: str = "", output_schema: dict | None = None) -> ProviderResult:
        started, path = _now(), shutil.which(self.command)
        if not path: return _result(self.name, self.mode, ProviderResultStatus.CLI_NOT_FOUND, started, error_code="CLI_NOT_FOUND", error_message=self.command)
        health = self.health()
        if not health.authenticated: return _result(self.name, self.mode, ProviderResultStatus.AUTH_REQUIRED, started, cli_version=health.version, authenticated=False, error_code="AUTH_REQUIRED", error_message=health.error_message)
        schema_file = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        output_file = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        isolated_cwd = tempfile.mkdtemp(prefix="glaw-codex-")
        try:
            schema_file.write(json.dumps(_strict_schema(output_schema or {"type": "object"}))); schema_file.close(); output_file.close()
            args = [path, "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config", "--ignore-rules", "--sandbox", "read-only", "--color", "never", "--output-schema", schema_file.name, "--output-last-message", output_file.name]
            if self.model: args += ["--model", self.model]
            stdout, stderr, code, timed_out = _run(args, prompt=_prompt_text(prompt), timeout=self.timeout, env=_redacted_env("OPENAI_API_KEY"), cwd=isolated_cwd)
            raw = Path(output_file.name).read_text(encoding="utf-8", errors="replace") if Path(output_file.name).exists() else stdout
            if timed_out: return _result(self.name, self.mode, ProviderResultStatus.TIMEOUT, started, raw, stderr, code, health.version, True, "TIMEOUT")
            parsed = _parse_json_text(raw) or _parse_json_text(stdout)
            valid, error = _validate_structured(parsed, output_schema)
            if code != 0:
                diagnostic = (stderr + "\n" + stdout).strip()
                return _result(self.name, self.mode, _classify_error(diagnostic), started, raw or stdout, stderr, code, health.version, True, "CLI_ERROR", diagnostic[-2000:])
            if not valid: return _result(self.name, self.mode, ProviderResultStatus.INVALID_OUTPUT, started, raw, stderr, code, health.version, True, error, error)
            return _result(self.name, self.mode, ProviderResultStatus.SUCCESS, started, raw, stderr, code, health.version, True, parsed_output=parsed)
        finally:
            for path_to_remove in (schema_file.name, output_file.name):
                try: os.unlink(path_to_remove)
                except OSError: pass
            shutil.rmtree(isolated_cwd, ignore_errors=True)


class AnthropicAPIProvider(ReasoningProvider):
    name, mode = "claude", ProviderMode.API
    def __init__(self, model: str | None = None, timeout: int | None = None): self.model, self.timeout = model or os.environ.get("CLAUDE_MODEL") or "claude-sonnet-4-5", timeout or int(os.environ.get("PROVIDER_TIMEOUT_SECONDS", "180"))
    def health(self) -> ProviderHealth:
        if not os.environ.get("ANTHROPIC_API_KEY"): return ProviderHealth(self.name, self.mode.value, ProviderStatus.UNAVAILABLE.value, authenticated=False, error_code="API_KEY_MISSING")
        try: __import__("anthropic")
        except ImportError: return ProviderHealth(self.name, self.mode.value, ProviderStatus.UNAVAILABLE.value, authenticated=False, error_code="SDK_NOT_INSTALLED")
        return ProviderHealth(self.name, self.mode.value, ProviderStatus.AVAILABLE.value, authenticated=True)
    def analyze(self, prompt: str | dict, *, matter_id: str = "", agent_id: str = "", output_schema: dict | None = None) -> ProviderResult:
        started, health = _now(), self.health()
        if health.status != ProviderStatus.AVAILABLE.value: return _result(self.name, self.mode, ProviderResultStatus.API_KEY_MISSING if health.error_code == "API_KEY_MISSING" else ProviderResultStatus.UNAVAILABLE, started, authenticated=False, error_code=health.error_code)
        try:
            from anthropic import Anthropic
            response = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]).messages.create(model=self.model, max_tokens=4096, messages=[{"role":"user","content":_prompt_text(prompt)}])
            raw = "".join(getattr(block, "text", "") for block in response.content)
            parsed = _parse_json_text(raw); valid, error = _validate_structured(parsed, output_schema)
            return _result(self.name, self.mode, ProviderResultStatus.SUCCESS if valid else ProviderResultStatus.INVALID_OUTPUT, started, raw, parsed_output=parsed, authenticated=True, error_code=None if valid else error, error_message=None if valid else error, model=self.model)
        except Exception as exc: return _result(self.name, self.mode, ProviderResultStatus.PROVIDER_ERROR, started, authenticated=True, error_code="API_ERROR", error_message=str(exc), model=self.model)


class OpenAIAPIProvider(ReasoningProvider):
    name, mode = "codex", ProviderMode.API
    def __init__(self, model: str | None = None, timeout: int | None = None): self.model, self.timeout = model or os.environ.get("CODEX_MODEL") or "gpt-5", timeout or int(os.environ.get("PROVIDER_TIMEOUT_SECONDS", "180"))
    def health(self) -> ProviderHealth:
        if not os.environ.get("OPENAI_API_KEY"): return ProviderHealth(self.name, self.mode.value, ProviderStatus.UNAVAILABLE.value, authenticated=False, error_code="API_KEY_MISSING")
        try: __import__("openai")
        except ImportError: return ProviderHealth(self.name, self.mode.value, ProviderStatus.UNAVAILABLE.value, authenticated=False, error_code="SDK_NOT_INSTALLED")
        return ProviderHealth(self.name, self.mode.value, ProviderStatus.AVAILABLE.value, authenticated=True)
    def analyze(self, prompt: str | dict, *, matter_id: str = "", agent_id: str = "", output_schema: dict | None = None) -> ProviderResult:
        started, health = _now(), self.health()
        if health.status != ProviderStatus.AVAILABLE.value: return _result(self.name, self.mode, ProviderResultStatus.API_KEY_MISSING if health.error_code == "API_KEY_MISSING" else ProviderResultStatus.UNAVAILABLE, started, authenticated=False, error_code=health.error_code)
        try:
            from openai import OpenAI
            kwargs: dict[str, Any] = {"model": self.model, "input": _prompt_text(prompt)}
            if output_schema: kwargs["text"] = {"format": {"type": "json_schema", "name": "legal_analysis", "strict": True, "schema": _strict_schema(output_schema)}}
            response = OpenAI(api_key=os.environ["OPENAI_API_KEY"]).responses.create(**kwargs)
            raw = response.output_text
            parsed = _parse_json_text(raw); valid, error = _validate_structured(parsed, output_schema)
            return _result(self.name, self.mode, ProviderResultStatus.SUCCESS if valid else ProviderResultStatus.INVALID_OUTPUT, started, raw, parsed_output=parsed, authenticated=True, error_code=None if valid else error, error_message=None if valid else error, model=self.model)
        except Exception as exc: return _result(self.name, self.mode, ProviderResultStatus.PROVIDER_ERROR, started, authenticated=True, error_code="API_ERROR", error_message=str(exc), model=self.model)


def _version(path: str, args: list[str]) -> str | None:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=10, check=False, env=_redacted_env("ANTHROPIC_API_KEY", "OPENAI_API_KEY"))
        return (p.stdout or p.stderr).strip().splitlines()[-1][:200] if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired): return None


def _classify_error(stderr: str) -> str:
    text = (stderr or "").lower()
    if any(token in text for token in ("rate limit", "usage limit", "quota", "too many requests")): return ProviderResultStatus.PROVIDER_LIMIT_REACHED.value
    if any(token in text for token in ("auth", "login", "unauthorized", "not logged")): return ProviderResultStatus.AUTH_REQUIRED.value
    return ProviderResultStatus.PROVIDER_ERROR.value


def _result(provider: str, mode: ProviderMode, status: ProviderResultStatus | str, started: str, raw_output: str | None = None, stderr: str | None = None, exit_code: int | None = None, cli_version: str | None = None, authenticated: bool | None = None, error_code: str | None = None, error_message: str | None = None, parsed_output: dict | None = None, model: str | None = None) -> ProviderResult:
    return ProviderResult(provider, mode.value, status.value if isinstance(status, Enum) else status, raw_output, parsed_output, stderr, exit_code, started, _now(), model, cli_version, authenticated, False, error_code, error_message)


class AnthropicAdapter(ClaudeCodeProvider):
    """Backward-compatible name; subscription CLI remains the default."""


class OpenAIAdapter(CodexCLIProvider):
    """Backward-compatible name; subscription CLI remains the default."""


class EmbeddingAdapter:
    name = "unconfigured"
    def embed(self, _texts: list[str]) -> list[list[float]]:
        raise ProviderUnavailable("embedding provider is not configured")


def provider_for(provider: str, mode: str | ProviderMode):
    selected = ProviderMode(mode)
    if provider in {"claude", "anthropic"}: return ClaudeCodeProvider() if selected == ProviderMode.SUBSCRIPTION_CLI else AnthropicAPIProvider()
    if provider in {"codex", "openai"}: return CodexCLIProvider() if selected == ProviderMode.SUBSCRIPTION_CLI else OpenAIAPIProvider()
    raise ValueError(f"unsupported provider: {provider}")


def configured_agent_provider(agent_id: str):
    provider = os.environ.get("ALEXANDRA_PROVIDER" if agent_id == "alexandra_vale" else "VICTOR_PROVIDER", "claude" if agent_id == "alexandra_vale" else "codex")
    mode = os.environ.get("ALEXANDRA_MODE" if agent_id == "alexandra_vale" else "VICTOR_MODE", ProviderMode.SUBSCRIPTION_CLI.value)
    return provider_for(provider, mode)


def health_all() -> dict[str, dict]:
    result = {}
    for agent_id in ("alexandra_vale", "victor_sterling"):
        provider = configured_agent_provider(agent_id)
        result[agent_id] = asdict(provider.health())
    return result

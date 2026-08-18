#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 - <<'PY'
import os, sys
sys.path.insert(0, 'lib')
from legal_governor.providers import (
    ClaudeCodeProvider, CodexCLIProvider, ProviderMode, ProviderResultStatus,
    AnthropicAPIProvider, OpenAIAPIProvider, provider_for,
)

os.environ['ANTHROPIC_API_KEY'] = 'must-not-be-used'
os.environ['OPENAI_API_KEY'] = 'must-not-be-used'
claude = ClaudeCodeProvider(command='provider-test-missing-claude')
codex = CodexCLIProvider(command='provider-test-missing-codex')
assert claude.health().error_code == 'CLI_NOT_FOUND'
assert codex.health().error_code == 'CLI_NOT_FOUND'
assert provider_for('claude', ProviderMode.SUBSCRIPTION_CLI).mode == ProviderMode.SUBSCRIPTION_CLI
assert provider_for('codex', ProviderMode.SUBSCRIPTION_CLI).mode == ProviderMode.SUBSCRIPTION_CLI
assert provider_for('claude', ProviderMode.API).mode == ProviderMode.API
assert provider_for('codex', ProviderMode.API).mode == ProviderMode.API
assert AnthropicAPIProvider().health().error_code == 'SDK_NOT_INSTALLED' or AnthropicAPIProvider().health().status == 'AVAILABLE'
assert OpenAIAPIProvider().health().error_code == 'SDK_NOT_INSTALLED' or OpenAIAPIProvider().health().status == 'AVAILABLE'
print('ALL PASS')
PY

# Security

## Threats
Credential theft, prompt injection, dependency compromise, forged market data, replayed commands, authorization bypass, log leakage, and unsafe configuration.

## Controls
Secret manager or environment variables, redacted logs, Argon2id, short-lived tokens, owner/operator/viewer roles, strict validation, rate limits, CORS allowlist, no AI execution tools, no withdrawal-enabled exchange keys, dependency pinning, SBOM, Bandit, Semgrep, and container scanning.

## Incident Response
Halt, revoke credentials, preserve evidence, scope impact, patch, test, rotate, and document.

No sandbox or live credentials while critical or high findings remain unresolved.

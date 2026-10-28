# Changelog

All notable changes to NeuroOps AI are documented in this file.

This project uses a simplified version of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic Versioning.

## [0.1.0] - 2026-10-28

### Added
- Initial command-line prototype for NeuroOps AI.
- Log parsing and normalization to extract useful incident signals.
- Heuristic anomaly scoring, with optional Isolation Forest support when `scikit-learn` is installed.
- Rule-based root-cause hypotheses for common application, database, network, latency, memory, and authentication symptoms.
- Optional LLM-assisted incident analysis using the OpenAI API.
- Repository inspection with Python syntax checks and heuristic warnings for possible exposed secrets.
- Validation command that runs a user-specified command against a temporary copy of a repository, with a timeout.
- JSON incident-report output and a built-in demo workflow.
- Unit tests for parsing, anomaly detection, root-cause analysis, report serialization, and repository inspection.
- Initial documentation, dependency list, contribution guide, and repository hygiene files.

### Security and limitations
- This release is a prototype intended for experimentation and learning.
- It does **not** autonomously generate or apply code patches.
- Running commands in a temporary repository copy is **not** a secure sandbox. Run only trusted commands and code; use a properly isolated sandbox before testing untrusted projects.
- Secret detection is heuristic and may produce false positives or miss credentials.
- LLM-assisted analysis is optional. Review your data-handling requirements before sending logs or incident details to an external API.

### Planned
- A trained deep-learning anomaly detector with documented evaluation metrics.
- Specialized agent workflows for investigation, remediation planning, and verification.
- Human-reviewed patch generation and safer patch validation.
- CI integration, structured telemetry, and a dashboard.
- Hardened sandboxing for untrusted code execution.

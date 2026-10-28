# Contributing to NeuroOps AI

Thank you for your interest in improving **NeuroOps AI — Autonomous AI Reliability Engineer**. Contributions, bug reports, documentation improvements, tests, and thoughtful feature proposals are welcome.

## Code of Conduct

Be respectful and constructive. Focus feedback on the code, evidence, and technical decisions.

## Before You Start

- Check existing issues and pull requests to avoid duplicating work.
- For substantial changes, open an issue first to discuss the proposed approach.
- Never commit API keys, passwords, private keys, production logs, or other sensitive information.
- Do not include proprietary or personally identifiable information in test fixtures.

## Development Setup

Use Python 3.10 or newer.

```bash
git clone https://github.com/YOUR_USERNAME/neuroops-ai.git
cd neuroops-ai

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Replace `YOUR_USERNAME` with the repository owner's GitHub username.

## Run the Application

Run the built-in demonstration:

```bash
python neuroops_ai.py demo
```

Analyze a log file:

```bash
python neuroops_ai.py analyze --log-file sample.log --output incident.json
```

## Run Tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

Please run the test suite before submitting a pull request. Add or update tests for behavior you change.

## Contribution Guidelines

### Bug fixes

1. Describe the observed behavior and the expected behavior.
2. Include a minimal, reproducible example where possible.
3. Add a regression test.
4. Keep the fix focused and explain any important trade-offs.

### New features

1. Explain the problem the feature solves.
2. Describe the proposed design and any new dependencies.
3. Include tests and documentation.
4. Report evaluation results for Machine Learning features where applicable.

### Machine Learning and incident analysis

- Compare new approaches against an appropriate baseline.
- Document the dataset, assumptions, and evaluation method.
- Report relevant metrics, such as precision, recall, F1 score, and false-positive rate.
- Do not claim performance improvements without reproducible measurements.
- Keep diagnostic evidence separate from assumptions or model-generated hypotheses.

### Security-sensitive changes

- Never add real secrets to code, examples, logs, or tests.
- Treat log content and LLM output as untrusted input.
- Do not automatically execute generated code or apply patches without explicit safeguards and review.
- Clearly document any new execution risks or external data sharing.

## Suggested Workflow

1. Fork the repository on GitHub.
2. Create a descriptive branch:

   ```bash
   git checkout -b fix/describe-the-change
   ```

3. Make your changes.
4. Run tests and inspect the diff:

   ```bash
   python -m unittest discover -s tests -v
   git diff --check
   git diff
   ```

5. Commit with a clear message:

   ```bash
   git add .
   git commit -m "Add descriptive change"
   ```

6. Push your branch and open a pull request describing the motivation, implementation, testing performed, and any limitations.

## Pull Request Checklist

Before opening a pull request, confirm that:

- [ ] The change has a clear purpose.
- [ ] Tests were added or updated as appropriate.
- [ ] Existing tests pass.
- [ ] Documentation is updated when needed.
- [ ] No secrets or sensitive data are included.
- [ ] New dependencies are justified and documented.
- [ ] Limitations and known risks are stated honestly.

## Reporting Bugs

When reporting a bug, include:

- A concise title and description.
- Steps to reproduce the problem.
- Expected and actual behavior.
- Python version and operating system.
- Relevant sanitized logs or error messages.
- The smallest useful example that reproduces the issue.

Remove API keys, tokens, personal information, and confidential system details before sharing logs.

## Feature Requests

For a feature request, describe the use case, the problem it addresses, the proposed behavior, and how success could be evaluated.

Thank you for helping make NeuroOps AI more reliable, explainable, and useful.

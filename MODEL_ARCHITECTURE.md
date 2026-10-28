# NeuroOps AI — Model Architecture Guide

> **Purpose:** Give engineers, reviewers, and recruiters a clear, honest view of the model pipeline and what is implemented today.

## Executive summary

NeuroOps AI is a prototype for software-reliability investigation. It combines a machine-learning anomaly-detection baseline with rule-based root-cause hypotheses, optional LLM-assisted analysis, repository checks, and JSON incident reporting.

**Current model:** scikit-learn `IsolationForest` — an unsupervised anomaly-detection baseline.  
**Important:** This is not yet a trained deep-learning model, and the current prototype does not autonomously generate or apply code patches.

## Architecture

See [`neuroops_model_architecture.png`](neuroops_model_architecture.png) for the visual pipeline.

1. **Input telemetry** — logs or a CSV containing numeric event features.
2. **Feature validation** — verifies required columns and converts values to numeric form.
3. **Preprocessing** — imputes missing feature values and scales numeric inputs.
4. **Anomaly detection** — Isolation Forest estimates which observations differ from the baseline.
5. **Prediction output** — each row receives a `normal` or `anomaly` label, a decision score, and a heuristic severity hint.
6. **Root-cause hypotheses** — separate rule-based logic connects log evidence to plausible causes.
7. **Optional LLM analysis** — can add a natural-language investigation summary when configured.
8. **Validation checks** — syntax checks and optional user-specified commands against a temporary repository copy.
9. **Incident report** — structured JSON output supports human review and triage.

## Model input schema

| Feature | Meaning | Example |
|---|---|---:|
| `error_count` | Number of error events in the observation window | 3 |
| `warning_count` | Number of warning events in the observation window | 8 |
| `latency_ms` | Observed request or operation latency in milliseconds | 420 |
| `response_size_bytes` | Response payload size in bytes | 12000 |

The feature values above are illustrative. Production feature extraction should define consistent time windows, service boundaries, units, and missing-value rules.

## How training works

The training CSV should represent **normal baseline behaviour**. The model learns the shape of this baseline and flags observations that appear unusual relative to it. The `contamination` setting controls the expected proportion of anomalies; it is a tuning assumption, not a measured accuracy score.

Example:

```bash
python -m pip install -r requirements.txt
python model.py demo
```

Train on baseline observations:

```bash
python model.py train \
  --train-csv normal_baseline.csv \
  --model-out artifacts/anomaly_model.joblib \
  --contamination 0.05
```

Score new observations:

```bash
python model.py predict \
  --model artifacts/anomaly_model.joblib \
  --predict-csv new_observations.csv \
  --output predictions.csv
```

The CSV files must include all four required feature columns. Training data should be representative of normal operating conditions and should not contain only a narrow or unrepresentative sample.

## Prediction interpretation

- `anomaly_label`: `normal` or `anomaly`, based on the Isolation Forest prediction.
- `anomaly_score`: the model's decision-function value. Lower values are more anomalous; scores are not probabilities.
- `severity_hint`: a simple heuristic to help sort review priority. It is not a calibrated incident-severity classifier.

Treat model output as a signal for investigation, not as proof of an incident or root cause.

## Evaluation plan

Before making reliability claims, evaluate on time-separated and service-separated data where possible:

- **Precision / recall / F1** on labelled incidents.
- **False-positive rate** during normal traffic.
- **Detection delay** from incident onset to alert.
- **Performance by service and incident type**.
- **Drift monitoring** as traffic patterns and deployments change.
- **Ablations** comparing rules-only, model-only, and combined approaches.

Do not report benchmark numbers until they have been measured on a documented dataset. Avoid random row-level splits when adjacent events from the same incident could leak between train and test sets.

## Security and operational boundaries

- Do not commit API keys, credentials, private logs, or customer data.
- Review log contents before sending them to any external LLM provider.
- Treat LLM output as untrusted suggestions; require human review.
- Repository secret scanning is heuristic and may miss secrets or report false positives.
- Running a command in a temporary copy is **not a secure sandbox**. Never run untrusted code this way. Use an isolated, resource-limited sandbox for untrusted workloads.
- A saved `joblib` model artifact should only be loaded from a trusted source.

## Current limitations and roadmap

**Implemented baseline:** numeric feature validation, preprocessing, Isolation Forest training/prediction, rule-based root-cause hypotheses, optional LLM analysis, repository checks, and report generation.

**Not yet implemented:** a trained deep-learning detector, specialized autonomous agents, automatic code-patch generation/application, robust CI integrations, and a hardened execution sandbox.

A credible next milestone is to build a reproducible labelled dataset, compare Isolation Forest with a supervised or sequence-based model, publish evaluation metrics, and add tests for data leakage, drift, and failure cases.

## Project files

- `model.py` — inspectable anomaly-detection model and CLI.
- `neuroops_ai.py` — main prototype workflow and incident-analysis utilities.
- `tests/test_neuroops.py` — unit tests for the existing prototype.
- `requirements.txt` — Python dependencies.
- `README.md` — project overview and quick start.

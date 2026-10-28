"""
NeuroOps AI — Anomaly Detection Model
=====================================

A small, inspectable machine-learning component for detecting unusual
software-log events using scikit-learn's Isolation Forest.

This is a practical baseline, not a trained deep-learning model. It uses
numeric features extracted from each log event. For a real deployment,
evaluate it on labelled production-like data and tune the threshold.

Quick start:
    python -m pip install -r requirements.txt
    python model.py --demo
    python model.py --train-csv sample_features.csv --model-out artifacts/anomaly_model.joblib
    python model.py --model artifacts/anomaly_model.joblib --predict-csv new_features.csv

CSV feature columns:
    error_count, warning_count, latency_ms, response_size_bytes

The training CSV should contain rows representing NORMAL behaviour. The
model learns a baseline and flags observations that differ from it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import IsolationForest
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:  # Clear guidance if optional dependencies are absent.
    raise SystemExit(
        "Missing ML dependencies. Install them with: "
        "python -m pip install -r requirements.txt"
    ) from exc


FEATURE_COLUMNS = [
    "error_count",
    "warning_count",
    "latency_ms",
    "response_size_bytes",
]
MODEL_FORMAT_VERSION = 1


def build_model(contamination: float = 0.05, random_state: int = 42) -> Pipeline:
    """Build a preprocessing + Isolation Forest anomaly-detection pipeline."""
    if not 0.0 < contamination <= 0.5:
        raise ValueError("contamination must be greater than 0 and at most 0.5")

    estimator = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("detector", estimator),
        ]
    )


def validate_features(data: pd.DataFrame) -> pd.DataFrame:
    """Validate and return the expected numeric feature columns."""
    missing = [column for column in FEATURE_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(
            "Missing required feature column(s): " + ", ".join(missing)
        )

    result = data[FEATURE_COLUMNS].copy()
    for column in FEATURE_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    if result.isna().all(axis=1).any():
        bad_rows = result.index[result.isna().all(axis=1)].tolist()
        raise ValueError(
            f"Rows {bad_rows[:10]} contain no usable numeric feature values."
        )
    return result


def train_model(
    csv_path: str | Path,
    model_path: str | Path,
    contamination: float = 0.05,
    random_state: int = 42,
) -> dict[str, Any]:
    """Train on baseline/normal examples and save the model artifact."""
    data = pd.read_csv(csv_path)
    features = validate_features(data)

    if len(features) < 10:
        raise ValueError(
            "Provide at least 10 baseline rows; more representative data is better."
        )

    model = build_model(contamination=contamination, random_state=random_state)
    model.fit(features)

    output = Path(model_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "format_version": MODEL_FORMAT_VERSION,
        "feature_columns": FEATURE_COLUMNS,
        "model": model,
        "contamination": contamination,
        "training_rows": int(len(features)),
        "model_type": "sklearn.ensemble.IsolationForest",
    }
    joblib.dump(artifact, output)

    return {
        "status": "trained",
        "model_path": str(output),
        "training_rows": int(len(features)),
        "feature_columns": FEATURE_COLUMNS,
        "contamination": contamination,
    }


def load_model(model_path: str | Path) -> dict[str, Any]:
    """Load and validate a saved model artifact."""
    artifact = joblib.load(model_path)
    if not isinstance(artifact, dict):
        raise ValueError("Invalid model artifact format.")
    if artifact.get("format_version") != MODEL_FORMAT_VERSION:
        raise ValueError("Unsupported model artifact version.")
    if artifact.get("feature_columns") != FEATURE_COLUMNS:
        raise ValueError("Model feature columns do not match this code version.")
    if "model" not in artifact:
        raise ValueError("Model artifact does not contain a trained estimator.")
    return artifact


def predict(data: pd.DataFrame, artifact: dict[str, Any]) -> pd.DataFrame:
    """Return predictions, anomaly scores, and a simple severity suggestion."""
    features = validate_features(data)
    estimator = artifact["model"]

    # IsolationForest returns 1 for inliers and -1 for outliers.
    labels = estimator.predict(features)
    # Lower decision_function scores indicate more anomalous observations.
    scores = estimator.decision_function(features)

    results = data.copy()
    results["anomaly_label"] = [
        "anomaly" if label == -1 else "normal" for label in labels
    ]
    results["anomaly_score"] = [round(float(score), 6) for score in scores]
    results["severity_hint"] = [
        "high" if label == -1 and score < -0.1
        else "medium" if label == -1
        else "low"
        for label, score in zip(labels, scores)
    ]
    return results


def run_demo() -> None:
    """Train a tiny illustrative baseline and score example incidents."""
    rng = np.random.default_rng(42)
    baseline = pd.DataFrame(
        {
            "error_count": rng.poisson(1.0, size=120),
            "warning_count": rng.poisson(3.0, size=120),
            "latency_ms": rng.normal(180, 35, size=120).clip(30, None),
            "response_size_bytes": rng.normal(12000, 2500, size=120).clip(500, None),
        }
    )

    model = build_model(contamination=0.05)
    model.fit(baseline)

    examples = pd.DataFrame(
        [
            {
                "event": "Routine request",
                "error_count": 1,
                "warning_count": 2,
                "latency_ms": 170,
                "response_size_bytes": 11800,
            },
            {
                "event": "Latency spike",
                "error_count": 2,
                "warning_count": 9,
                "latency_ms": 2400,
                "response_size_bytes": 16000,
            },
            {
                "event": "Error burst",
                "error_count": 35,
                "warning_count": 28,
                "latency_ms": 950,
                "response_size_bytes": 8000,
            },
        ]
    )

    temporary_artifact = {
        "format_version": MODEL_FORMAT_VERSION,
        "feature_columns": FEATURE_COLUMNS,
        "model": model,
    }
    print(predict(examples, temporary_artifact).to_string(index=False))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="NeuroOps AI baseline anomaly-detection model."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_parser = subparsers.add_parser("demo", help="Run an illustrative demo.")
    demo_parser.set_defaults(action="demo")

    train_parser = subparsers.add_parser(
        "train", help="Train on a CSV of baseline/normal observations."
    )
    train_parser.add_argument("--train-csv", required=True)
    train_parser.add_argument("--model-out", default="artifacts/anomaly_model.joblib")
    train_parser.add_argument("--contamination", type=float, default=0.05)
    train_parser.add_argument("--random-state", type=int, default=42)
    train_parser.set_defaults(action="train")

    predict_parser = subparsers.add_parser(
        "predict", help="Score rows in a CSV using a saved model."
    )
    predict_parser.add_argument("--model", required=True)
    predict_parser.add_argument("--predict-csv", required=True)
    predict_parser.add_argument("--output", default="predictions.csv")
    predict_parser.set_defaults(action="predict")

    args = parser.parse_args()

    try:
        if args.action == "demo":
            run_demo()
        elif args.action == "train":
            result = train_model(
                args.train_csv,
                args.model_out,
                contamination=args.contamination,
                random_state=args.random_state,
            )
            print(json.dumps(result, indent=2))
        elif args.action == "predict":
            artifact = load_model(args.model)
            data = pd.read_csv(args.predict_csv)
            results = predict(data, artifact)
            results.to_csv(args.output, index=False)
            print(
                json.dumps(
                    {
                        "status": "complete",
                        "rows_scored": int(len(results)),
                        "output": args.output,
                        "anomalies_found": int(
                            (results["anomaly_label"] == "anomaly").sum()
                        ),
                    },
                    indent=2,
                )
            )
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

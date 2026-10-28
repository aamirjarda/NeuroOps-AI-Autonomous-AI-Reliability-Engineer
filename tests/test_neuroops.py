"""Automated tests for the NeuroOps AI prototype.

Run from the repository root:
    python -m unittest discover -s tests -v

These tests use only Python's standard library and the project's public functions.
"""

import json
import tempfile
import unittest
from pathlib import Path

import neuroops_ai as neuroops


class LogParsingTests(unittest.TestCase):
    def test_parses_timestamp_level_and_message(self):
        event = neuroops.parse_log_line(
            "2026-10-28T09:00:00Z ERROR service=checkout Database connection refused",
            source="app.log",
            line_number=7,
        )
        self.assertEqual(event.timestamp, "2026-10-28T09:00:00Z")
        self.assertEqual(event.level, "ERROR")
        self.assertEqual(event.source, "checkout")
        self.assertIn("Database connection refused", event.message)
        self.assertEqual(event.line_number, 7)

    def test_normalizes_warning_level(self):
        event = neuroops.parse_log_line("WARNING disk usage is high", "app.log", 1)
        self.assertEqual(event.level, "WARN")

    def test_events_from_text_ignores_blank_lines(self):
        events = neuroops.events_from_text("INFO started\n\nERROR failed\n", "test.log")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[1].level, "ERROR")


class AnomalyDetectionTests(unittest.TestCase):
    def test_error_event_is_flagged(self):
        events = neuroops.events_from_text(
            "2026-10-28T09:00:00Z INFO service=api request completed 20ms\n"
            "2026-10-28T09:00:01Z ERROR service=api database connection refused\n"
        )
        anomalies = neuroops.detect_anomalies(events, use_ml=False)
        self.assertTrue(any(item.event["level"] == "ERROR" for item in anomalies))

    def test_empty_event_list_returns_no_anomalies(self):
        self.assertEqual(neuroops.detect_anomalies([], use_ml=False), [])

    def test_feature_extraction_includes_latency(self):
        event = neuroops.parse_log_line("INFO request took 2 seconds", "app.log", 1)
        features = neuroops.event_features(event)
        self.assertEqual(features["latency_ms"], 2000.0)


class RootCauseTests(unittest.TestCase):
    def test_database_failure_produces_database_hypothesis(self):
        events = neuroops.events_from_text(
            "ERROR Database connection refused\n"
            "ERROR too many connections in connection pool\n"
        )
        anomalies = neuroops.detect_anomalies(events, use_ml=False)
        causes = neuroops.analyze_root_causes(events, anomalies)
        self.assertTrue(causes)
        self.assertEqual(causes[0].title, "Database connectivity or saturation")
        self.assertTrue(causes[0].evidence)

    def test_unclassified_anomaly_gets_fallback_hypothesis(self):
        events = neuroops.events_from_text("ERROR unexpected failure marker\n")
        anomalies = neuroops.detect_anomalies(events, use_ml=False)
        causes = neuroops.analyze_root_causes(events, anomalies)
        self.assertTrue(causes)


class ReportTests(unittest.TestCase):
    def test_report_serializes_to_json(self):
        events = neuroops.events_from_text("ERROR Database connection refused\n")
        report = neuroops.analyze_events(events, project="unit-test", use_ml=False)
        payload = json.loads(report.to_json())
        self.assertEqual(payload["project"], "unit-test")
        self.assertIn("severity", payload)
        self.assertIn("root_causes", payload)
        self.assertTrue(payload["incident_id"].startswith("NO-"))

    def test_severity_is_critical_for_critical_event(self):
        events = neuroops.events_from_text("CRITICAL service unavailable\n")
        self.assertEqual(neuroops.classify_severity(events, []), "critical")


class RepositoryInspectionTests(unittest.TestCase):
    def test_inspector_detects_python_syntax_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / "broken.py").write_text("def broken(:\n    pass\n", encoding="utf-8")
            summary = neuroops.inspect_repository(repo)
            self.assertEqual(len(summary["python_syntax_errors"]), 1)
            self.assertEqual(summary["python_syntax_errors"][0]["path"], "broken.py")

    def test_inspector_skips_git_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / ".git").mkdir()
            (repo / ".git" / "ignored.py").write_text("def broken(:", encoding="utf-8")
            (repo / "valid.py").write_text("print('ok')\n", encoding="utf-8")
            summary = neuroops.inspect_repository(repo)
            paths = {item["path"] for item in summary["files"]}
            self.assertIn("valid.py", paths)
            self.assertNotIn(".git/ignored.py", paths)


if __name__ == "__main__":
    unittest.main(verbosity=2)

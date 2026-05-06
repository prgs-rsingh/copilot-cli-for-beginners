"""Instrumentation tests — verify structured log events fire across all modules.

Strategy: monkeypatch each module's `logger` with a `LogCapture` instance that
records calls. This is more reliable than fd-level stderr capture (which interacts
unpredictably with pytest's own capture pipeline) and cleanly tests the contract:
  - The correct event name is passed to the right log level
  - The required payload fields are present

To validate instrumentation against real JSON output:
    LOG_LEVEL=DEBUG python book_app.py list 2>&1 | python -m json.tool

Pattern contract (all modules):
  - from logging_config import get_logger; logger = get_logger(__name__)
  - Event names: <module>.<action> dot-notation
  - Extra fields are JSON-serialisable primitives
  - Output goes to stderr only
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
import book_app
import utils


# ---------------------------------------------------------------------------
# Log capture helper
# ---------------------------------------------------------------------------

class LogCapture:
    """Records logger.info/warning/error calls as dicts for assertion."""

    def __init__(self):
        self.records: list[dict] = []

    def info(self, event: str, *, extra: dict | None = None) -> None:
        self.records.append({"event": event, "level": "INFO", **(extra or {})})

    def warning(self, event: str, *, extra: dict | None = None) -> None:
        self.records.append({"event": event, "level": "WARNING", **(extra or {})})

    def error(self, event: str, *, extra: dict | None = None) -> None:
        self.records.append({"event": event, "level": "ERROR", **(extra or {})})

    def events(self, name: str) -> list[dict]:
        return [r for r in self.records if r["event"] == name]


@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    """Isolate data file for every test."""
    data_file = tmp_path / "data.json"
    data_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))
    monkeypatch.setattr(book_app, "collection", books.BookCollection())


# ---------------------------------------------------------------------------
# book_app.py — app.command, app.error, app.unknown_command
# ---------------------------------------------------------------------------

class TestBookAppLogging:
    def test_known_command_emits_app_command(self, monkeypatch):
        """app.command is logged at INFO for every valid dispatch."""
        cap = LogCapture()
        monkeypatch.setattr(book_app, "logger", cap)
        monkeypatch.setattr(sys, "argv", ["book_app.py", "list"])
        book_app.main()
        assert cap.events("app.command"), "app.command must be emitted"
        ev = cap.events("app.command")[0]
        assert ev["level"] == "INFO"
        assert ev["command"] == "list"

    def test_unknown_command_emits_warning(self, monkeypatch):
        """app.unknown_command is logged at WARNING for unrecognised commands."""
        cap = LogCapture()
        monkeypatch.setattr(book_app, "logger", cap)
        monkeypatch.setattr(sys, "argv", ["book_app.py", "bogus"])
        book_app.main()
        assert cap.events("app.unknown_command"), "app.unknown_command must be emitted"
        ev = cap.events("app.unknown_command")[0]
        assert ev["level"] == "WARNING"
        assert ev["command"] == "bogus"

    def test_add_error_emits_app_error(self, monkeypatch):
        """app.error is logged at WARNING when handle_add() raises ValueError."""
        cap = LogCapture()
        monkeypatch.setattr(book_app, "logger", cap)
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        # also patch utils.logger to suppress year.parse_rejected noise
        utils_cap = LogCapture()
        monkeypatch.setattr(utils, "logger", utils_cap)
        responses = iter(["Test Book", "Author", "9999"])
        monkeypatch.setattr(book_app, "prompt", lambda _: next(responses))
        book_app.handle_add()
        assert cap.events("app.error"), "app.error must be emitted on ValueError"
        ev = cap.events("app.error")[0]
        assert ev["level"] == "WARNING"
        assert ev["command"] == "add"
        assert "error" in ev


# ---------------------------------------------------------------------------
# utils.py — year.parse_error, year.parse_rejected
# ---------------------------------------------------------------------------

class TestUtilsLogging:
    def test_invalid_year_emits_parse_error(self, monkeypatch):
        """year.parse_error is logged at WARNING when year input is non-numeric."""
        cap = LogCapture()
        monkeypatch.setattr(utils, "logger", cap)
        responses = iter(["Title", "Author", "notayear"])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        utils.get_book_details()
        assert cap.events("year.parse_error"), "year.parse_error must be emitted"
        ev = cap.events("year.parse_error")[0]
        assert ev["level"] == "WARNING"
        assert ev["input"] == "notayear"
        assert "reason" in ev

    def test_strict_year_out_of_range_emits_parse_rejected(self, monkeypatch):
        """year.parse_rejected is logged at INFO when strict guard rejects input."""
        cap = LogCapture()
        monkeypatch.setattr(utils, "logger", cap)
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        with pytest.raises(ValueError):
            utils.parse_year("9999")
        assert cap.events("year.parse_rejected"), "year.parse_rejected must be emitted"
        ev = cap.events("year.parse_rejected")[0]
        assert ev["level"] == "INFO"
        assert ev["year"] == 9999
        assert "limit" in ev


# ---------------------------------------------------------------------------
# resilience.py — retry.attempt, retry.exhausted
# ---------------------------------------------------------------------------

class TestResilienceLogging:
    def test_retry_attempt_logged_on_transient_failure(self, monkeypatch):
        """retry.attempt is logged at WARNING for each non-final retry."""
        import resilience
        from resilience import retry_with_backoff

        cap = LogCapture()
        monkeypatch.setattr(resilience, "logger", cap)
        monkeypatch.setattr(resilience.time, "sleep", lambda _: None)

        call_count = {"n": 0}

        @retry_with_backoff(max_retries=3, initial_delay=0.0, backoff_factor=1.0, exceptions=(OSError,))
        def flaky():
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise OSError("transient")
            return "ok"

        result = flaky()
        assert result == "ok"

        attempts = cap.events("retry.attempt")
        assert len(attempts) == 2, f"Expected 2 retry.attempt events; got {len(attempts)}"
        assert attempts[0]["fn"] == "flaky"
        assert attempts[0]["attempt"] == 1
        assert attempts[1]["attempt"] == 2
        assert all(e["level"] == "WARNING" for e in attempts)

    def test_retry_exhausted_logged_after_all_retries_fail(self, monkeypatch):
        """retry.exhausted is logged at ERROR when all retries are consumed."""
        import resilience
        from resilience import retry_with_backoff

        cap = LogCapture()
        monkeypatch.setattr(resilience, "logger", cap)
        monkeypatch.setattr(resilience.time, "sleep", lambda _: None)

        @retry_with_backoff(max_retries=2, initial_delay=0.0, backoff_factor=1.0, exceptions=(OSError,))
        def always_fails():
            raise OSError("persistent")

        with pytest.raises(OSError):
            always_fails()

        exhausted = cap.events("retry.exhausted")
        assert len(exhausted) == 1
        ev = exhausted[0]
        assert ev["level"] == "ERROR"
        assert ev["fn"] == "always_fails"
        assert ev["attempts"] == 2
        assert "error" in ev


"""
Feature flag tests: BOOK_APP_STRICT_YEAR and BOOK_APP_STRICT_REMOVE

Validates parse_year() and handle_remove() behaviour in both flag states (ON and OFF).
Every test explicitly sets or clears the env var via monkeypatch so
tests are isolated regardless of the shell environment.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime

import pytest

import book_app
import books
import utils
from utils import parse_year


class LogCapture:
    """Minimal logger mock — records calls for assertion."""
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


# ---------------------------------------------------------------------------
# Flag OFF (default) — any integer year is accepted
# ---------------------------------------------------------------------------

class TestStrictYearOff:
    """BOOK_APP_STRICT_YEAR unset → permissive year parsing."""

    def test_blank_returns_zero(self, monkeypatch):
        monkeypatch.delenv("BOOK_APP_STRICT_YEAR", raising=False)
        assert parse_year("") == 0

    def test_valid_historic_year(self, monkeypatch):
        monkeypatch.delenv("BOOK_APP_STRICT_YEAR", raising=False)
        assert parse_year("1949") == 1949

    def test_future_year_accepted(self, monkeypatch):
        """Flag OFF: future years pass without error."""
        monkeypatch.delenv("BOOK_APP_STRICT_YEAR", raising=False)
        assert parse_year("9999") == 9999

    def test_zero_year_accepted(self, monkeypatch):
        """Flag OFF: numeric zero is a valid (if unusual) year."""
        monkeypatch.delenv("BOOK_APP_STRICT_YEAR", raising=False)
        assert parse_year("0") == 0

    def test_non_numeric_raises(self, monkeypatch):
        monkeypatch.delenv("BOOK_APP_STRICT_YEAR", raising=False)
        with pytest.raises(ValueError):
            parse_year("abc")


# ---------------------------------------------------------------------------
# Flag ON — strict range [1, current_year] enforced
# ---------------------------------------------------------------------------

class TestStrictYearOn:
    """BOOK_APP_STRICT_YEAR=1 → only years in [1, current_year] accepted."""

    def test_blank_still_returns_zero(self, monkeypatch):
        """Blank input bypasses range check even with flag ON."""
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        assert parse_year("") == 0

    def test_valid_historic_year(self, monkeypatch):
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        assert parse_year("1949") == 1949

    def test_current_year_accepted(self, monkeypatch):
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        current_year = str(datetime.date.today().year)
        assert parse_year(current_year) == datetime.date.today().year

    def test_future_year_rejected(self, monkeypatch):
        """Flag ON: a year beyond current_year must raise ValueError."""
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        future = str(datetime.date.today().year + 1)
        with pytest.raises(ValueError, match="out of range"):
            parse_year(future)

    def test_far_future_year_rejected(self, monkeypatch):
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        with pytest.raises(ValueError, match="out of range"):
            parse_year("9999")

    def test_zero_year_rejected(self, monkeypatch):
        """Flag ON: numeric 0 (as string '0') is out of range [1, current_year]."""
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        with pytest.raises(ValueError, match="out of range"):
            parse_year("0")

    def test_negative_year_rejected(self, monkeypatch):
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        with pytest.raises(ValueError, match="out of range"):
            parse_year("-100")

    def test_non_numeric_raises(self, monkeypatch):
        """Non-numeric input raises ValueError regardless of flag state."""
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        with pytest.raises(ValueError):
            parse_year("abc")

    @pytest.mark.parametrize("truthy", ["1", "true", "True", "TRUE", "yes", "Yes", "YES"])
    def test_flag_truthy_values(self, monkeypatch, truthy):
        """All documented truthy values activate strict mode."""
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", truthy)
        with pytest.raises(ValueError, match="out of range"):
            parse_year("9999")

    @pytest.mark.parametrize("falsy", ["0", "false", "no", "", "off"])
    def test_flag_falsy_values_are_permissive(self, monkeypatch, falsy):
        """Values outside the truthy set leave flag OFF."""
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", falsy)
        assert parse_year("9999") == 9999


# ---------------------------------------------------------------------------
# Shared fixture for BOOK_APP_STRICT_REMOVE tests
# ---------------------------------------------------------------------------

@pytest.fixture
def collection_with_book(tmp_path, monkeypatch):
    """Isolated BookCollection with one pre-loaded book."""
    data_file = tmp_path / "data.json"
    data_file.write_text('[{"title": "Dune", "author": "Herbert", "year": 1965, "read": false}]')
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))
    coll = books.BookCollection()
    monkeypatch.setattr(book_app, "collection", coll)
    return coll


# ---------------------------------------------------------------------------
# BOOK_APP_STRICT_REMOVE — Flag OFF (default): hedged message
# ---------------------------------------------------------------------------

class TestStrictRemoveOff:
    """BOOK_APP_STRICT_REMOVE unset → hedged 'Book removed if it existed.' message."""

    def test_found_book_prints_hedged_message(self, monkeypatch, collection_with_book, capsys):
        """Flag OFF: success still prints hedged message."""
        monkeypatch.delenv("BOOK_APP_STRICT_REMOVE", raising=False)
        monkeypatch.setattr("builtins.input", lambda _: "Dune")
        book_app.handle_remove()
        out = capsys.readouterr().out
        assert "Book removed if it existed." in out
        assert "successfully" not in out

    def test_missing_book_prints_hedged_message(self, monkeypatch, collection_with_book, capsys):
        """Flag OFF: not-found still prints hedged message."""
        monkeypatch.delenv("BOOK_APP_STRICT_REMOVE", raising=False)
        monkeypatch.setattr("builtins.input", lambda _: "Nonexistent")
        book_app.handle_remove()
        out = capsys.readouterr().out
        assert "Book removed if it existed." in out
        assert "No book found" not in out


# ---------------------------------------------------------------------------
# BOOK_APP_STRICT_REMOVE — Flag ON: precise success/failure feedback
# ---------------------------------------------------------------------------

class TestStrictRemoveOn:
    """BOOK_APP_STRICT_REMOVE=1 → precise 'removed successfully' or 'No book found' message."""

    def test_found_book_prints_success(self, monkeypatch, collection_with_book, capsys):
        """Flag ON: removing an existing book gives success message."""
        monkeypatch.setenv("BOOK_APP_STRICT_REMOVE", "1")
        monkeypatch.setattr("builtins.input", lambda _: "Dune")
        book_app.handle_remove()
        out = capsys.readouterr().out
        assert "Book removed successfully." in out
        assert "if it existed" not in out

    def test_missing_book_prints_not_found(self, monkeypatch, collection_with_book, capsys):
        """Flag ON: removing a non-existent book gives not-found message."""
        monkeypatch.setenv("BOOK_APP_STRICT_REMOVE", "1")
        monkeypatch.setattr("builtins.input", lambda _: "Nonexistent")
        book_app.handle_remove()
        out = capsys.readouterr().out
        assert "No book found with that title." in out
        assert "if it existed" not in out

    @pytest.mark.parametrize("truthy", ["1", "true", "yes", "True", "YES"])
    def test_flag_truthy_values(self, monkeypatch, collection_with_book, capsys, truthy):
        """All documented truthy values activate strict remove mode."""
        monkeypatch.setenv("BOOK_APP_STRICT_REMOVE", truthy)
        monkeypatch.setattr("builtins.input", lambda _: "Dune")
        book_app.handle_remove()
        out = capsys.readouterr().out
        assert "Book removed successfully." in out

    @pytest.mark.parametrize("falsy", ["0", "false", "no", "", "off"])
    def test_flag_falsy_values_give_hedged_message(self, monkeypatch, collection_with_book, capsys, falsy):
        """Non-truthy values leave flag OFF → hedged message."""
        monkeypatch.setenv("BOOK_APP_STRICT_REMOVE", falsy)
        monkeypatch.setattr("builtins.input", lambda _: "Dune")
        book_app.handle_remove()
        out = capsys.readouterr().out
        assert "Book removed if it existed." in out


# ---------------------------------------------------------------------------
# Telemetry: flag.active event emitted once when flag is ON
# ---------------------------------------------------------------------------

class TestFlagTelemetry:
    """_flag_enabled() emits 'flag.active' at INFO once per flag per process when ON."""

    def test_flag_active_emits_telemetry_when_on(self, monkeypatch):
        """flag.active INFO event fires when flag is ON."""
        monkeypatch.setenv("BOOK_APP_STRICT_REMOVE", "1")
        monkeypatch.setattr(utils, "_logged_flags", set())  # reset per-process dedup set
        cap = LogCapture()
        monkeypatch.setattr(utils, "logger", cap)
        result = utils._flag_enabled("BOOK_APP_STRICT_REMOVE")
        assert result is True
        evs = cap.events("flag.active")
        assert len(evs) == 1
        assert evs[0]["flag"] == "BOOK_APP_STRICT_REMOVE"
        assert evs[0]["level"] == "INFO"

    def test_flag_active_not_emitted_when_off(self, monkeypatch):
        """No telemetry event when flag is OFF (default quiet state)."""
        monkeypatch.delenv("BOOK_APP_STRICT_REMOVE", raising=False)
        monkeypatch.setattr(utils, "_logged_flags", set())
        cap = LogCapture()
        monkeypatch.setattr(utils, "logger", cap)
        result = utils._flag_enabled("BOOK_APP_STRICT_REMOVE")
        assert result is False
        assert cap.events("flag.active") == []

    def test_flag_active_emitted_only_once_per_process(self, monkeypatch):
        """Dedup: second evaluation of same ON flag does not emit a second event."""
        monkeypatch.setenv("BOOK_APP_STRICT_REMOVE", "1")
        monkeypatch.setattr(utils, "_logged_flags", set())
        cap = LogCapture()
        monkeypatch.setattr(utils, "logger", cap)
        utils._flag_enabled("BOOK_APP_STRICT_REMOVE")
        utils._flag_enabled("BOOK_APP_STRICT_REMOVE")
        utils._flag_enabled("BOOK_APP_STRICT_REMOVE")
        assert len(cap.events("flag.active")) == 1  # exactly one, not three

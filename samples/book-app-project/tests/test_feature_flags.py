"""
Feature flag tests: BOOK_APP_STRICT_YEAR

Validates parse_year() behaviour in both flag states (ON and OFF).
Every test explicitly sets or clears the env var via monkeypatch so
tests are isolated regardless of the shell environment.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import pytest
from utils import parse_year


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

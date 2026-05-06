"""Failure tests for the resilience.retry_with_backoff helper.

Tests cover:
- Decorator unit behaviour (retries, backoff timing, final raise)
- Integration: save_books() retries on transient OSError
- Guard-rail: invalid tuning parameters raise ValueError at decoration time
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, call, patch

import pytest

import books
from books import BookCollection
from resilience import retry_with_backoff

# ── Decorator unit tests ──────────────────────────────────────────────────────

class TestRetryWithBackoff:

    def test_success_on_first_attempt_no_sleep(self):
        """A function that never raises should be called exactly once, no sleep."""
        fn = MagicMock(return_value="ok")
        decorated = retry_with_backoff(max_retries=3, initial_delay=0.1)(fn)

        with patch("resilience.time.sleep") as mock_sleep:
            result = decorated()

        assert result == "ok"
        fn.assert_called_once()
        mock_sleep.assert_not_called()

    def test_retries_then_succeeds(self):
        """Function fails twice then succeeds on the third attempt."""
        fn = MagicMock(side_effect=[OSError("disk full"), OSError("disk full"), "recovered"])
        decorated = retry_with_backoff(max_retries=3, initial_delay=0.1, backoff_factor=2.0)(fn)

        with patch("resilience.time.sleep") as mock_sleep:
            result = decorated()

        assert result == "recovered"
        assert fn.call_count == 3
        # Sleep called twice: after attempt 1 (0.1 s) and after attempt 2 (0.2 s)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_has_calls([call(0.1), call(0.2)])

    def test_raises_after_exhausting_retries(self):
        """After max_retries failures, the last exception is re-raised."""
        fn = MagicMock(side_effect=OSError("permanent failure"))
        decorated = retry_with_backoff(max_retries=3, initial_delay=0.1)(fn)

        with patch("resilience.time.sleep"):
            with pytest.raises(OSError, match="permanent failure"):
                decorated()

        assert fn.call_count == 3

    def test_no_retry_on_non_matching_exception(self):
        """Exceptions not in the exceptions tuple propagate immediately."""
        fn = MagicMock(side_effect=ValueError("wrong type"))
        decorated = retry_with_backoff(max_retries=3, initial_delay=0.1, exceptions=(OSError,))(fn)

        with patch("resilience.time.sleep") as mock_sleep:
            with pytest.raises(ValueError, match="wrong type"):
                decorated()

        fn.assert_called_once()  # no retry
        mock_sleep.assert_not_called()

    def test_max_retries_one_means_no_retry(self):
        """max_retries=1 means a single attempt — failure raises immediately."""
        fn = MagicMock(side_effect=OSError("fail"))
        decorated = retry_with_backoff(max_retries=1, initial_delay=0.1)(fn)

        with patch("resilience.time.sleep") as mock_sleep:
            with pytest.raises(OSError):
                decorated()

        fn.assert_called_once()
        mock_sleep.assert_not_called()

    def test_backoff_sequence_is_exponential(self):
        """Verify sleep durations follow the exponential backoff sequence."""
        fn = MagicMock(side_effect=OSError("fail"))
        decorated = retry_with_backoff(
            max_retries=4, initial_delay=0.1, backoff_factor=3.0,
        )(fn)

        with patch("resilience.time.sleep") as mock_sleep:
            with pytest.raises(OSError):
                decorated()

        # 3 sleeps: 0.1, 0.3, 0.9
        delays = [c.args[0] for c in mock_sleep.call_args_list]
        assert delays == pytest.approx([0.1, 0.3, 0.9])

    def test_preserves_function_name_and_docstring(self):
        """@retry_with_backoff preserves the wrapped function's metadata."""
        def my_func():
            """My docstring."""

        decorated = retry_with_backoff()(my_func)
        assert decorated.__name__ == "my_func"
        assert decorated.__doc__ == "My docstring."


# ── Tuning parameter guard-rails ─────────────────────────────────────────────

class TestRetryParameterValidation:

    def test_max_retries_zero_raises(self):
        with pytest.raises(ValueError, match="max_retries"):
            retry_with_backoff(max_retries=0)(lambda: None)

    def test_negative_max_retries_raises(self):
        with pytest.raises(ValueError, match="max_retries"):
            retry_with_backoff(max_retries=-1)(lambda: None)

    def test_negative_initial_delay_raises(self):
        with pytest.raises(ValueError, match="initial_delay"):
            retry_with_backoff(initial_delay=-0.1)(lambda: None)

    def test_backoff_factor_below_one_raises(self):
        with pytest.raises(ValueError, match="backoff_factor"):
            retry_with_backoff(backoff_factor=0.5)(lambda: None)


# ── Integration: save_books retries on transient OSError ─────────────────────

class TestSaveBooksResilience:
    """save_books() is decorated with @retry_with_backoff(max_retries=3).
    Simulate transient disk failures via monkeypatch.
    """

    @pytest.fixture(autouse=True)
    def use_temp_data_file(self, tmp_path, monkeypatch):
        temp_file = tmp_path / "data.json"
        temp_file.write_text("[]")
        monkeypatch.setattr(books, "DATA_FILE", str(temp_file))

    def test_save_succeeds_after_one_transient_oserror(self, monkeypatch):
        """save_books() recovers when the first write fails with OSError."""
        collection = BookCollection()
        collection.add_book("Dune", "Frank Herbert", 1965)

        call_count = {"n": 0}
        original_open = open

        def flaky_open(path, mode="r", *args, **kwargs):
            if mode == "w":
                call_count["n"] += 1
                if call_count["n"] == 1:
                    raise OSError("simulated disk blip")
            return original_open(path, mode, *args, **kwargs)

        with patch("resilience.time.sleep"):  # suppress real sleeps
            with patch("builtins.open", side_effect=flaky_open):
                # Should not raise — retries past the first failure
                collection.save_books()

        assert call_count["n"] == 2  # failed once, succeeded on second attempt

    def test_save_raises_after_three_oserrors(self, monkeypatch):
        """save_books() re-raises OSError after exhausting all 3 attempts."""
        collection = BookCollection()
        collection.add_book("Dune", "Frank Herbert", 1965)

        original_open = open

        def always_fail_on_write(path, mode="r", *args, **kwargs):
            if mode == "w":
                raise OSError("permanent disk failure")
            return original_open(path, mode, *args, **kwargs)

        with patch("resilience.time.sleep"):
            with patch("builtins.open", side_effect=always_fail_on_write):
                with pytest.raises(OSError, match="permanent disk failure"):
                    collection.save_books()

    def test_sleep_called_between_save_retries(self):
        """Verify backoff sleeps are triggered between save_books retry attempts."""
        collection = BookCollection()

        original_open = open
        fail_count = {"n": 0}

        def fail_twice_on_write(path, mode="r", *args, **kwargs):
            if mode == "w":
                fail_count["n"] += 1
                if fail_count["n"] <= 2:
                    raise OSError("transient")
            return original_open(path, mode, *args, **kwargs)

        with patch("resilience.time.sleep") as mock_sleep:
            with patch("builtins.open", side_effect=fail_twice_on_write):
                collection.save_books()  # fails twice, succeeds on 3rd

        assert mock_sleep.call_count == 2  # one sleep per failed attempt


# ── Deadline parameter ────────────────────────────────────────────────────────

class TestDeadlineParameter:
    """deadline= raises TimeoutError when wall time is exhausted before retries finish."""

    def test_deadline_exceeded_raises_timeout_error(self, monkeypatch):
        """When elapsed >= deadline after a failure, TimeoutError is raised."""
        # Simulate time advancing 6 s on the first failure (> deadline=5.0)
        monotonic_values = iter([0.0, 6.0])
        monkeypatch.setattr("resilience.time.monotonic", lambda: next(monotonic_values))

        fn = MagicMock(side_effect=OSError("disk error"))
        decorated = retry_with_backoff(
            max_retries=3, initial_delay=0.1, deadline=5.0, exceptions=(OSError,)
        )(fn)

        with patch("resilience.time.sleep"):
            with pytest.raises(TimeoutError, match="Deadline of 5.0s exceeded"):
                decorated()

        fn.assert_called_once()  # stopped after first attempt

    def test_deadline_not_exceeded_allows_retry(self, monkeypatch):
        """When elapsed < deadline, retries continue as normal."""
        # Simulate time advancing only 0.1 s per attempt (well under deadline=5.0)
        monotonic_seq = iter([0.0, 0.1, 0.2, 0.3])
        monkeypatch.setattr("resilience.time.monotonic", lambda: next(monotonic_seq))

        fn = MagicMock(side_effect=[OSError("transient"), OSError("transient"), "ok"])
        decorated = retry_with_backoff(
            max_retries=3, initial_delay=0.01, deadline=5.0, exceptions=(OSError,)
        )(fn)

        with patch("resilience.time.sleep"):
            result = decorated()

        assert result == "ok"
        assert fn.call_count == 3

    def test_deadline_zero_or_negative_raises_value_error(self):
        """deadline <= 0 is rejected at decoration time with ValueError."""
        with pytest.raises(ValueError, match="deadline"):
            retry_with_backoff(deadline=0.0)(lambda: None)

        with pytest.raises(ValueError, match="deadline"):
            retry_with_backoff(deadline=-1.0)(lambda: None)

    def test_deadline_none_means_no_time_limit(self, monkeypatch):
        """deadline=None (default) never raises TimeoutError regardless of elapsed time."""
        # Simulate very large elapsed time — should not trigger deadline logic
        monotonic_values = iter([0.0, 9999.0])
        monkeypatch.setattr("resilience.time.monotonic", lambda: next(monotonic_values))

        fn = MagicMock(side_effect=[OSError("slow"), "ok"])
        decorated = retry_with_backoff(
            max_retries=2, initial_delay=0.0, deadline=None, exceptions=(OSError,)
        )(fn)

        with patch("resilience.time.sleep"):
            result = decorated()

        assert result == "ok"


# ── Integration: load_books retries on transient PermissionError ──────────────

class TestLoadBooksResilience:
    """load_books() is now decorated with @retry_with_backoff(exceptions=(OSError,)).

    PermissionError (a subclass of OSError) escapes the inner try/except inside
    load_books and is caught by the decorator. FileNotFoundError and
    JSONDecodeError are handled INSIDE load_books and never reach the decorator.
    """

    @pytest.fixture(autouse=True)
    def use_temp_data_file(self, tmp_path, monkeypatch):
        temp_file = tmp_path / "data.json"
        temp_file.write_text("[]")
        monkeypatch.setattr(books, "DATA_FILE", str(temp_file))
        return temp_file

    def test_load_succeeds_after_one_transient_permission_error(self, monkeypatch):
        """load_books() retries and recovers from a single transient PermissionError."""
        call_count = {"n": 0}
        original_open = open

        def flaky_open(path, mode="r", *args, **kwargs):
            # Raise PermissionError on the first open() attempt during load
            if "data.json" in str(path) and mode == "r":
                call_count["n"] += 1
                if call_count["n"] == 1:
                    raise PermissionError("NFS lock")
            return original_open(path, mode, *args, **kwargs)

        with patch("resilience.time.sleep"):
            with patch("builtins.open", side_effect=flaky_open):
                col = BookCollection()

        assert col.books == []  # empty data file, loaded successfully on retry

    def test_load_raises_after_exhausting_retries(self, monkeypatch):
        """load_books() re-raises OSError after exhausting all retries."""
        original_open = open

        def always_permission_error(path, mode="r", *args, **kwargs):
            if "data.json" in str(path) and mode == "r":
                raise PermissionError("permanent lock")
            return original_open(path, mode, *args, **kwargs)

        with patch("resilience.time.sleep"):
            with patch("builtins.open", side_effect=always_permission_error):
                with pytest.raises(PermissionError, match="permanent lock"):
                    BookCollection()

    def test_file_not_found_still_gives_empty_collection(self, monkeypatch):
        """FileNotFoundError is handled INSIDE load_books — not retried by decorator.

        This confirms the two-layer design: inner handler deals with expected absence,
        outer decorator deals with transient I/O failures.
        """
        monkeypatch.setattr(books, "DATA_FILE", "/nonexistent/path/data.json")
        with patch("resilience.time.sleep") as mock_sleep:
            col = BookCollection()

        assert col.books == []
        mock_sleep.assert_not_called()  # no retry occurred

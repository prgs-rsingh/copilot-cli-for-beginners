"""Security hygiene tests for books.py.

Covers three fixes applied in Run-08:
  Fix 1 — Atomic write: save_books() writes to .tmp then os.replace()
  Fix 3 — Strict deserialization: load_books() rejects unexpected/missing fields

Each test documents the specific risk being guarded and the rollback path.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

import pytest

import books
from books import BookCollection


@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    """Redirect DATA_FILE to an isolated temp file for every test."""
    data_file = tmp_path / "data.json"
    data_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))
    return data_file


# ---------------------------------------------------------------------------
# Fix 1 — Atomic write
# ---------------------------------------------------------------------------

class TestAtomicWrite:
    def test_no_tmp_file_after_successful_save(self):
        """Security/Safety: .tmp file must not remain after a successful save_books().

        Rationale: if os.replace() succeeds, the temp file is the real file.
        A leftover .tmp would indicate a failed rename and confuse future reads.
        Rollback: restore open(DATA_FILE, 'w') direct write in save_books().
        """
        col = BookCollection()
        col.add_book("Dune", "Frank Herbert", 1965)

        tmp_path = books.DATA_FILE + ".tmp"
        assert not os.path.exists(tmp_path), (
            f".tmp file should not exist after a successful save; found: {tmp_path}"
        )

    def test_data_file_correct_after_atomic_write(self, temp_data):
        """Safety: data.json contains correct data after the atomic rename."""
        col = BookCollection()
        col.add_book("Foundation", "Isaac Asimov", 1951)

        records = json.loads(temp_data.read_text())
        assert len(records) == 1
        assert records[0]["title"] == "Foundation"

    def test_atomic_write_survives_retry(self, temp_data, monkeypatch):
        """Safety: if the first write attempt fails, retry still leaves data intact.

        Simulate one OSError on open() then let it succeed on the second attempt.
        Rollback: remove @retry_with_backoff from save_books().
        """
        call_count = {"n": 0}
        real_open = open

        def flaky_open(path, mode="r", **kwargs):
            if mode == "w" and call_count["n"] == 0:
                call_count["n"] += 1
                raise OSError("Simulated transient write failure")
            return real_open(path, mode, **kwargs)

        monkeypatch.setattr("builtins.open", flaky_open)

        col = BookCollection()
        # Manually append so we bypass the add_book() save path already patched
        col.books.append(books.Book("Dune", "Frank Herbert", 1965))
        col.save_books()  # first call fails → retry → succeeds

        records = json.loads(temp_data.read_text())
        assert len(records) == 1
        assert records[0]["title"] == "Dune"


# ---------------------------------------------------------------------------
# Fix 3 — Strict deserialization
# ---------------------------------------------------------------------------

class TestStrictDeserialization:
    def test_record_with_extra_field_skipped_with_warning(self, temp_data, capsys):
        """Security: records with unexpected JSON keys are skipped, not crashed on.

        Rationale: Book(**b) raises TypeError on unexpected keys. An attacker or
        corrupted file could inject extra fields to cause an unhandled crash.
        Rollback: replace per-record validation loop with [Book(**b) for b in data].
        """
        temp_data.write_text(json.dumps([
            {"title": "Dune", "author": "Frank Herbert", "year": 1965, "read": False,
             "injected_field": "malicious"},
        ]))
        col = BookCollection()
        assert col.books == [], "Record with unexpected field must be skipped"
        assert "unexpected field" in capsys.readouterr().out

    def test_record_missing_required_field_skipped_with_warning(self, temp_data, capsys):
        """Security: records missing required fields are skipped gracefully.

        Rationale: missing 'year' causes TypeError at Book construction time.
        Rollback: remove the _BOOK_REQUIRED_FIELDS.issubset() check.
        """
        temp_data.write_text(json.dumps([
            {"title": "Dune", "author": "Frank Herbert"},  # missing 'year'
        ]))
        col = BookCollection()
        assert col.books == [], "Record missing required field must be skipped"
        assert "missing required field" in capsys.readouterr().out

    def test_non_dict_record_skipped_with_warning(self, temp_data, capsys):
        """Security: non-dict elements in the JSON array are skipped, not crashed on.

        Rationale: JSON arrays can contain any value type. A string or int element
        would cause 'TypeError: argument of type str is not iterable' in the validator.
        Rollback: remove the isinstance(record, dict) guard.
        """
        temp_data.write_text(json.dumps(["not_a_dict", 42, None]))
        col = BookCollection()
        assert col.books == [], "Non-dict records must all be skipped"
        out = capsys.readouterr().out
        assert "non-dict" in out

    def test_valid_record_still_loads_correctly(self, temp_data):
        """Regression: validation must not break loading of well-formed records."""
        temp_data.write_text(json.dumps([
            {"title": "Dune", "author": "Frank Herbert", "year": 1965, "read": True},
            {"title": "Foundation", "author": "Isaac Asimov", "year": 1951, "read": False},
        ]))
        col = BookCollection()
        assert len(col.books) == 2
        assert col.books[0].title == "Dune"
        assert col.books[1].read is False

    def test_mixed_valid_and_invalid_records(self, temp_data):
        """Safety: valid records are loaded even when some records are malformed."""
        temp_data.write_text(json.dumps([
            {"title": "Dune", "author": "Frank Herbert", "year": 1965, "read": False},
            {"title": "Bad", "author": "X", "year": 2000, "extra": "oops"},
            {"title": "Foundation", "author": "Isaac Asimov", "year": 1951, "read": False},
        ]))
        col = BookCollection()
        assert len(col.books) == 2, "Only valid records should be loaded"
        titles = [b.title for b in col.books]
        assert "Dune" in titles
        assert "Foundation" in titles
        assert "Bad" not in titles

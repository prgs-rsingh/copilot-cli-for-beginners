import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pytest
import books
from books import BookCollection

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
GOLDEN_BOOK_FILE = os.path.join(FIXTURES_DIR, "golden_book.json")

# Authoritative schema for a single book record in data.json.
# Update this dict (and golden_book.json) whenever the Book dataclass fields change.
BOOK_SCHEMA = {
    "title": str,
    "author": str,
    "year": int,
    "read": bool,
}


@pytest.fixture()
def temp_data(tmp_path, monkeypatch):
    """Redirect DATA_FILE to an isolated temp file and return its path."""
    data_file = tmp_path / "data.json"
    data_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))
    return data_file


def assert_book_record_schema(record: dict) -> None:
    """Assert one book record has exactly the expected keys and value types."""
    assert set(record.keys()) == set(BOOK_SCHEMA.keys()), (
        f"Schema mismatch: expected {set(BOOK_SCHEMA.keys())}, got {set(record.keys())}"
    )
    for field, expected_type in BOOK_SCHEMA.items():
        assert isinstance(record[field], expected_type), (
            f"Field '{field}': expected {expected_type.__name__}, "
            f"got {type(record[field]).__name__} (value={record[field]!r})"
        )


# ---------------------------------------------------------------------------
# Contract test 1 — Schema shape
# ---------------------------------------------------------------------------
def test_save_books_schema_shape(temp_data):
    """Contract: save_books() writes a JSON array; every record matches BOOK_SCHEMA."""
    collection = BookCollection()
    collection.add_book("The Pragmatic Programmer", "Dave Thomas", 1999)
    collection.add_book("Clean Code", "Robert Martin", 2008)

    records = json.loads(temp_data.read_text())

    assert isinstance(records, list), "Persisted data must be a JSON array"
    assert len(records) == 2
    for record in records:
        assert_book_record_schema(record)


# ---------------------------------------------------------------------------
# Contract test 2 — Field values preserved
# ---------------------------------------------------------------------------
def test_save_books_field_values(temp_data):
    """Contract: save_books() preserves exact field values including read flag."""
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.mark_as_read("Dune")

    records = json.loads(temp_data.read_text())

    assert len(records) == 1
    r = records[0]
    assert r["title"] == "Dune"
    assert r["author"] == "Frank Herbert"
    assert r["year"] == 1965
    assert r["read"] is True


# ---------------------------------------------------------------------------
# Contract test 3 — Round-trip serialization
# ---------------------------------------------------------------------------
def test_round_trip_serialization(temp_data):
    """Contract: a Book written by save_books() and read by a fresh load_books() is identical."""
    writer = BookCollection()
    writer.add_book("Neuromancer", "William Gibson", 1984)
    writer.mark_as_read("Neuromancer")

    reader = BookCollection()  # loads from the same temp_data file
    assert len(reader.books) == 1
    b = reader.books[0]
    assert b.title == "Neuromancer"
    assert b.author == "William Gibson"
    assert b.year == 1984
    assert b.read is True


# ---------------------------------------------------------------------------
# Contract test 4 — Golden file schema guard
# Golden file: tests/fixtures/golden_book.json
# Update it intentionally when the Book schema changes (see CONTRIBUTING.md).
# ---------------------------------------------------------------------------
def test_golden_book_schema():
    """Contract: golden fixture conforms to BOOK_SCHEMA (guards against accidental field renames)."""
    assert os.path.isfile(GOLDEN_BOOK_FILE), (
        f"Golden file missing: {GOLDEN_BOOK_FILE}\n"
        "Re-generate it by running: python -c \"import json,books; "
        "c=books.BookCollection(); print(json.dumps([{'title':'...','author':'...','year':1999,'read':False}], indent=2))\""
    )
    with open(GOLDEN_BOOK_FILE) as f:
        records = json.load(f)

    assert isinstance(records, list)
    assert len(records) >= 1, "Golden file must contain at least one record"
    for record in records:
        assert_book_record_schema(record)

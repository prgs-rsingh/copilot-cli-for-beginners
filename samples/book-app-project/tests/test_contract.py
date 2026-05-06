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


# ---------------------------------------------------------------------------
# Sweep — TODOs and edge cases identified (Run-05)
#
# Finding 1 (HIGH):   remove_book() returns bool but disk state was never verified
#                     → test_remove_book_round_trip
# Finding 2 (MEDIUM): add_book() return type (Book) never asserted in contract context
#                     → test_add_book_return_type
# Finding 3 (MEDIUM): find_by_author() return type and empty-list branch not guarded
#                     → test_find_by_author_contract
# Finding 4 (MEDIUM): case-insensitive matching implicit but not contractually pinned
#                     → test_case_insensitive_lookup_contract
# Finding 5 (LOW):    save_books() on empty collection not tested
#                     → test_empty_collection_persistence
#
# Update process for future boundary changes:
#   1. Change the Book dataclass field or BookCollection method signature.
#   2. Update BOOK_SCHEMA above to match the new shape.
#   3. Regenerate tests/fixtures/golden_book.json with the new shape.
#   4. Run pytest tests/test_contract.py to confirm all contract tests pass.
#   5. Update this comment block with any new findings.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Contract test 5 — remove_book() round-trip (Finding 1)
# ---------------------------------------------------------------------------
def test_remove_book_round_trip(temp_data):
    """Contract: after remove_book(), a fresh load sees the book gone from disk.

    Rationale: remove_book() returns bool (success/not-found), but the real
    contract is that the JSON file no longer contains the removed book.  A bug
    in save_books() could return True while leaving stale data on disk.
    """
    collection = BookCollection()
    collection.add_book("Foundation", "Isaac Asimov", 1951)
    collection.add_book("Dune", "Frank Herbert", 1965)

    result = collection.remove_book("Foundation")
    assert result is True, "remove_book() must return True for an existing title"

    records = json.loads(temp_data.read_text())
    titles = [r["title"] for r in records]
    assert "Foundation" not in titles, "Removed book must not appear in persisted JSON"
    assert "Dune" in titles, "Non-removed book must still be in persisted JSON"

    # Reload from disk to confirm the live collection also reflects the removal
    reloaded = BookCollection()
    assert reloaded.find_book_by_title("Foundation") is None
    assert reloaded.find_book_by_title("Dune") is not None


# ---------------------------------------------------------------------------
# Contract test 6 — add_book() return type (Finding 2)
# ---------------------------------------------------------------------------
def test_add_book_return_type(temp_data):
    """Contract: add_book() returns a Book object with the correct field values.

    Rationale: callers (present and future) may use the returned Book directly
    rather than re-fetching via find_book_by_title().  The return type is part
    of the public interface contract.
    """
    from books import Book

    collection = BookCollection()
    returned = collection.add_book("Neuromancer", "William Gibson", 1984)

    assert isinstance(returned, Book), (
        f"add_book() must return a Book instance; got {type(returned).__name__}"
    )
    assert returned.title == "Neuromancer"
    assert returned.author == "William Gibson"
    assert returned.year == 1984
    assert returned.read is False, "Newly added book must have read=False"


# ---------------------------------------------------------------------------
# Contract test 7 — find_by_author() return type and empty-list branch (Finding 3)
# ---------------------------------------------------------------------------
def test_find_by_author_contract(temp_data):
    """Contract: find_by_author() returns list[Book]; returns [] when no match.

    Rationale: show_books() in utils.py iterates this return value and accesses
    .title, .author, .year, .read.  If the method returns the wrong type (e.g.
    list[dict]) or raises instead of returning [], the UI layer breaks silently.
    """
    from books import Book

    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("Dune Messiah", "Frank Herbert", 1969)
    collection.add_book("Foundation", "Isaac Asimov", 1951)

    results = collection.find_by_author("Frank Herbert")

    assert isinstance(results, list), "find_by_author() must return a list"
    assert len(results) == 2
    for book in results:
        assert isinstance(book, Book), (
            f"Each item must be a Book instance; got {type(book).__name__}"
        )
        assert book.author == "Frank Herbert"

    empty = collection.find_by_author("Unknown Author")
    assert empty == [], "find_by_author() must return [] when no books match"


# ---------------------------------------------------------------------------
# Contract test 8 — case-insensitive lookup (Finding 4)
# ---------------------------------------------------------------------------
def test_case_insensitive_lookup_contract(temp_data):
    """Contract: find_book_by_title() and find_by_author() match regardless of case.

    Rationale: user input is not normalized before lookup; case sensitivity would
    cause silent failures (book 'not found') that are hard to diagnose.  This
    contract pins the normalization behaviour so a refactor cannot remove it.
    """
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)

    # find_book_by_title — all-caps, all-lower, mixed
    assert collection.find_book_by_title("DUNE") is not None
    assert collection.find_book_by_title("dune") is not None
    assert collection.find_book_by_title("DuNe") is not None

    # find_by_author — all-caps, all-lower
    assert len(collection.find_by_author("FRANK HERBERT")) == 1
    assert len(collection.find_by_author("frank herbert")) == 1


# ---------------------------------------------------------------------------
# Contract test 9 — empty collection persistence (Finding 5)
# ---------------------------------------------------------------------------
def test_empty_collection_persistence(temp_data):
    """Contract: saving an empty collection writes '[]', not an error or missing file.

    Rationale: after the last book is removed, load_books() must be able to read
    the result without raising JSONDecodeError.  An empty file or null would break
    the round-trip.
    """
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.remove_book("Dune")

    raw = temp_data.read_text()
    assert raw.strip() != "", "data.json must not be empty after removing the last book"

    records = json.loads(raw)
    assert records == [], "Persisted JSON for an empty collection must be []"

    reloaded = BookCollection()
    assert reloaded.books == [], "Reloaded collection from [] must have no books"

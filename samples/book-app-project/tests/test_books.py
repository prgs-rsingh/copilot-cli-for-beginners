import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import books
from books import BookCollection


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result is True
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False

def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result is True
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result is False

def test_find_by_author_returns_only_matching_books():
    collection = BookCollection()
    collection.add_book("Foundation", "Isaac Asimov", 1951)
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("I, Robot", "Isaac Asimov", 1950)
    results = collection.find_by_author("Isaac Asimov")
    assert len(results) == 2
    assert all(b.author == "Isaac Asimov" for b in results)

# --- input validation (negative tests) ---

@pytest.mark.parametrize("title,author,year,match", [
    ("",        "Orwell",  1984, "title"),
    ("  ",      "Orwell",  1984, "title"),
    ("1984",    "",        1984, "author"),
    ("1984",    "   ",     1984, "author"),
    ("1984",    "Orwell",  0,    "year"),
    ("1984",    "Orwell", -5,    "year"),
])
def test_add_book_rejects_invalid_input(title, author, year, match):
    """add_book must raise ValueError for blank strings or non-positive year."""
    collection = BookCollection()
    with pytest.raises(ValueError, match=match):
        collection.add_book(title, author, year)
    # collection must remain unmodified
    assert collection.books == []

# --- no_duplicates toggle ---

def test_toggle_off_allows_duplicate_titles():
    """Default (no_duplicates=False): same title can be added more than once."""
    collection = BookCollection()  # toggle OFF
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("Dune", "Frank Herbert", 1965)  # must not raise
    assert len(collection.books) == 2

def test_toggle_on_rejects_duplicate_title():
    """no_duplicates=True: adding a title that already exists raises ValueError."""
    collection = BookCollection(no_duplicates=True)
    collection.add_book("Dune", "Frank Herbert", 1965)
    with pytest.raises(ValueError, match="already exists"):
        collection.add_book("dune", "Someone Else", 2000)  # case-insensitive match
    assert len(collection.books) == 1  # original entry untouched

# --- save_books resilience (retry / error mapping) ---

def test_save_books_raises_ioerror_when_all_retries_fail(monkeypatch, tmp_path):
    """save_books must raise IOError (not OSError) after exhausting all retries."""
    import books as bk

    monkeypatch.setattr(bk, "SAVE_MAX_RETRIES", 1)
    monkeypatch.setattr(bk, "SAVE_RETRY_DELAY_S", 0.0)  # no real sleeping in tests

    # Point DATA_FILE at a path whose parent doesn't exist so every write fails.
    monkeypatch.setattr(bk, "DATA_FILE", str(tmp_path / "no_dir" / "data.json"))

    collection = BookCollection()  # starts empty (FileNotFoundError on missing dir)
    collection.books.append(bk.Book("Dune", "Herbert", 1965))

    with pytest.raises(OSError, match="save_books failed after 2 attempt"):
        collection.save_books()


def test_save_books_succeeds_after_transient_failure(monkeypatch, tmp_path):
    """save_books succeeds if one attempt fails but a subsequent one succeeds."""
    import books as bk

    monkeypatch.setattr(bk, "SAVE_MAX_RETRIES", 2)
    monkeypatch.setattr(bk, "SAVE_RETRY_DELAY_S", 0.0)

    good_path = str(tmp_path / "data.json")
    monkeypatch.setattr(bk, "DATA_FILE", good_path)

    # Patch open() to fail on the first *write* to good_path, then succeed.
    real_open = open
    call_count = {"n": 0}

    def flaky_open(path, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        if path == good_path and "w" in mode and call_count["n"] == 0:
            call_count["n"] += 1
            raise OSError("simulated transient disk error")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", flaky_open)

    collection = BookCollection()
    collection.books.append(bk.Book("Foundation", "Asimov", 1951))
    collection.save_books()  # must not raise

    import json
    saved = json.loads(open(good_path).read())
    assert len(saved) == 1
    assert saved[0]["title"] == "Foundation"

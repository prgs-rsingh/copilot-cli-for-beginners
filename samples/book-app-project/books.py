"""books.py — core domain model for the book collection app.

Public surface:
  Book            – immutable-ish dataclass representing a single book.
  BookCollection  – in-memory collection backed by a JSON file (DATA_FILE).

Persistence is intentionally simple: every mutating operation rewrites the
entire JSON file.  See ai-track-docs/extending-books.md for guidance on
adding new fields or methods.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Optional

# ---------------------------------------------------------------------------
# Structured logger
# Emits one JSON line per mutating operation with fields:
#   op         – operation name (e.g. "add_book")
#   status     – "ok" | "not_found" | "error"
#   elapsed_ms – wall-clock time for the operation in milliseconds
#   title      – book title involved (when applicable)
#
# Control verbosity with the BOOK_APP_LOG_LEVEL env var (default: WARNING).
# Set to DEBUG or INFO to see mutation logs:
#   BOOK_APP_LOG_LEVEL=INFO python book_app.py add
# ---------------------------------------------------------------------------
_log = logging.getLogger("book_app")

if not _log.handlers:
    _handler = logging.StreamHandler()  # writes to stderr, not stdout
    _handler.setFormatter(logging.Formatter("%(message)s"))
    _log.addHandler(_handler)

_log.setLevel(os.environ.get("BOOK_APP_LOG_LEVEL", "WARNING").upper())


def _log_op(op: str, status: str, elapsed_ms: float, **extra) -> None:
    """Emit a single structured JSON log line to stderr."""
    record = {"op": op, "status": status, "elapsed_ms": round(elapsed_ms, 2)}
    record.update(extra)
    _log.info(json.dumps(record))


# Path to the JSON file used for persistence.  Tests override this via
# monkeypatch so they never touch the real file.
DATA_FILE = "data.json"


@dataclass
class Book:
    """A single book entry.

    Attributes:
        title:  Book title (used as the primary lookup key, case-insensitive).
        author: Author full name.
        year:   Publication year.
        read:   Whether the user has marked this book as read.
    """
    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:
    """In-memory list of Book objects, automatically persisted to DATA_FILE.

    Args:
        no_duplicates: When True, add_book raises ValueError if a book with
                       the same title (case-insensitive) already exists.
                       Default is False (current behaviour: duplicates allowed).
    """

    def __init__(self, no_duplicates: bool = False):
        # Feature toggle: reject duplicate titles when True.
        self.no_duplicates = no_duplicates
        self.books: List[Book] = []
        self.load_books()

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")
            self.books = []

    def save_books(self):
        """Save the current book collection to JSON."""
        with open(DATA_FILE, "w") as f:
            json.dump([asdict(b) for b in self.books], f, indent=2)

    def add_book(self, title: str, author: str, year: int) -> Book:
        """Create a new Book, append it to the collection, and persist.

        Raises:
            ValueError: if title or author are blank, or year is not a
                        positive integer, or (when no_duplicates=True) a book
                        with the same title already exists.
        """
        if not title or not title.strip():
            raise ValueError("title must not be blank")
        if not author or not author.strip():
            raise ValueError("author must not be blank")
        if not isinstance(year, int) or year <= 0:
            raise ValueError("year must be a positive integer")
        # Toggle: duplicate-title guard (OFF by default).
        if self.no_duplicates and self.find_book_by_title(title) is not None:
            raise ValueError(f"a book titled '{title}' already exists")
        _t = time.perf_counter()
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self.save_books()
        _log_op("add_book", "ok", (time.perf_counter() - _t) * 1000, title=title, author=author, year=year)
        return book

    def list_books(self) -> List[Book]:
        """Return all books in insertion order."""
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        """Return the first book whose title matches *title* (case-insensitive).

        Returns None if no match is found.  All mutating helpers delegate
        to this method so lookup logic lives in exactly one place.
        """
        # next() with a default avoids an explicit loop and communicates
        # "find one or nothing" at a glance.
        return next((b for b in self.books if b.title.lower() == title.lower()), None)

    def mark_as_read(self, title: str) -> bool:
        """Mark a book as read.  Returns True on success, False if not found."""
        _t = time.perf_counter()
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            _log_op("mark_as_read", "ok", (time.perf_counter() - _t) * 1000, title=title)
            return True
        _log_op("mark_as_read", "not_found", (time.perf_counter() - _t) * 1000, title=title)
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book by title.  Returns True on success, False if not found."""
        _t = time.perf_counter()
        book = self.find_book_by_title(title)
        if book:
            self.books.remove(book)
            self.save_books()
            _log_op("remove_book", "ok", (time.perf_counter() - _t) * 1000, title=title)
            return True
        _log_op("remove_book", "not_found", (time.perf_counter() - _t) * 1000, title=title)
        return False

    def find_by_author(self, author: str) -> List[Book]:
        """Return all books whose author matches *author* (case-insensitive)."""
        return [b for b in self.books if b.author.lower() == author.lower()]

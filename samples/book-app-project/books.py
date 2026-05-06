"""Core domain module: Book dataclass and BookCollection persistence."""

import json
import os
from dataclasses import asdict, dataclass

from logging_config import get_logger
from resilience import retry_with_backoff

DATA_FILE = "data.json"

# Schema constants used in load_books() to validate each JSON record before
# constructing a Book. Prevents unhandled TypeError on malformed/tampered data.
# Update both sets whenever Book fields change (also update BOOK_SCHEMA in test_contract.py).
_BOOK_REQUIRED_FIELDS = frozenset({"title", "author", "year"})
_BOOK_ALLOWED_FIELDS = frozenset({"title", "author", "year", "read"})

logger = get_logger(__name__)


@dataclass
class Book:  # noqa: D101 -- dataclass fields are self-documenting; no library API contract
    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:  # noqa: D101 -- public interface documented in README and architecture.md
    def __init__(self) -> None:  # noqa: D107
        self.books: list[Book] = []
        self.load_books()

    def load_books(self) -> None:
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE) as f:  # noqa: PTH123 -- pathlib migration is a separate backlog item (backlog.md item 1)
                data = json.load(f)
                validated = []
                for record in data:
                    if not isinstance(record, dict):
                        print("Warning: skipping non-dict record in data.json")  # noqa: T201
                        continue
                    unexpected = set(record.keys()) - _BOOK_ALLOWED_FIELDS
                    if unexpected:
                        print(f"Warning: skipping record with unexpected field(s) {sorted(unexpected)} in data.json")  # noqa: T201
                        continue
                    if not _BOOK_REQUIRED_FIELDS.issubset(record.keys()):
                        missing = _BOOK_REQUIRED_FIELDS - set(record.keys())
                        print(f"Warning: skipping record missing required field(s) {sorted(missing)} in data.json")  # noqa: T201
                        continue
                    validated.append(Book(**record))
                self.books = validated
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")  # noqa: T201 -- intentional user-facing warning; must reach stdout
            self.books = []
        logger.info(
            "collection.loaded",
            extra={"count": len(self.books), "data_file": DATA_FILE},
        )

    # Retry parameters: 3 attempts, 50 ms → 100 ms backoff (total worst-case wait: 150 ms).
    # Handles transient OSError (disk full, network filesystem blip, permission flush delay).
    # Rollback: remove the @retry_with_backoff line; save_books works without it.
    @retry_with_backoff(max_retries=3, initial_delay=0.05, backoff_factor=2.0, exceptions=(OSError,))
    def save_books(self) -> None:
        """Save the current book collection to JSON (atomic write via temp file).

        Writes to DATA_FILE + '.tmp' first, then renames atomically with os.replace().
        This prevents partial-write corruption if the process is interrupted mid-write.
        Rollback: replace tmp_path pattern with open(DATA_FILE, 'w') directly.
        """
        tmp_path = DATA_FILE + ".tmp"
        with open(tmp_path, "w") as f:  # noqa: PTH123 -- pathlib migration is a separate backlog item (backlog.md item 1)
            json.dump([asdict(b) for b in self.books], f, indent=2)
        os.replace(tmp_path, DATA_FILE)  # atomic on POSIX; best-effort on Windows

    def add_book(self, title: str, author: str, year: int) -> Book:  # noqa: D102
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self.save_books()
        logger.info(
            "collection.add",
            extra={
                "title": title,
                "author": author,
                "year": year,
                "result": "success",
                "collection_size": len(self.books),
            },
        )
        return book

    def list_books(self) -> list[Book]:  # noqa: D102
        return self.books

    def find_book_by_title(self, title: str) -> Book | None:  # noqa: D102
        title_lower = title.lower()
        for book in self.books:
            if book.title.lower() == title_lower:
                return book
        return None

    def mark_as_read(self, title: str) -> bool:  # noqa: D102
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            logger.info(
                "collection.mark_read",
                extra={"title": title, "result": "success"},
            )
            return True
        logger.info(
            "collection.mark_read",
            extra={"title": title, "result": "not_found"},
        )
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book by title."""
        book = self.find_book_by_title(title)
        if book:
            self.books.remove(book)
            self.save_books()
            logger.info(
                "collection.remove",
                extra={"title": title, "result": "success", "collection_size": len(self.books)},
            )
            return True
        logger.info(
            "collection.remove",
            extra={"title": title, "result": "not_found"},
        )
        return False

    def find_by_author(self, author: str) -> list[Book]:
        """Find all books by a given author."""
        author_lower = author.lower()
        return [b for b in self.books if b.author.lower() == author_lower]

"""Core domain module: Book dataclass and BookCollection persistence."""

import json
from dataclasses import asdict, dataclass

from logging_config import get_logger

DATA_FILE = "data.json"

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
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")  # noqa: T201 -- intentional user-facing warning; must reach stdout
            self.books = []
        logger.info(
            "collection.loaded",
            extra={"count": len(self.books), "data_file": DATA_FILE},
        )

    def save_books(self) -> None:
        """Save the current book collection to JSON."""
        with open(DATA_FILE, "w") as f:  # noqa: PTH123 -- pathlib migration is a separate backlog item (backlog.md item 1)
            json.dump([asdict(b) for b in self.books], f, indent=2)

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

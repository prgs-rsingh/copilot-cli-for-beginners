"""Tests for utils.py — covers print_menu, get_user_choice, get_book_details, show_books.

All tests are deterministic:
- print/output functions verified via pytest capsys
- input() calls patched with monkeypatch to avoid interactive prompts
- No real I/O occurs in any test
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from utils import get_book_details, get_user_choice, print_menu, show_books


# ── print_menu ────────────────────────────────────────────────────────────────

class TestPrintMenu:
    def test_contains_app_title(self, capsys):
        print_menu()
        out = capsys.readouterr().out
        assert "Book Collection App" in out

    def test_contains_all_five_options(self, capsys):
        print_menu()
        out = capsys.readouterr().out
        for option in ("1.", "2.", "3.", "4.", "5."):
            assert option in out

    def test_contains_exit_option(self, capsys):
        print_menu()
        out = capsys.readouterr().out
        assert "Exit" in out


# ── get_user_choice ───────────────────────────────────────────────────────────

class TestGetUserChoice:
    def test_returns_stripped_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "  3  ")
        assert get_user_choice() == "3"

    def test_returns_exact_choice(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "1")
        assert get_user_choice() == "1"


# ── get_book_details ──────────────────────────────────────────────────────────

class TestGetBookDetails:
    def test_valid_inputs(self, monkeypatch):
        """Three successive inputs: title, author, year."""
        responses = iter(["Dune", "Frank Herbert", "1965"])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        title, author, year = get_book_details()
        assert title == "Dune"
        assert author == "Frank Herbert"
        assert year == 1965

    def test_blank_year_returns_zero(self, monkeypatch):
        """Blank year input produces year=0 (parse_year returns 0 for blank)."""
        responses = iter(["1984", "George Orwell", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        _, _, year = get_book_details()
        assert year == 0

    def test_non_numeric_year_defaults_to_zero(self, monkeypatch, capsys):
        """Non-numeric year triggers ValueError → prints warning, returns year=0."""
        responses = iter(["The Hobbit", "Tolkien", "abc"])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        _, _, year = get_book_details()
        assert year == 0
        out = capsys.readouterr().out
        assert "Invalid year" in out

    def test_strips_whitespace_from_title_and_author(self, monkeypatch):
        responses = iter(["  Dune  ", "  Frank Herbert  ", "1965"])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        title, author, _ = get_book_details()
        assert title == "Dune"
        assert author == "Frank Herbert"

    def test_strict_year_invalid_when_flag_on(self, monkeypatch):
        """With BOOK_APP_STRICT_YEAR=1, an out-of-range year falls back to 0."""
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        responses = iter(["Book", "Author", "9999"])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        _, _, year = get_book_details()
        assert year == 0


# ── show_books ────────────────────────────────────────────────────────────────

class TestShowBooks:
    def test_empty_list_prints_no_books(self, capsys):
        show_books([])
        out = capsys.readouterr().out
        assert "No books found." in out

    def test_empty_list_does_not_print_collection_header(self, capsys):
        show_books([])
        out = capsys.readouterr().out
        assert "Your Book Collection" not in out

    def test_populated_list_shows_header(self, capsys):
        book = SimpleNamespace(title="Dune", author="Frank Herbert", year=1965, read=False)
        show_books([book])
        out = capsys.readouterr().out
        assert "Your Book Collection" in out

    def test_unread_book_shows_empty_checkbox(self, capsys):
        book = SimpleNamespace(title="Dune", author="Frank Herbert", year=1965, read=False)
        show_books([book])
        out = capsys.readouterr().out
        assert "[ ]" in out

    def test_read_book_shows_checkmark(self, capsys):
        book = SimpleNamespace(title="Dune", author="Frank Herbert", year=1965, read=True)
        show_books([book])
        out = capsys.readouterr().out
        assert "[✓]" in out

    def test_shows_title_author_and_year(self, capsys):
        book = SimpleNamespace(title="Dune", author="Frank Herbert", year=1965, read=False)
        show_books([book])
        out = capsys.readouterr().out
        assert "Dune" in out
        assert "Frank Herbert" in out
        assert "1965" in out

    def test_multiple_books_numbered(self, capsys):
        books = [
            SimpleNamespace(title="Dune", author="Frank Herbert", year=1965, read=True),
            SimpleNamespace(title="1984", author="George Orwell", year=1949, read=False),
        ]
        show_books(books)
        out = capsys.readouterr().out
        assert "1." in out
        assert "2." in out
        assert "[✓]" in out
        assert "[ ]" in out

    def test_mixed_read_status(self, capsys):
        books = [
            SimpleNamespace(title="A", author="X", year=2000, read=True),
            SimpleNamespace(title="B", author="Y", year=2001, read=False),
        ]
        show_books(books)
        out = capsys.readouterr().out
        assert out.count("[✓]") == 1
        assert out.count("[ ]") == 1

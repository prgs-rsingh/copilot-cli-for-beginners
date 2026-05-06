"""Tests for book_app.py handlers.

All tests monkeypatch:
  - `book_app.prompt` to control user input without real I/O
  - `book_app.collection` to use an in-memory BookCollection backed by a temp file

book_app.py is the CLI entry point (0% coverage before this PR).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import books
import book_app
import pytest


@pytest.fixture(autouse=True)
def fresh_collection(tmp_path, monkeypatch):
    """Replace the global collection with a temp-file-backed BookCollection."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))
    monkeypatch.setattr(book_app, "collection", books.BookCollection())


# ── handle_list ───────────────────────────────────────────────────────────────

class TestHandleList:
    def test_empty_collection_prints_no_books(self, capsys):
        book_app.handle_list()
        assert "No books found." in capsys.readouterr().out

    def test_shows_added_book(self, capsys):
        book_app.collection.add_book("Dune", "Frank Herbert", 1965)
        book_app.handle_list()
        assert "Dune" in capsys.readouterr().out


# ── handle_add ────────────────────────────────────────────────────────────────

class TestHandleAdd:
    def test_adds_book_successfully(self, monkeypatch, capsys):
        responses = iter(["Dune", "Frank Herbert", "1965"])
        monkeypatch.setattr(book_app, "prompt", lambda _: next(responses))
        book_app.handle_add()
        assert "added successfully" in capsys.readouterr().out
        assert book_app.collection.find_book_by_title("Dune") is not None

    def test_invalid_year_with_strict_flag_shows_error(self, monkeypatch, capsys):
        monkeypatch.setenv("BOOK_APP_STRICT_YEAR", "1")
        responses = iter(["Future Book", "Author", "9999"])
        monkeypatch.setattr(book_app, "prompt", lambda _: next(responses))
        book_app.handle_add()
        out = capsys.readouterr().out
        assert "Error" in out

    def test_non_numeric_year_shows_error(self, monkeypatch, capsys):
        responses = iter(["Bad Book", "Author", "notayear"])
        monkeypatch.setattr(book_app, "prompt", lambda _: next(responses))
        book_app.handle_add()
        out = capsys.readouterr().out
        assert "Error" in out


# ── handle_remove ─────────────────────────────────────────────────────────────

class TestHandleRemove:
    def test_removes_existing_book(self, monkeypatch, capsys):
        book_app.collection.add_book("Dune", "Frank Herbert", 1965)
        monkeypatch.setattr(book_app, "prompt", lambda _: "Dune")
        book_app.handle_remove()
        assert book_app.collection.find_book_by_title("Dune") is None

    def test_remove_nonexistent_book_does_not_crash(self, monkeypatch, capsys):
        monkeypatch.setattr(book_app, "prompt", lambda _: "Nonexistent")
        book_app.handle_remove()  # should not raise
        assert "removed" in capsys.readouterr().out.lower()


# ── handle_find ───────────────────────────────────────────────────────────────

class TestHandleFind:
    def test_find_returns_matching_books(self, monkeypatch, capsys):
        book_app.collection.add_book("Dune", "Frank Herbert", 1965)
        book_app.collection.add_book("Foundation", "Isaac Asimov", 1951)
        monkeypatch.setattr(book_app, "prompt", lambda _: "Frank Herbert")
        book_app.handle_find()
        out = capsys.readouterr().out
        assert "Dune" in out
        assert "Foundation" not in out

    def test_find_no_match_prints_no_books(self, monkeypatch, capsys):
        monkeypatch.setattr(book_app, "prompt", lambda _: "Unknown Author")
        book_app.handle_find()
        assert "No books found." in capsys.readouterr().out


# ── show_help ─────────────────────────────────────────────────────────────────

class TestShowHelp:
    def test_contains_commands(self, capsys):
        book_app.show_help()
        out = capsys.readouterr().out
        for cmd in ("list", "add", "remove", "find", "help"):
            assert cmd in out


# ── main ──────────────────────────────────────────────────────────────────────

class TestMain:
    def test_no_args_prints_help(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["book_app.py"])
        book_app.main()
        assert "Commands" in capsys.readouterr().out

    def test_list_command(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["book_app.py", "list"])
        book_app.main()
        assert "No books found." in capsys.readouterr().out

    def test_help_command(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["book_app.py", "help"])
        book_app.main()
        assert "Commands" in capsys.readouterr().out

    def test_unknown_command_prints_help(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["book_app.py", "bogus"])
        book_app.main()
        out = capsys.readouterr().out
        assert "Unknown command" in out

    def test_add_command(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["book_app.py", "add"])
        responses = iter(["Dune", "Frank Herbert", "1965"])
        monkeypatch.setattr(book_app, "prompt", lambda _: next(responses))
        book_app.main()
        assert "added successfully" in capsys.readouterr().out

    def test_remove_command(self, monkeypatch, capsys):
        book_app.collection.add_book("Dune", "Frank Herbert", 1965)
        monkeypatch.setattr(sys, "argv", ["book_app.py", "remove"])
        monkeypatch.setattr(book_app, "prompt", lambda _: "Dune")
        book_app.main()
        assert capsys.readouterr().out  # printed something

    def test_find_command(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["book_app.py", "find"])
        monkeypatch.setattr(book_app, "prompt", lambda _: "Nobody")
        book_app.main()
        assert "No books found." in capsys.readouterr().out

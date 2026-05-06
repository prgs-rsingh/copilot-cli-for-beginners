import sys

from books import BookCollection
from logging_config import get_logger
from utils import _strict_remove_enabled, parse_year, prompt, show_books

logger = get_logger(__name__)

# Global collection instance
collection = BookCollection()



def handle_list():
    books = collection.list_books()
    show_books(books)


def handle_add():
    print("\nAdd a New Book\n")

    title = prompt("Title: ")
    author = prompt("Author: ")
    year_str = prompt("Year: ")

    try:
        year = parse_year(year_str)
        collection.add_book(title, author, year)
        print("\nBook added successfully.\n")
    except ValueError as e:
        logger.warning("app.error", extra={"command": "add", "error": str(e)})
        print(f"\nError: {e}\n")


def handle_remove():
    print("\nRemove a Book\n")

    title = prompt("Enter the title of the book to remove: ")
    removed = collection.remove_book(title)

    if _strict_remove_enabled():
        if removed:
            print("\nBook removed successfully.\n")
        else:
            print("\nNo book found with that title.\n")
    else:
        print("\nBook removed if it existed.\n")


def handle_find():
    print("\nFind Books by Author\n")

    author = prompt("Author name: ")
    books = collection.find_by_author(author)

    show_books(books)


def show_help():
    print("""
Book Collection Helper

Commands:
  list     - Show all books
  add      - Add a new book
  remove   - Remove a book by title
  find     - Find books by author
  help     - Show this help message
""")


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "list":
        logger.info("app.command", extra={"command": command})
        handle_list()
    elif command == "add":
        logger.info("app.command", extra={"command": command})
        handle_add()
    elif command == "remove":
        logger.info("app.command", extra={"command": command})
        handle_remove()
    elif command == "find":
        logger.info("app.command", extra={"command": command})
        handle_find()
    elif command == "help":
        logger.info("app.command", extra={"command": command})
        show_help()
    else:
        logger.warning("app.unknown_command", extra={"command": command})
        print("Unknown command.\n")
        show_help()


if __name__ == "__main__":
    main()

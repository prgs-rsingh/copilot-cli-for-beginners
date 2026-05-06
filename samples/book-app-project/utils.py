import os
import datetime


def print_menu():
    print("\n📚 Book Collection App")
    print("1. Add a book")
    print("2. List books")
    print("3. Mark book as read")
    print("4. Remove a book")
    print("5. Exit")


def get_user_choice() -> str:
    return input("Choose an option (1-5): ").strip()


def _strict_year_enabled() -> bool:
    """Return True when BOOK_APP_STRICT_YEAR is set to '1', 'true', or 'yes' (case-insensitive)."""
    return os.environ.get("BOOK_APP_STRICT_YEAR", "").lower() in ("1", "true", "yes")


def parse_year(year_str: str) -> int:
    """Convert a year string to int.

    Returns 0 for blank input. Raises ValueError for non-numeric input.

    When BOOK_APP_STRICT_YEAR=1 is set, also raises ValueError if the year is
    not in the range [1, current_year].
    """
    if not year_str:
        return 0
    year = int(year_str)
    if _strict_year_enabled():
        current_year = datetime.date.today().year
        if not (1 <= year <= current_year):
            raise ValueError(
                f"Year {year} is out of range. Must be between 1 and {current_year} "
                "(BOOK_APP_STRICT_YEAR is enabled)."
            )
    return year


def get_book_details():
    title = input("Enter book title: ").strip()
    author = input("Enter author: ").strip()

    year_input = input("Enter publication year: ").strip()
    try:
        year = parse_year(year_input)
    except ValueError:
        print("Invalid year. Defaulting to 0.")
        year = 0

    return title, author, year


def show_books(books):
    """Display books in a user-friendly format."""
    if not books:
        print("No books found.")
        return

    print("\nYour Book Collection:\n")

    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")

    print()

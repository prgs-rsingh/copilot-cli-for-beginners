import datetime
import os

from logging_config import get_logger

logger = get_logger(__name__)


def print_menu():
    # Batch 6 print() calls into one to reduce print() call overhead per menu display.
    print(
        "\n\U0001f4da Book Collection App\n"
        "1. Add a book\n"
        "2. List books\n"
        "3. Mark book as read\n"
        "4. Remove a book\n"
        "5. Exit"
    )


def prompt(label: str) -> str:
    """Prompt the user with label and return the stripped response."""
    return input(label).strip()


def get_user_choice() -> str:
    return prompt("Choose an option (1-5): ")


# All flag truthy values — case-insensitive. Any other value (including empty) is OFF.
_BOOK_APP_TRUTHY = frozenset({"1", "true", "yes"})

# Tracks which flags have already emitted telemetry this process lifetime.
# Reset is needed in tests via monkeypatch.setattr(utils, "_logged_flags", set()).
_logged_flags: set[str] = set()


def _flag_enabled(env_var: str) -> bool:
    """Evaluate a BOOK_APP_* feature flag from the environment.

    Returns True when the named env var is '1', 'true', or 'yes' (case-insensitive).
    Emits a 'flag.active' INFO log event once per flag per process lifetime when ON.
    Silent when the flag is OFF (default state).

    Naming convention: BOOK_APP_<FEATURE> — uppercase, underscore-separated.
    Rollback any flag: unset the env var or set it to '0'.
    """
    result = os.environ.get(env_var, "").lower() in _BOOK_APP_TRUTHY
    if result and env_var not in _logged_flags:
        _logged_flags.add(env_var)
        logger.info("flag.active", extra={"flag": env_var})
    return result


def _strict_year_enabled() -> bool:
    """Return True when BOOK_APP_STRICT_YEAR is active (strict year range enforcement)."""
    return _flag_enabled("BOOK_APP_STRICT_YEAR")


def _strict_remove_enabled() -> bool:
    """Return True when BOOK_APP_STRICT_REMOVE is active.

    When ON: handle_remove() prints precise success/failure feedback.
    When OFF (default): prints hedged 'Book removed if it existed.' message.
    Rollback: unset BOOK_APP_STRICT_REMOVE or set it to '0'.
    """
    return _flag_enabled("BOOK_APP_STRICT_REMOVE")


def parse_year(year_str: str) -> int:
    """Convert a year string to int.

    Returns 0 for blank input. Raises ValueError for non-numeric input.

    Input length is capped at 10 digits before int() conversion to prevent
    large-integer resource exhaustion at the input boundary (CWE-190 variant).

    When BOOK_APP_STRICT_YEAR=1 is set, also raises ValueError if the year is
    not in the range [1, current_year].
    """
    if not year_str:
        return 0
    if len(year_str) > 10:  # 10 digits > any plausible year; guards large-int resource exhaustion
        raise ValueError(
            f"Year input is too long ({len(year_str)} chars). Maximum accepted length: 10 digits."
        )
    year = int(year_str)
    if _strict_year_enabled():
        current_year = datetime.date.today().year
        if not (1 <= year <= current_year):
            logger.info(
                "year.parse_rejected",
                extra={"year": year, "limit": current_year, "strict": True},
            )
            raise ValueError(
                f"Year {year} is out of range. Must be between 1 and {current_year} "
                "(BOOK_APP_STRICT_YEAR is enabled)."
            )
    return year


def get_book_details():
    title = prompt("Enter book title: ")
    author = prompt("Enter author: ")

    year_input = prompt("Enter publication year: ")
    try:
        year = parse_year(year_input)
    except ValueError as e:
        logger.warning("year.parse_error", extra={"input": year_input, "reason": str(e)})
        print("Invalid year. Defaulting to 0.")
        year = 0

    return title, author, year


def show_books(books):
    """Display books in a user-friendly format."""
    if not books:
        print("No books found.")
        return

    # Batch all lines into one print() call instead of N+3 separate calls.
    # Output is byte-for-byte identical; reduces print overhead from O(N) to O(1).
    lines = ["\nYour Book Collection:\n"]
    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        lines.append(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")
    lines.append("")
    print("\n".join(lines))

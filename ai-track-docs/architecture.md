# Architecture — Book App Project

This document maps the conceptual architecture of the primary course sample
(`samples/book-app-project/`) to real file paths in the repository.

---

## Module Map

| Conceptual Role | Real File Path |
|---|---|
| CLI Entry Point | `samples/book-app-project/book_app.py` |
| Domain Model + Collection | `samples/book-app-project/books.py` |
| UI Helpers | `samples/book-app-project/utils.py` |
| Persistent Store | `samples/book-app-project/data.json` |
| Test Suite | `samples/book-app-project/tests/test_books.py` |
| Project Config | `samples/book-app-project/pyproject.toml` |

---

## Dependency Graph

```mermaid
graph TD
    A["book_app.py<br/>(CLI Entry Point)"] -->|imports BookCollection| B["books.py<br/>(Book + BookCollection)"]
    A["book_app.py<br/>(CLI Entry Point)"] -->|imports helpers| C["utils.py<br/>(UI Helpers)"]
    B["books.py<br/>(Book + BookCollection)"] -->|reads/writes| D["data.json<br/>(Persistent Store)"]
    B["books.py<br/>(Book + BookCollection)"] -->|uses| E["json / dataclasses<br/>(stdlib)"]
    T["tests/test_books.py<br/>(pytest Suite)"] -->|imports BookCollection| B
    T -->|monkeypatches DATA_FILE| F["tmp_path/data.json<br/>(Test Isolation)"]
```

---

## Data Flows

### Flow 1 — User writes a book (Add/Remove/Mark-Read)

```mermaid
sequenceDiagram
    participant U as User (stdin)
    participant A as book_app.py
    participant Ut as utils.py
    participant BC as books.py::BookCollection
    participant D as data.json

    U->>A: selects menu option (1/4/3)
    A->>Ut: get_book_details() / get_user_choice()
    Ut-->>A: (title, author, year)
    A->>BC: add_book(title, author, year)
    BC->>D: save_books() → json.dump(...)
    D-->>BC: write confirmed
    BC-->>A: Book instance
    A->>Ut: show_books([...])
    Ut-->>U: formatted output (stdout)
```

### Flow 2 — User reads the collection (List)

```mermaid
sequenceDiagram
    participant U as User (stdin)
    participant A as book_app.py
    participant BC as books.py::BookCollection
    participant D as data.json
    participant Ut as utils.py

    U->>A: selects option 2 (List)
    A->>BC: list_books()
    BC->>D: load_books() → json.load(...)
    D-->>BC: raw JSON list
    BC-->>A: List[Book]
    A->>Ut: show_books(books)
    Ut-->>U: numbered book list (stdout)
```

### Flow 3 — Test isolation (pytest)

```mermaid
sequenceDiagram
    participant PT as pytest runner
    participant TF as test_books.py
    participant MP as monkeypatch fixture
    participant TMP as tmp_path/data.json
    participant BC as books.py::BookCollection

    PT->>TF: collect & run test
    TF->>MP: monkeypatch.setattr(books, "DATA_FILE", tmp_file)
    MP-->>TF: DATA_FILE redirected
    TF->>BC: BookCollection() — loads from tmp_path
    TMP-->>BC: empty []
    TF->>BC: add_book / assert ...
    BC->>TMP: save_books()
    TF-->>PT: pass / fail
```

---

## Course-Level Structure

```mermaid
graph LR
    ROOT["repo root"] --> CHAPTERS["00-07/<br/>Chapter READMEs"]
    ROOT --> SAMPLES["samples/<br/>All Sample Apps"]
    ROOT --> SCRIPTS[".github/scripts/<br/>Build & Demo Scripts"]
    ROOT --> CI[".github/workflows/<br/>CI Workflows"]
    ROOT --> AIDOCS["ai-track-docs/<br/>Track Docs"]

    SAMPLES --> PRIMARY["book-app-project/<br/>(primary sample)"]
    SAMPLES --> BUGGY["book-app-buggy/<br/>(debugging exercises)"]
    SAMPLES --> CS["book-app-project-cs/<br/>(C# variant)"]
    SAMPLES --> JS["book-app-project-js/<br/>(JS variant)"]

    SCRIPTS --> PKG["package.json<br/>npm run release / validate:arch"]
```

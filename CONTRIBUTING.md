## Contributing

[fork]: https://github.com/github/REPO/fork
[pr]: https://github.com/github/REPO/compare

Hi there! We're thrilled that you'd like to contribute to this project. Your help is essential for keeping it great.

Contributions to this project are [released](https://help.github.com/articles/github-terms-of-service/#6-contributions-under-repository-license) to the public under the [project's open source license](LICENSE.txt).

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## Running Tests and Coverage

The primary sample app uses **pytest** with **pytest-cov** for test coverage.

### Prerequisites

Make sure you are using the project's virtual environment (Python 3.10+):

```bash
cd samples/book-app-project
# Activate the existing venv, or create one:
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pytest-cov
```

### Run tests with coverage

```bash
cd samples/book-app-project
.venv/bin/pytest
```

Coverage is enabled by default via `pyproject.toml` (`addopts`). This produces:
- A **terminal summary** with missing line numbers
- An **HTML report** at `samples/book-app-project/htmlcov/index.html`

### Understanding coverage numbers

| Module | Role | Expected coverage |
|---|---|---|
| `books.py` | Domain logic — `Book` dataclass + `BookCollection` | High (≥ 85%) |
| `book_app.py` | CLI entry point — `input()` / `print()` orchestration | Low (not unit-tested by design) |
| `utils.py` | UI helpers — menu display, stdin prompts | Low (not unit-tested by design) |

**Target**: keep `books.py` coverage ≥ 85%. The overall total will be lower due to the untested CLI/UI surface — this is expected and acceptable.

### Including coverage in your PR

Run the command above and paste the `TOTAL` line from the terminal output into your PR description under the **Evidence** section, e.g.:

```
- Tests/logs/metrics: `.venv/bin/pytest` → 5 passed in 0.17s
- Coverage: 35% total (books.py 87%)
```

---

## Walk Track Workflow

This repo uses a structured **Walk track** for AI-assisted development exercises. If you are working through the walk exercises, follow this workflow for every PR.

### Branching strategy

```
main
└── walk/ex-<N>-<slug>    e.g. walk/ex-04-onboarding-docs
```

Create a branch per exercise:

```bash
git checkout -b walk/ex-04-onboarding-docs
```

### Prompt structure

Every exercise starts with a structured prompt (stored in `.copilot-track/walk/prompt-exercise.md`) with four sections:

| Section | Purpose |
|---|---|
| **Mini Prompt** | One-sentence goal |
| **Steps** | Ordered steps for Copilot to follow |
| **Acceptance** | Pass/fail checkpoints to verify after execution |
| **Troubleshooting** | Hints for resolving ambiguity |

Paste the full prompt into Copilot Chat at the start of each session.

### PR expectations

Every walk PR must use the template in `.copilot-track/walk/pr-template.md`. The PR description must include:

- A filled **Summary** with a link or inline plan
- **Evidence**: test command + output + coverage percentage
- **Risk & Rollback**: always include the rollback commit SHA after pushing
- **Review Focus**: at least one runnable verification step for the reviewer

### Exercise record

After completing an exercise, save `ai-track-docs/ex-<N>-<summary>.md` (auto-incremented) containing the steps run, acceptance results, and the filled PR template. Commit this file alongside the exercise changes.

> For a copy-pasteable onboarding prompt to get Copilot oriented, see [ai-track-docs/onboarding-walk.md](./ai-track-docs/onboarding-walk.md).

# Book App — Operations Runbook

This runbook covers the retry/backoff/deadline configuration used by the book app,
worst-case latency calculations, diagnostic procedures, and escalation steps.

---

## Retry Call-Path Registry

| Call site | Decorator parameters | Purpose |
|---|---|---|
| `books.save_books()` | `max_retries=3, initial_delay=0.05, backoff_factor=2.0, exceptions=(OSError,), deadline=5.0` | Atomic JSON write; retries disk/NFS blips |
| `books.load_books()` | `max_retries=3, initial_delay=0.1, backoff_factor=2.0, exceptions=(OSError,), deadline=5.0` | JSON read at startup; retries transient PermissionError |

Both decorators are in `resilience.py`. To check active settings at runtime:

```python
import inspect
from books import BookCollection
print(inspect.getsource(BookCollection.save_books))
```

---

## Worst-Case Latency

### `save_books()` (initial_delay=0.05 s)

| Attempt | Outcome | Sleep before next |
|---|---|---|
| 1 | Fail | 0.05 s |
| 2 | Fail | 0.10 s |
| 3 | Fail/raise | — |

**Max wall time (no deadline):** ~150 ms + call time  
**With deadline=5.0 s:** raises `TimeoutError` if any attempt + sleep exceeds 5 s

### `load_books()` (initial_delay=0.1 s)

| Attempt | Outcome | Sleep before next |
|---|---|---|
| 1 | Fail | 0.10 s |
| 2 | Fail | 0.20 s |
| 3 | Fail/raise | — |

**Max wall time (no deadline):** ~300 ms + call time  
**With deadline=5.0 s:** raises `TimeoutError` if total time exceeds 5 s

---

## Log Events

All events are emitted via the `resilience` logger in JSON format (see `logging_config.py`).

| Event | Level | When |
|---|---|---|
| `retry.attempt` | WARNING | After each failed attempt except the last |
| `retry.exhausted` | ERROR (exception) | All retries used; re-raising last exception |
| `retry.deadline_exceeded` | WARNING | Elapsed wall time >= deadline; raising TimeoutError |

### Filtering retry events from logs

```bash
# Show all retry events (structured JSON log to stderr)
python book_app.py 2>&1 | grep -E '"(retry\.attempt|retry\.exhausted|retry\.deadline_exceeded)"'
```

---

## Tuning Guide

### Change retry count

Edit the `max_retries` argument on the decorator in `books.py`.
Higher values increase worst-case latency linearly.

```
Worst-case sleeps = max_retries - 1
Max sleep total   = initial_delay × (backoff_factor^(max_retries-1) - 1) / (backoff_factor - 1)
```

For `initial_delay=0.05, backoff_factor=2.0, max_retries=3`:  
Max sleep = 0.05 × (4 - 1) / (2 - 1) = **0.15 s**

### Change deadline

`deadline` sets the total wall-time budget. A `TimeoutError` is raised once
`time.monotonic() - start >= deadline` after a failure. The budget covers all
attempts and all sleeps.

Recommended values by context:

| Context | Suggested deadline |
|---|---|
| Local SSD | 1.0 s |
| Local HDD / busy filesystem | 5.0 s (current default) |
| Network filesystem (NFS/SMB) | 15.0–30.0 s |
| Not applicable / disable | Remove `deadline=` argument |

### Disable retries for a call site

Remove the `@retry_with_backoff(...)` decorator line from the method.
The underlying function is unchanged and works without it.

### Disable deadline only

Remove `deadline=5.0` from the decorator argument list.
Retries continue until `max_retries` is exhausted, with no wall-time limit.

---

## Diagnostic Procedure

### Symptom: `TimeoutError` raised during startup

**Likely cause:** Filesystem lock held for > 5 s when `load_books()` tries to open `data.json`.

**Steps:**
1. Check filesystem health: `df -h`, `mount`, check NFS/SMB mount status
2. Check file permissions: `ls -la samples/book-app-project/data.json`
3. Check for lock holders: `lsof samples/book-app-project/data.json`
4. If NFS: increase `deadline` to 30.0 in `books.py`; restart the app
5. If permission issue: `chmod 644 samples/book-app-project/data.json`

### Symptom: `OSError` / `PermissionError` raised during save

**Likely cause:** Disk full, or write permission revoked.

**Steps:**
1. Check disk space: `df -h .`
2. Check write permission: `ls -la samples/book-app-project/`
3. Review retry log: look for `retry.exhausted` events in stderr

### Symptom: Slow startup (> 1 s but no exception)

**Likely cause:** Transient filesystem hiccups being retried silently.

**Steps:**
1. Run with stderr visible: `python book_app.py 2>&1 | head -50`
2. Look for `retry.attempt` events — they indicate retries are occurring
3. If retries are frequent, investigate filesystem stability

---

## Rollback

To remove all retry/deadline behaviour from the book app:

```bash
cd samples/book-app-project
git checkout HEAD -- resilience.py books.py
```

To remove retry from a single call site only, delete the `@retry_with_backoff(...)`
decorator line from the relevant method in `books.py`. The function works unchanged.

---

## Testing Resilience Locally

```bash
cd samples/book-app-project
# Run all resilience tests
.venv/bin/pytest tests/test_resilience.py -v

# Run only deadline tests
.venv/bin/pytest tests/test_resilience.py -v -k "Deadline"

# Run only load_books resilience tests
.venv/bin/pytest tests/test_resilience.py -v -k "LoadBooks"
```

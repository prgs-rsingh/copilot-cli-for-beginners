---
applyTo: "**/*"
---

# Submodule & Vendor Safety Rules

The following paths are **read-only references**. Do not propose or apply edits inside them.

## Excluded Paths

```
vendor/**
third_party/**
**/.git/modules/**
```

Any path listed in `.gitmodules` (if present) is also excluded.

## Rules

- Do not propose or apply edits in excluded paths; treat them as read-only references.
- If a task requires changes that appear to touch an excluded path, stop and explain the constraint to the user instead of modifying the file.
- Cross-reference excluded code by file path only (e.g., in comments or docs), never by copying and modifying it.

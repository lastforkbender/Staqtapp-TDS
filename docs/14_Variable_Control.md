# 14 — Variable Control Layer

Staqtapp-TDS v1.7.3 restores the core identity of original Staqtapp: Python variable storage with names that matter.

The variable layer is intentionally isolated in `variables.py`. It does not become part of the low-level hot path. The directory still owns storage, the entry index still owns lookup, and the variable layer owns naming behavior, locks, and residual/stalk chains.

## APIs

```python
dir.addvar("name", data)
dir.editvar("name", data)
dir.lockvar("name")
dir.unlockvar("name")
dir.stalkvar("~name", data)
dir.stalkvar("name", None)
dir.findvar("name")
dir.loadvar("name")
```

All normal conflicts return `TDSResult` rather than halting execution.

## Duplicate Name Rule

Inside a directory, variable names are protected identities. `addvar()` will not silently overwrite an existing name.

```python
result = dir.addvar("state", {"a": 1})
result = dir.addvar("state", {"b": 2})
assert result.code == "VAR_EXISTS"
```

The AI/agent receives structured feedback and can decide whether to call `editvar()`.

## Lock Variables

`lockvar()` marks a variable as protected in the internal control table. Locked variables reject normal edits and stalk operations with structured feedback.

```python
dir.lockvar("state")
result = dir.editvar("state", {"x": 1})
assert result.code == "VAR_LOCKED"
```

## Stalk Variables

`stalkvar()` preserves the original Staqtapp residual-copy feature.

```python
dir.addvar("new_var", {"a": 1})
dir.stalkvar("~new_var", {"b": 2})
dir.stalkvar("~new_var", {"c": 3})
```

Result:

```text
new_var      = {"a": 1}
new_var_0001 = {"a": 1, "b": 2}
new_var_0002 = {"a": 1, "b": 2, "c": 3}
```

Each increment is built from the immediately previous tracked value, not from the original base every time.

## Clearing a Chain

```python
dir.stalkvar("new_var", None)
```

This removes tracked `new_var_####` increments and keeps the base `new_var` unchanged.

```python
dir.stalkvar("new_var", {"z": 9})
```

This removes tracked increments and replaces the base value.

## Internal Tracking

The control state is exposed conceptually as:

```text
.tds_internal/
  lockvars/
  stalkvars/
```

In v1.7.3 the control tables are stored in the directory metadata snapshot and persisted in `.tds.meta`.

## Performance Boundary

The variable layer performs checks only at variable API boundaries. Normal low-level `read()` and entry-index lookup remain separate. Future native indexing can accelerate storage lookup without changing variable semantics.

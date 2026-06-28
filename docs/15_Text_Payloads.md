# 15 — Text Payloads

Staqtapp-TDS is Python-variable-native, but v1.7.3 adds a first-class text lane for source data.

Target text types:

- `.txt`
- `.md`
- `.py`
- `.json`
- `.yaml` / `.yml`
- `.toml`
- `.csv` / `.tsv`
- logs and notes

Non-goals:

- images
- audio
- video
- arbitrary opaque binary media

## APIs

```python
dir.write_text("README.md", "# Title")
text = dir.read_text("README.md")
```

Duplicate text file names return structured conflict feedback unless `overwrite=True`.

```python
result = dir.write_text("README.md", "new")
result = dir.write_text("README.md", "replacement")
assert result.code == "TEXT_EXISTS"

result = dir.write_text("README.md", "replacement", overwrite=True)
assert result.ok
```

## Encoding

Text is stored as strict UTF-8 using `FmtID.TEXT_UTF8`.

This avoids unnecessary pickle usage for whole text files and makes the storage path clearer for future non-Python tooling.

## Compression

Text compression is optional:

```python
dir.write_text("notes.md", text, compress=True)
```

Policy guidance:

- small text: no compression
- medium/large cold text: compression acceptable
- hot source files: prefer raw UTF-8 until profiling proves otherwise
- logs: future chunked append storage is preferred

## Separation from Variables

Text files and Python variables share directory namespace identity, so duplicate names are still protected. However, they use separate APIs and payload formats.

```text
variables.py    -> Python variable semantics
TEXT_UTF8 lane  -> whole source text storage
```

This keeps Staqtapp identity intact while giving source text a cleaner storage path.

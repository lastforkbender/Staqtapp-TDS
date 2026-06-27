# 04 — Semantic Routing Zones

Semantic Routing Zones provide compact routing identity for directories.

An SRZ-enabled directory may include:

- `route_stamp`,
- `route_id`,
- source tags,
- aliases,
- latent ID,
- flags.

SRZ is optional because some directories should remain simple and fast.

## Example

```python
zone = fs.root.mkdir(
    "tokenizers",
    srz_enabled=True,
    route_stamp="ML.TOK.ENC.SEM.v1",
    source_tags=["ml", "encoding"],
    aliases=["semantic-token-map"],
)
```

## Boundary

SRZ routes. It does not reason. It gives the consuming system stable names and compact IDs.

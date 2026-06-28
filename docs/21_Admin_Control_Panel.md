# 21 — Admin Control Panel and Runtime Config Generations

v2.2.0 adds an optional localhost admin control surface for staging, promoting,
and rolling back immutable `RuntimeConfig` generations. It is deliberately outside
TDS hot-path operations.

## Boundary

```text
Browser/CLI panel -> AdminControl -> ConfigRegistry -> TDSDirectory.active()
```

Normal reads and writes only read the active config pointer. Authorization,
validation, and audit happen before promotion.

## Local panel

```bash
python -m staqtapp_tds.admin.console serve-panel --host 127.0.0.1 --port 8765
```

The panel is local-only by default. It should not be placed on the public internet.
Future hardened deployments can replace the local auth provider with mTLS,
hardware-backed grants, quorum approval, or signed offline config bundles without
changing the core TDS directory/index code.

## Metadata

New writes record compact config provenance:

```text
config_id
config_generation
key_id
serializer/compression metadata already tracked by the entry
```

Existing entries retain the metadata of the config generation that wrote them.

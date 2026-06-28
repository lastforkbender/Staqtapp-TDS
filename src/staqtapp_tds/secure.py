from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping
import os

REDACTED = "***REDACTED***"

@dataclass(frozen=True)
class SecureParams:
    values: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls, prefix: str = "TDS_") -> "SecureParams":
        return cls({k[len(prefix):].lower(): v for k, v in os.environ.items() if k.startswith(prefix)})

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> "SecureParams":
        return cls(dict(values))

    def get_secret(self, name: str, default: str | None = None) -> str | None:
        return self.values.get(name, default)

    def require(self, *names: str) -> None:
        missing = [n for n in names if n not in self.values or self.values[n] == ""]
        if missing:
            raise ValueError(f"Missing secure parameter(s): {', '.join(missing)}")

    def redact(self) -> dict[str, str]:
        return {k: REDACTED for k in self.values}

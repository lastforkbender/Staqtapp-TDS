from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class EntryDescriptor:
    entry_id: str
    key: str = ""
    handle: int = -1
    hash_value: int = 0
    chunk_id: str = ""
    size: int = 0
    flags: int = 0
    runtime_config: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id, "key": self.key, "handle": self.handle,
            "hash_value": self.hash_value, "chunk_id": self.chunk_id,
            "size": self.size, "flags": self.flags,
            "runtime_config": self.runtime_config,
        }

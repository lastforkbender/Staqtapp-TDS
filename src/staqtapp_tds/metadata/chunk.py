from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class ChunkDescriptor:
    chunk_id: str
    entry_id: str = ""
    offset: int = 0
    length: int = 0
    stored_length: int = 0
    compressed: bool = False
    checksum: int = 0
    codec: str = ""
    runtime_config: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id, "entry_id": self.entry_id,
            "offset": self.offset, "length": self.length,
            "stored_length": self.stored_length, "compressed": self.compressed,
            "checksum": self.checksum, "codec": self.codec,
            "runtime_config": self.runtime_config,
        }

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class NamespaceDescriptor:
    name: str
    path: str = ""
    parent: str = ""
    depth: int = 0
    entry_count: int = 0
    child_count: int = 0
    route_id: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name, "path": self.path, "parent": self.parent,
            "depth": self.depth, "entry_count": self.entry_count,
            "child_count": self.child_count, "route_id": self.route_id,
        }

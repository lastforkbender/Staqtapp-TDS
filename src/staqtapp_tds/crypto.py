from __future__ import annotations
from typing import Protocol

class CryptoProvider(Protocol):
    def encrypt(self, data: bytes, key_id: str | None = None) -> bytes: ...
    def decrypt(self, data: bytes, key_id: str | None = None) -> bytes: ...

class NoopCryptoProvider:
    def encrypt(self, data: bytes, key_id: str | None = None) -> bytes:
        return data
    def decrypt(self, data: bytes, key_id: str | None = None) -> bytes:
        return data

class XorCryptoProvider:
    """Tiny deterministic test provider, not production cryptography."""
    def __init__(self, key: bytes):
        if not key:
            raise ValueError("key must not be empty")
        self.key = key
    def _apply(self, data: bytes) -> bytes:
        k = self.key
        return bytes(b ^ k[i % len(k)] for i, b in enumerate(data))
    def encrypt(self, data: bytes, key_id: str | None = None) -> bytes:
        return self._apply(data)
    def decrypt(self, data: bytes, key_id: str | None = None) -> bytes:
        return self._apply(data)

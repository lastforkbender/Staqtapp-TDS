from __future__ import annotations
from dataclasses import dataclass, field
import hmac, secrets, time

@dataclass(frozen=True)
class ConfigGrant:
    subject: str
    action: str
    issued_at: float
    expires_at: float
    nonce: str
    signature: str

    def is_valid(self, secret: str, action: str | None = None) -> bool:
        if time.time() > self.expires_at:
            return False
        if action is not None and self.action != action:
            return False
        msg = f"{self.subject}|{self.action}|{self.issued_at:.6f}|{self.expires_at:.6f}|{self.nonce}"
        expected = hmac.new(secret.encode(), msg.encode(), "sha256").hexdigest()
        return hmac.compare_digest(expected, self.signature)

class LocalAuthProvider:
    def __init__(self, secret: str = "local-dev-admin-secret", default_subject: str = "local-admin"):
        self.secret = secret
        self.default_subject = default_subject
    def issue(self, action: str, *, subject: str | None = None, ttl_seconds: int = 300) -> ConfigGrant:
        issued = time.time(); expires = issued + ttl_seconds; nonce = secrets.token_hex(12)
        subj = subject or self.default_subject
        msg = f"{subj}|{action}|{issued:.6f}|{expires:.6f}|{nonce}"
        sig = hmac.new(self.secret.encode(), msg.encode(), "sha256").hexdigest()
        return ConfigGrant(subj, action, issued, expires, nonce, sig)
    def verify(self, grant: ConfigGrant, action: str) -> None:
        if not grant.is_valid(self.secret, action):
            raise PermissionError("Invalid or expired config grant")

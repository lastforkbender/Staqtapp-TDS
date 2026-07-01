from __future__ import annotations
from dataclasses import dataclass, field
import hmac, os, secrets, time

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
    DEV_SECRET = "local-dev-admin-secret"

    def __init__(self, secret: str | None = None, default_subject: str = "local-admin", *, allow_dev_secret: bool | None = None):
        resolved = secret or os.environ.get("STAQTAPP_TDS_ADMIN_SECRET") or self.DEV_SECRET
        if allow_dev_secret is None:
            allow_dev_secret = resolved == self.DEV_SECRET
        if resolved == self.DEV_SECRET and not allow_dev_secret:
            raise ValueError("STAQTAPP_TDS_ADMIN_SECRET must override the local development admin secret outside localhost/dev mode")
        self.secret = resolved
        self.default_subject = default_subject
        self.using_dev_secret = resolved == self.DEV_SECRET

    def assert_safe_for_bind(self, host: str) -> None:
        local_hosts = {"", "localhost", "127.0.0.1", "::1"}
        if self.using_dev_secret and str(host).strip().lower() not in local_hosts:
            raise ValueError("Refusing non-local admin bind with default local-dev-admin-secret; set STAQTAPP_TDS_ADMIN_SECRET or pass a unique secret")
    def issue(self, action: str, *, subject: str | None = None, ttl_seconds: int = 300) -> ConfigGrant:
        issued = time.time(); expires = issued + ttl_seconds; nonce = secrets.token_hex(12)
        subj = subject or self.default_subject
        msg = f"{subj}|{action}|{issued:.6f}|{expires:.6f}|{nonce}"
        sig = hmac.new(self.secret.encode(), msg.encode(), "sha256").hexdigest()
        return ConfigGrant(subj, action, issued, expires, nonce, sig)
    def verify(self, grant: ConfigGrant, action: str) -> None:
        if not grant.is_valid(self.secret, action):
            raise PermissionError("Invalid or expired config grant")

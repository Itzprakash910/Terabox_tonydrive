from dataclasses import dataclass, field
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc)

@dataclass
class User:
    user_id: int
    username: str | None = None
    first_name: str | None = None
    blocked: bool = False
    premium_until: str | None = None
    downloads_today: int = 0
    usage_date: str = field(default_factory=lambda: now().date().isoformat())
    total_downloads: int = 0

    def is_premium(self):
        if not self.premium_until:
            return False
        try:
            return datetime.fromisoformat(self.premium_until) > now()
        except ValueError:
            return False

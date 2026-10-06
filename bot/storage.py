import json
from pathlib import Path
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from .models import User

class JSONRepository:
    # MongoDB can replace this repository later without changing bot business logic.
    def __init__(self, path="data/users.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def get(self, user_id, **meta):
        data = self._load()
        key = str(user_id)
        if key not in data:
            data[key] = asdict(User(user_id=user_id, **meta))
        else:
            for k, v in meta.items():
                if v is not None:
                    data[key][k] = v
        u = User(**data[key])
        today = datetime.now(timezone.utc).date().isoformat()
        if u.usage_date != today:
            u.usage_date, u.downloads_today = today, 0
        data[key] = asdict(u)
        self._save(data)
        return u

    def put(self, user):
        data = self._load()
        data[str(user.user_id)] = asdict(user)
        self._save(data)

    def all(self):
        return [User(**x) for x in self._load().values()]

    def set_premium(self, user_id, days):
        u = self.get(user_id)
        base = datetime.now(timezone.utc)
        if u.is_premium():
            base = datetime.fromisoformat(u.premium_until)
        u.premium_until = (base + timedelta(days=days)).isoformat()
        self.put(u)
        return u

    def remove_premium(self, user_id):
        u = self.get(user_id)
        u.premium_until = None
        self.put(u)
        return u

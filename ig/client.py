from __future__ import annotations
import json
from pathlib import Path
import requests
from .constants import SEARCH_URL

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Referer": "https://www.instagram.com/",
}

REQUIRED_COOKIES = {"csrftoken", "ds_user_id", "sessionid"}


def load_cookies(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = REQUIRED_COOKIES - set(data.keys())
    if missing:
        raise ValueError(f"Missing cookies: {', '.join(sorted(missing))}")
    return data


def make_session(cookies: dict, headers: dict | None = None) -> requests.Session:
    s = requests.Session()
    s.headers.update(headers or DEFAULT_HEADERS)
    s.cookies.update(cookies)
    return s


def get_user_id(session: requests.Session, username: str) -> str:
    resp = session.get(SEARCH_URL, params={"context": "blended", "query": username})
    resp.raise_for_status()
    data = resp.json()
    users = data.get("users", [])
    if not users:
        raise ValueError(f"Unable to resolve user id for '{username}'.")
    user = users[0].get("user", {})
    uid = str(user.get("pk", "")) if user else ""
    if not uid:
        raise ValueError(f"User id missing in response for '{username}'.")
    return uid

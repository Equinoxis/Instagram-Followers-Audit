from __future__ import annotations
import requests
from .constants import QH_FOLLOWERS, QH_FOLLOWINGS
from .paginate import paginate_edges

def get_followers_nodes(session: requests.Session, user_id: str) -> list[dict]:
    nodes = paginate_edges(session, user_id, QH_FOLLOWERS, ["data", "user", "edge_followed_by"])
    out = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        out.append({
            "username": n.get("username"),
            "full_name": n.get("full_name") or "",
            "pk": n.get("id") or n.get("pk"),
            "is_verified": bool(n.get("is_verified")),
            "is_private": bool(n.get("is_private")),
            "profile_pic_url": n.get("profile_pic_url") or "",
        })
    return [u for u in out if u["username"]]

def get_followings_nodes(session: requests.Session, user_id: str) -> list[dict]:
    nodes = paginate_edges(session, user_id, QH_FOLLOWINGS, ["data", "user", "edge_follow"])
    out = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        out.append({
            "username": n.get("username"),
            "full_name": n.get("full_name") or "",
            "pk": n.get("id") or n.get("pk"),
            "is_verified": bool(n.get("is_verified")),
            "is_private": bool(n.get("is_private")),
            "profile_pic_url": n.get("profile_pic_url") or "",
        })
    return [u for u in out if u["username"]]

def get_followers(session: requests.Session, user_id: str) -> list[str]:
    return [u["username"] for u in get_followers_nodes(session, user_id)]

def get_followings(session: requests.Session, user_id: str) -> tuple[list[str], list[str]]:
    nodes = get_followings_nodes(session, user_id)
    followings = [u["username"] for u in nodes]
    verified = [u["username"] for u in nodes if u["is_verified"]]
    return verified, followings

from __future__ import annotations
import json
import time
import requests
from .constants import GRAPHQL_URL


class GraphQLPaginationError(RuntimeError):
    pass


def paginate_edges(
    session: requests.Session,
    user_id: str,
    query_hash: str,
    edge_path: list[str],
    per_page: int = 50,
    sleep_seconds: float = 0.3,
) -> list[dict]:
    """
    Returns a list of node dicts for the requested edge.
    edge_path examples:
      followers: ["data", "user", "edge_followed_by"]
      followings: ["data", "user", "edge_follow"]
    """
    nodes: list[dict] = []
    after: str | None = None

    while True:
        variables = {"id": user_id, "first": per_page}
        if after:
            variables["after"] = after

        params = {
            "query_hash": query_hash,
            "variables": json.dumps(variables, separators=(",", ":")),
        }

        resp = session.get(GRAPHQL_URL, params=params)
        resp.raise_for_status()
        payload = resp.json()

        cur: dict | None = payload
        for key in edge_path:
            if not isinstance(cur, dict) or key not in cur:
                raise GraphQLPaginationError("Unexpected GraphQL response structure.")
            cur = cur[key]

        if not isinstance(cur, dict):
            raise GraphQLPaginationError("Edge node is not a dict.")

        edges = cur.get("edges", []) or []
        page_info = cur.get("page_info", {}) or {}

        for e in edges:
            node = (e or {}).get("node")
            if node:
                nodes.append(node)

        if page_info.get("has_next_page") and page_info.get("end_cursor"):
            after = page_info["end_cursor"]
            time.sleep(sleep_seconds)
        else:
            break

    return nodes

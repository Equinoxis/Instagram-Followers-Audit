from __future__ import annotations
from pathlib import Path
from datetime import datetime
import csv
import json

# ---------- helpers ----------
def _index_by_username(users: list[dict]) -> dict[str, dict]:
    return {u["username"]: u for u in users}

def _sorted_usernames(names: list[str]) -> list[str]:
    return sorted(set(names), key=str.lower)

def _as_table_md(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    # pad header separator row
    widths = [max(len(str(cell)) for cell in col) for col in zip(*rows)]
    def fmt(r):
        return "| " + " | ".join(str(c).ljust(w) for c, w in zip(r, widths)) + " |\n"
    out = ""
    out += fmt(rows[0])
    out += "| " + " | ".join("-" * w for w in widths) + " |\n"
    for r in rows[1:]:
        out += fmt(r)
    return out

# ---------- main builders ----------
def build_sets(
    followers_nodes: list[dict],
    followings_nodes: list[dict],
) -> dict:
    followers = [u["username"] for u in followers_nodes]
    followings = [u["username"] for u in followings_nodes]
    s_followers = set(followers)
    s_followings = set(followings)

    # Derived sets
    mutuals = _sorted_usernames(s_followers & s_followings)
    i_dont_follow_back = _sorted_usernames(s_followers - s_followings)

    # Split "I follow them but they don't follow me" into verified vs non-verified
    idx_followings = _index_by_username(followings_nodes)
    raw_not_following_back = s_followings - s_followers
    verified_not_following_back = _sorted_usernames(
        [u for u in raw_not_following_back if idx_followings.get(u, {}).get("is_verified")]
    )
    not_following_back = _sorted_usernames(
        [u for u in raw_not_following_back if not idx_followings.get(u, {}).get("is_verified")]
    )

    return {
        "followers": _sorted_usernames(followers),
        "followings": _sorted_usernames(followings),
        "mutuals": mutuals,
        "i_dont_follow_back": i_dont_follow_back,
        "not_following_back": not_following_back,  # now ONLY unverified accounts
        "verified_not_following_back": verified_not_following_back,
    }


def build_markdown_report(username: str, sets: dict, followings_nodes: list[dict]) -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    idx_followings = _index_by_username(followings_nodes)

    def people_rows(names: list[str]) -> list[list[str]]:
        rows = [["#", "Username", "Full name", "Verified", "Private"]]
        for i, u in enumerate(names, 1):
            n = idx_followings.get(u, {})  # for followers only, some fields may be empty; ok
            rows.append([
                str(i),
                u,
                n.get("full_name", ""),
                "✅" if n.get("is_verified") else "",
                "🔒" if n.get("is_private") else "",
            ])
        return rows

    title = f"# Instagram audit for **{username}**\n\n_Generated: {ts}_\n\n"
    summary = _as_table_md([
        ["Metric", "Count"],
        ["Followers", str(len(sets["followers"]))],
        ["Followings", str(len(sets["followings"]))],
        ["Mutuals", str(len(sets["mutuals"]))],
        ["I don't follow back", str(len(sets["i_dont_follow_back"]))],
        ["Not following back", str(len(sets["not_following_back"]))],
        ["Not following back (verified)", str(len(sets["verified_not_following_back"]))],
    ]) + "\n\n"

    sections = []
    for label, key in [
        ("Mutuals", "mutuals"),
        ("I don't follow back", "i_dont_follow_back"),
        ("Not following back", "not_following_back"),
        ("Not following back (verified)", "verified_not_following_back"),
    ]:
        names = sets[key]
        sections.append(f"## {label} ({len(names)})\n\n" + _as_table_md(people_rows(names)) + "\n")

    return title + "## Summary\n\n" + summary + "".join(sections)

# ---------- writers ----------
def write_all_outputs(
    username: str,
    followers_nodes: list[dict],
    followings_nodes: list[dict],
    out_dir: str | Path = ".",
) -> dict[str, Path]:
    out = {}
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    sets = build_sets(followers_nodes, followings_nodes)

    # CSVs
    def write_csv(name: str, rows: list[dict]):
        p = out_path / f"{name}.csv"
        if rows:
            fieldnames = ["username", "full_name", "is_verified", "is_private", "pk", "profile_pic_url"]
            with p.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in fieldnames})
        else:
            p.write_text("", encoding="utf-8")
        out[name] = p

    # Followers / Followings raw
    write_csv("followers", followers_nodes)
    write_csv("followings", followings_nodes)

    # Derived CSVs (by username)
    idx_followers = _index_by_username(followers_nodes)
    idx_followings = _index_by_username(followings_nodes)

    def rows_from_usernames(names: list[str]) -> list[dict]:
        rows = []
        for u in names:
            rows.append(idx_followings.get(u) or idx_followers.get(u) or {"username": u})
        return rows

    for key in ["mutuals", "i_dont_follow_back", "not_following_back", "verified_not_following_back"]:
        rows = rows_from_usernames(sets[key])
        write_csv(key, rows)

    # JSON snapshot
    json_path = out_path / "snapshot.json"
    snapshot = {
        "username": username,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "counts": {k: len(sets[k]) for k in sets.keys()},
        "sets": sets,
        "followers": followers_nodes,
        "followings": followings_nodes,
    }
    json_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    out["snapshot_json"] = json_path

    # Markdown summary
    md_path = out_path / "summary.md"
    md = build_markdown_report(username, sets, followings_nodes)
    md_path.write_text(md, encoding="utf-8")
    out["summary_md"] = md_path

    # Plain text (compact)
    txt_path = out_path / f"Non_Abonne_En_Retour_De_{username}.txt"
    txt = []
    txt.append(f"{username}\n" + "=" * len(username) + "\n\n")
    for key, label in [
        ("mutuals", "Mutuals"),
        ("i_dont_follow_back", "I don't follow back"),
        ("not_following_back", "Not following back"),
        ("verified_not_following_back", "Not following back (verified)"),
    ]:
        names = sets[key]
        txt.append(f"{label} ({len(names)}):\n")
        for i, u in enumerate(names, 1):
            txt.append(f"  {i:>3}. {u}\n")
        txt.append("\n")
    (out_path / txt_path.name).write_text("".join(txt), encoding="utf-8")
    out["legacy_txt"] = txt_path

    return out

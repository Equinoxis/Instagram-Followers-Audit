from __future__ import annotations
import argparse
from pathlib import Path
from ig.client import load_cookies, make_session, get_user_id
from ig.scrape import get_followers_nodes, get_followings_nodes
from ig.report import write_all_outputs, build_sets

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Instagram followers/followings audit (private endpoints).")
    p.add_argument("-u", "--username", required=True, help="Instagram username to inspect")
    p.add_argument("-c", "--cookies", required=True, help="Path to JSON file with csrftoken, ds_user_id, sessionid")
    # intentionally NO output flag — always ./out/<username>/
    return p.parse_args()

def _print_summary(username: str, sets: dict) -> None:
    print(f"\nAudit for @{username}")
    print("=" * (12 + len(username)))
    rows = [
        ("Followers", len(sets["followers"])),
        ("Followings", len(sets["followings"])),
        ("Mutuals", len(sets["mutuals"])),
        ("I don't follow back", len(sets["i_dont_follow_back"])),
        ("Not following back", len(sets["not_following_back"])),
        ("Not following back (verified)", len(sets["verified_not_following_back"])),
    ]
    w = max(len(k) for k, _ in rows)
    for k, v in rows:
        print(f"{k.ljust(w)} : {v}")
    print()

def main() -> None:
    args = parse_args()
    cookies = load_cookies(args.cookies)

    # Always write under ./out/<username>/
    out_dir = Path("out") / args.username
    out_dir.mkdir(parents=True, exist_ok=True)

    with make_session(cookies) as session:
        uid = get_user_id(session, args.username)
        print(f"[info] User ID: {uid}")

        followers_nodes = get_followers_nodes(session, uid)
        followings_nodes = get_followings_nodes(session, uid)

        sets = build_sets(followers_nodes, followings_nodes)
        _print_summary(args.username, sets)

        outputs = write_all_outputs(args.username, followers_nodes, followings_nodes, out_dir)
        print("[ok] Files written:")
        for label, path in outputs.items():
            print(f"  - {label}: {Path(path).resolve()}")

if __name__ == "__main__":
    main()

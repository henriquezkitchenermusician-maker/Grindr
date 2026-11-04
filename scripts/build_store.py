#!/usr/bin/env python3
"""Genera store.json: tu fuente personal para SideStore/AltStore.

Une Plus+ (source.json de este repo) con las fuentes de UPSTREAMS.
Lo llama .github/workflows/store.yml. Si una fuente externa falla,
se conserva lo último que había de ella en store.json.
"""
import argparse
import json
import urllib.request
from pathlib import Path

UPSTREAMS = [
    # SideStore Team Picks: apps revisadas por el equipo de SideStore.
    "https://community-apps.sidestore.io/sidecommunity.json",
]

p = argparse.ArgumentParser()
p.add_argument("--repo", required=True)
p.add_argument("--branch", default="main")
p.add_argument("--out", default="store.json")
args = p.parse_args()

raw = f"https://raw.githubusercontent.com/{args.repo}/{args.branch}"
out = Path(args.out)
old = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
old_apps = {a.get("bundleIdentifier"): a for a in old.get("apps", [])}

own = json.loads(Path("source.json").read_text(encoding="utf-8"))
apps = list(own["apps"])
# La app instaladora Plus+ Store (la escribe build-store-app.yml).
if Path("store-app.json").exists():
    apps = json.loads(Path("store-app.json").read_text(encoding="utf-8"))["apps"] + apps
seen = {a["bundleIdentifier"] for a in apps}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "plus-store-builder"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


for url in UPSTREAMS:
    try:
        upstream_apps = fetch(url).get("apps", [])
        print(f"[ok]   {url}: {len(upstream_apps)} apps")
    except Exception as e:  # noqa: BLE001
        upstream_apps = [a for a in old_apps.values() if a.get("_from") == url]
        print(f"[warn] {url}: {e}; conservo {len(upstream_apps)} apps anteriores")
    for app in upstream_apps:
        bid = app.get("bundleIdentifier")
        if not bid or bid in seen or not app.get("versions"):
            continue
        seen.add(bid)
        apps.append({**app, "_from": url})

store = {
    "name": "Plus+ Store",
    "identifier": f"{own['identifier']}.store",
    "sourceURL": f"{raw}/store.json",
    "website": own.get("website", ""),
    "subtitle": "Plus+ y apps revisadas por SideStore",
    "description": "Fuente personal: Plus+ (basado en Open Grind) y las apps de SideStore Team Picks.",
    "tintColor": "#FFCC00",
    "iconURL": f"{raw}/icon.png",
    "apps": apps,
    "news": [],
}
out.write_text(json.dumps(store, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"store.json: {len(apps)} apps")

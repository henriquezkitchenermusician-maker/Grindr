#!/usr/bin/env python3
"""Añade la nueva compilación al principio de source.json (formato AltStore/SideStore).

Lo llama .github/workflows/build-ios.yml después de publicar cada Release.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

MAX_VERSIONS = 5

p = argparse.ArgumentParser()
for a in ("repo", "tag", "version", "build", "bundle-id", "min-os", "size", "commit"):
    p.add_argument(f"--{a}", required=True)
p.add_argument("--file", default="source.json")
p.add_argument("--branch", default="main")
args = p.parse_args()

owner, name = args.repo.split("/", 1)
raw = f"https://raw.githubusercontent.com/{args.repo}/{args.branch}"
path = Path(args.file)
src = json.loads(path.read_text(encoding="utf-8"))

src["sourceURL"] = f"{raw}/source.json"
src["website"] = f"https://github.com/{args.repo}"
src["identifier"] = f"io.github.{owner.lower()}.{name.lower()}"
app = src["apps"][0]
app["bundleIdentifier"] = args.bundle_id
app["iconURL"] = f"{raw}/icon.png"

entry = {
    "version": args.version,
    "buildVersion": args.build,
    "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "localizedDescription": f"Compilado del commit oficial {args.commit[:7]}.",
    "downloadURL": f"https://github.com/{args.repo}/releases/download/{args.tag}/OpenGrind.ipa",
    "size": int(args.size),
    "minOSVersion": args.min_os,
}
versions = [v for v in app.get("versions", []) if v.get("buildVersion") != args.build]
app["versions"] = [entry] + versions[: MAX_VERSIONS - 1]

path.write_text(json.dumps(src, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"source.json -> {args.version} ({args.build})")

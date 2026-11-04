#!/usr/bin/env python3
"""Cambia la marca de una copia de SideStore (AGPL-3.0) a "Plus+ Store".

Lo llama .github/workflows/build-store-app.yml en macOS antes de compilar.
Solo toca la copia temporal clonada. Usa `sips` (incluido en macOS) para
redimensionar el icono, así no necesita dependencias.

Uso: python3 rebrand.py <carpeta SideStore> <icon-1024.png> <org identifier>
"""
import re
import subprocess
import sys
from pathlib import Path

root, icon, org = Path(sys.argv[1]), Path(sys.argv[2]).resolve(), sys.argv[3]
DISPLAY_NAME = "Plus+ Store"

# 1) Iconos: sustituye cada PNG de cada .appiconset por el nuestro, al mismo tamaño.
count = 0
for png in root.glob("AltStore/Resources/Icons.xcassets/**/*.appiconset/*.png"):
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", str(png)], capture_output=True, text=True, check=True
    ).stdout
    size = int(re.search(r"pixelWidth:\s*(\d+)", out).group(1))
    subprocess.run(
        ["sips", "-z", str(size), str(size), str(icon), "--out", str(png)],
        capture_output=True, check=True,
    )
    count += 1
print(f"[icon] {count} imágenes reemplazadas")

# 2) Nombre visible bajo el icono.
plist = root / "AltStore/Info.plist"
s = plist.read_text()
if "CFBundleDisplayName" not in s:
    s = s.replace(
        "<key>CFBundleName</key>",
        f"<key>CFBundleDisplayName</key>\n\t<string>{DISPLAY_NAME}</string>\n\t<key>CFBundleName</key>",
        1,
    )
    plist.write_text(s)
print(f"[name] {DISPLAY_NAME}")

# 3) Identificador propio (evita chocar con el SideStore oficial).
for rel in ("Makefile", "Build.xcconfig"):
    f = root / rel
    t = f.read_text()
    t2 = re.sub(r"ORG_IDENTIFIER\s*=\s*com\.SideStore", f"ORG_IDENTIFIER = {org}", t)
    t2 = t2.replace("ORG_IDENTIFIER=com.SideStore", f"ORG_IDENTIFIER={org}")
    if t2 != t:
        f.write_text(t2)
        print(f"[id]   {rel}: {org}")

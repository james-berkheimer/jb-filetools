#!/usr/bin/env python3
import pathlib
import sys

version_path = pathlib.Path("VERSION")

if not version_path.exists():
    print("❌ VERSION file not found.")
    sys.exit(1)

current_version = version_path.read_text().strip()

try:
    major, minor, patch = map(int, current_version.split("."))
except ValueError:
    print(f"❌ Invalid version format: {current_version}. Expected format: X.Y.Z")
    sys.exit(1)

patch += 1
new_version = f"{major}.{minor}.{patch}"
version_path.write_text(new_version + "\n")

print(f"✅ Version bumped: {current_version} → {new_version}")

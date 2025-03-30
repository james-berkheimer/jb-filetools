#!/usr/bin/env python3
import pathlib
import sys

import toml

version_file_path = pathlib.Path("VERSION")
pyproject_path = pathlib.Path("pyproject.toml")

# Check file existence
if not version_file_path.exists():
    print("❌ VERSION file not found.")
    sys.exit(1)

if not pyproject_path.exists():
    print("❌ pyproject.toml file not found.")
    sys.exit(1)

# Load and compare versions
version_file = version_file_path.read_text().strip()
pyproject = toml.load(pyproject_path)
declared_version = pyproject.get("project", {}).get("version", "").strip()

if declared_version != version_file:
    print(f"❌ pyproject.toml version ({declared_version}) does not match VERSION file ({version_file})")
    sys.exit(1)

print(f"✅ Version check passed: {version_file}")

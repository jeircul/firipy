"""Utility to bump project version and roll the changelog release entries."""
from __future__ import annotations

import argparse
import datetime as _dt
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"
CHANGELOG = PROJECT_ROOT / "CHANGELOG.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--part",
        choices={"major", "minor", "patch"},
        default="patch",
        help="Semantic version component to increment (default: patch)",
    )
    group.add_argument(
        "--new-version",
        dest="new_version",
        help="Explicit version string to set (overrides --part)",
    )
    parser.add_argument(
        "--date",
        default=_dt.date.today().isoformat(),
        help="Release date for the changelog entry (default: today)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the would-be changes without modifying files.",
    )
    return parser.parse_args()


def bump_semver(current: str, part: str) -> str:
    try:
        major, minor, patch = [int(x) for x in current.split(".")]
    except ValueError as exc:  # pragma: no cover - defensive parsing
        raise SystemExit(f"Unrecognized version format: {current}") from exc
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def update_pyproject(new_version: str, *, dry_run: bool) -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    pattern = r'version\s*=\s*"(?P<version>[^"]+)"'
    match = re.search(pattern, text)
    if not match:
        raise SystemExit("Could not locate version field in pyproject.toml")
    current = match.group("version")
    if current == new_version:
        print(f"pyproject.toml already set to {new_version}")
        return
    new_text = (
        text[: match.start("version")] + new_version + text[match.end("version") :]
    )
    if dry_run:
        print(f"[dry-run] Would update pyproject.toml version: {current} -> {new_version}")
        return
    PYPROJECT.write_text(new_text, encoding="utf-8")
    print(f"Updated pyproject.toml version: {current} -> {new_version}")


def update_changelog(new_version: str, date: str, *, dry_run: bool) -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    pattern = r"## \[Unreleased\]\n+(.+?)(?=\n## \[)"
    match = re.search(pattern, text, flags=re.S)
    if not match:
        raise SystemExit("Could not locate 'Unreleased' section in CHANGELOG.md")
    preamble = text[: match.start()]
    unreleased_body = match.group(1).rstrip()
    remainder = text[match.end() :]
    if not unreleased_body.strip():
        print("Warning: Unreleased section is empty; creating placeholder release entry.")
    new_unreleased = "## [Unreleased]\n\n- Nothing yet.\n\n"
    new_release = (
        f"## [{new_version}] - {date}\n\n{unreleased_body}\n\n"
    )
    new_text = preamble + new_unreleased + new_release + remainder
    if dry_run:
        print("[dry-run] Would update CHANGELOG.md with new release header:")
        print(new_release)
        return
    CHANGELOG.write_text(new_text, encoding="utf-8")
    print(f"Recorded {new_version} in CHANGELOG.md")


def main() -> None:
    args = parse_args()
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"(?P<version>[^\"]+)"', text)
    if not match:
        raise SystemExit("Could not determine current version from pyproject.toml")
    current_version = match.group("version")
    new_version = args.new_version or bump_semver(current_version, args.part)
    print(f"Current version: {current_version}\nTarget version: {new_version}")
    update_pyproject(new_version, dry_run=args.dry_run)
    update_changelog(new_version, args.date, dry_run=args.dry_run)
    print("Done.")


if __name__ == "__main__":
    main()

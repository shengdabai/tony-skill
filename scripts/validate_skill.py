#!/usr/bin/env python3
"""Validate an Agent Skill repository without leaking sensitive values."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_BODY_LINES = 500
IGNORED_DIRECTORIES = {".git", ".omc", ".claude", ".codex", ".cache", ".next", ".pytest_cache", ".venv", "__pycache__", "build", "coverage", "dist", "node_modules", "target", "venv"}
REFERENCE_PATTERN = re.compile(r"(?<![A-Za-z0-9_./-])((?:references|examples)/[A-Za-z0-9._/-]+\.md)\b")
SENSITIVE_FILENAME_RULES = (
    ("SENSITIVE_FILENAME_ENV", re.compile(r"^\.env(?:\.(?!example$)[^/]+)?$", re.IGNORECASE)),
    (
        "SENSITIVE_FILENAME_AUTH",
        re.compile(
            r"^(?:auth\.json|credentials\.(?:json|ya?ml)|service[-_]account\.json)$",
            re.IGNORECASE,
        ),
    ),
    ("SENSITIVE_FILENAME_KEY", re.compile(r"(?:^id_(?:rsa|dsa|ecdsa|ed25519)$|\.(?:key|pem|p12|pfx)$)", re.IGNORECASE)),
    ("SENSITIVE_FILENAME_CONFIG", re.compile(r"^(?:\.npmrc|secrets?\.[^/]+)$", re.IGNORECASE)),
)
SECRET_PATTERNS = (
    ("SECRET_GITHUB_TOKEN", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("SECRET_OPENAI_KEY", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("SECRET_AWS_ACCESS_KEY", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    (
        "SECRET_ASSIGNED_VALUE",
        re.compile(
            r"(?i)\b(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|"
            r"db[_ -]?password|private[_ -]?key|secret|token|password)\b\s*[:=]\s*"
            r"(?:['\"])?([^\s'\"`#,;}]+)"
        ),
    ),
)
PLACEHOLDER_MARKERS = ("<", "{{", "${", "changeme", "dummy", "example", "fake", "not-a-real", "placeholder", "redacted", "replace", "sample", "test", "todo", "your_", "your-", "xxx")


def display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def add_error(errors: list[str], root: Path, path: Path, line: int, rule: str) -> None:
    errors.append(f"{display_path(root, path)}:{line}:{rule}")


def parse_frontmatter(skill_path: Path) -> tuple[dict[str, str], int, list[str]]:
    try:
        lines = skill_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return {}, 0, ["FRONTMATTER_UTF8"]
    except OSError:
        return {}, 0, ["FRONTMATTER_READ_ERROR"]
    if not lines or lines[0].strip() != "---":
        return {}, 0, ["FRONTMATTER_REQUIRED"]
    end = next((index for index, value in enumerate(lines[1:], 1) if value.strip() == "---"), None)
    if end is None:
        return {}, 0, ["FRONTMATTER_UNTERMINATED"]
    values: dict[str, str] = {}
    errors: list[str] = []
    index = 1
    while index < end:
        raw = lines[index]
        if not raw.strip() or raw.lstrip().startswith("#"):
            index += 1
            continue
        if raw[:1].isspace() or ":" not in raw:
            errors.append("FRONTMATTER_INVALID")
            index += 1
            continue
        key, value = (piece.strip() for piece in raw.split(":", 1))
        if key in values:
            errors.append("FRONTMATTER_DUPLICATE_KEY")
        values[key] = value
        if value in {"|", ">", "|-", ">-", "|+", ">+"}:
            continuation: list[str] = []
            index += 1
            while index < end and (not lines[index] or lines[index][:1].isspace()):
                continuation.append(lines[index].strip())
                index += 1
            values[key] = " ".join(piece for piece in continuation if piece).strip()
            continue
        index += 1
    return values, end + 1, errors


def is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or any(marker in normalized for marker in PLACEHOLDER_MARKERS)


def iter_repository_files(root: Path):
    for directory, subdirectories, filenames in os.walk(root, followlinks=False):
        current = Path(directory)
        # Prune before traversal, and yield links for diagnostics without following them.
        kept = []
        for name in subdirectories:
            if name in IGNORED_DIRECTORIES:
                continue
            path = current / name
            if path.is_symlink():
                yield path
            else:
                kept.append(name)
        subdirectories[:] = kept
        for name in filenames:
            if name not in IGNORED_DIRECTORIES:
                yield current / name


def validate_frontmatter(root: Path, errors: list[str]) -> None:
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        add_error(errors, root, skill_path, 1, "SKILL_FILE_REQUIRED")
        return
    fields, body_start, parse_errors = parse_frontmatter(skill_path)
    for rule in parse_errors:
        add_error(errors, root, skill_path, 1, rule)
    if not body_start:
        return
    unexpected = set(fields) - {"name", "description"}
    for _field in sorted(unexpected):
        add_error(errors, root, skill_path, 1, "FRONTMATTER_ONLY_NAME_DESCRIPTION")
    if set(fields) != {"name", "description"}:
        add_error(errors, root, skill_path, 1, "FRONTMATTER_NAME_DESCRIPTION_REQUIRED")
    name, description = fields.get("name", ""), fields.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        add_error(errors, root, skill_path, 1, "NAME_HYPHEN_CASE")
    if len(name) > MAX_NAME_LENGTH:
        add_error(errors, root, skill_path, 1, "NAME_TOO_LONG")
    if not description:
        add_error(errors, root, skill_path, 1, "DESCRIPTION_REQUIRED")
    if len(description) > MAX_DESCRIPTION_LENGTH:
        add_error(errors, root, skill_path, 1, "DESCRIPTION_TOO_LONG")
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if len(lines[body_start:]) >= MAX_BODY_LINES:
        add_error(errors, root, skill_path, body_start + MAX_BODY_LINES, "BODY_TOO_LONG")


def validate_references(root: Path, errors: list[str]) -> None:
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return
    try:
        text = skill_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        # Frontmatter validation already reports unreadable SKILL.md files.
        return
    mentioned: set[str] = set()
    for match in REFERENCE_PATTERN.finditer(text):
        relative = Path(match.group(1))
        line = text.count("\n", 0, match.start()) + 1
        try:
            candidate = (root / relative).resolve()
        except (OSError, RuntimeError):
            add_error(errors, root, skill_path, line, "REFERENCE_PATH_INVALID")
            continue
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            add_error(errors, root, skill_path, line, "REFERENCE_PATH_ESCAPES_ROOT")
            continue
        mentioned.add(relative.as_posix())
        if not candidate.is_file():
            add_error(errors, root, skill_path, line, "REFERENCE_PATH_MISSING")
    for directory_name, orphan_rule in (("references", "REFERENCE_ORPHANED"), ("examples", "EXAMPLE_ORPHANED")):
        directory = root / directory_name
        if directory.is_dir() and not directory.is_symlink():
            for document in sorted(path for path in iter_repository_files(directory) if path.suffix == ".md"):
                if document.relative_to(root).as_posix() not in mentioned:
                    add_error(errors, root, document, 1, orphan_rule)


def validate_sensitive_content(root: Path, errors: list[str]) -> None:
    for path in iter_repository_files(root):
        if path.is_symlink():
            add_error(errors, root, path, 1, "SYMLINK_NOT_ALLOWED")
            continue
        if not path.is_file():
            add_error(errors, root, path, 1, "NON_REGULAR_FILE")
            continue
        sensitive_rule = next((rule for rule, pattern in SENSITIVE_FILENAME_RULES if pattern.search(path.name)), None)
        if sensitive_rule is not None:
            add_error(errors, root, path, 1, sensitive_rule)
            # The filename is sufficient evidence; never open credential files.
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(lines, 1):
            for rule, pattern in SECRET_PATTERNS:
                for match in pattern.finditer(line):
                    value = match.group(1) if rule == "SECRET_ASSIGNED_VALUE" else match.group(0)
                    if not is_placeholder(value):
                        add_error(errors, root, path, line_number, rule)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not (root / "SKILL.md").is_symlink():
        validate_frontmatter(root, errors)
        validate_references(root, errors)
    validate_sensitive_content(root, errors)
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a public Agent Skill repository.")
    parser.add_argument("path", nargs="?", default=".", help="repository root (default: current directory)")
    args = parser.parse_args(argv)
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"{args.path}:1:REPOSITORY_ROOT_MISSING")
        return 1
    errors = validate(root)
    if errors:
        print("\n".join(errors))
        return 1
    print("skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

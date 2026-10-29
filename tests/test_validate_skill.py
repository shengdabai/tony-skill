from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
import validate_skill  # noqa: E402


class SkillValidatorTests(unittest.TestCase):
    def make_repository(self, *, frontmatter: str | None = None, body: str = "Use references/guide.md.") -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "references").mkdir()
        (root / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        frontmatter = frontmatter or "name: valid-skill\ndescription: A valid skill."
        (root / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{body}\n", encoding="utf-8")
        return root

    def rules(self, root: Path) -> set[str]:
        return {entry.rsplit(":", 1)[-1] for entry in validate_skill.validate(root)}

    def test_valid_skill_passes(self) -> None:
        self.assertEqual(validate_skill.validate(self.make_repository()), [])

    def test_frontmatter_contract_is_strict(self) -> None:
        root = self.make_repository(frontmatter="name: Invalid_Name\ndescription: \nlicense: MIT")
        rules = self.rules(root)
        self.assertTrue({"FRONTMATTER_ONLY_NAME_DESCRIPTION", "NAME_HYPHEN_CASE", "DESCRIPTION_REQUIRED"} <= rules)

    def test_overlong_description_and_body_fail(self) -> None:
        root = self.make_repository(
            frontmatter=f"name: valid-skill\ndescription: {'d' * 1025}",
            body="\n".join("line" for _ in range(500)),
        )
        rules = self.rules(root)
        self.assertTrue({"DESCRIPTION_TOO_LONG", "BODY_TOO_LONG"} <= rules)

    def test_missing_and_orphaned_references_fail(self) -> None:
        root = self.make_repository(body="Use references/missing.md and examples/missing.md.")
        rules = self.rules(root)
        self.assertTrue({"REFERENCE_PATH_MISSING", "REFERENCE_ORPHANED"} <= rules)

    def test_examples_must_be_routed_from_skill(self) -> None:
        root = self.make_repository()
        (root / "examples").mkdir()
        (root / "examples" / "walkthrough.md").write_text("# Walkthrough\n", encoding="utf-8")
        self.assertIn("EXAMPLE_ORPHANED", self.rules(root))

    def test_reference_path_cannot_escape_repository(self) -> None:
        root = self.make_repository(body="Use references/../../outside.md.")
        self.assertIn("REFERENCE_PATH_ESCAPES_ROOT", self.rules(root))

    def test_sensitive_filename_matrix(self) -> None:
        root = self.make_repository()
        for filename in (
            ".env",
            "auth.json",
            "credentials.json",
            "credentials.yml",
            "credentials.yaml",
            "service-account.json",
            "service_account.json",
            "id_rsa",
            "private.pem",
            ".npmrc",
            "secrets.yml",
        ):
            (root / filename).write_text("safe placeholder\n", encoding="utf-8")
        errors = validate_skill.validate(root)
        self.assertEqual(sum(error.endswith(":SENSITIVE_FILENAME_ENV") for error in errors), 1)
        self.assertEqual(sum(error.endswith(":SENSITIVE_FILENAME_AUTH") for error in errors), 6)
        self.assertEqual(sum(error.endswith(":SENSITIVE_FILENAME_KEY") for error in errors), 2)
        self.assertEqual(sum(error.endswith(":SENSITIVE_FILENAME_CONFIG") for error in errors), 2)

    def test_secret_diagnostics_do_not_echo_value(self) -> None:
        root = self.make_repository()
        value = "-".join(("very", "secret", "value", "123"))
        key_name = "private" + "_key"
        (root / "notes.md").write_text(f"{key_name}={value}\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(REPOSITORY_ROOT / "scripts" / "validate_skill.py"), str(root)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("notes.md:1:SECRET_ASSIGNED_VALUE", result.stdout)
        self.assertNotIn(value, result.stdout)

    def test_compound_assignment_names_are_detected(self) -> None:
        root = self.make_repository()
        names = (
            ("access", "_", "token"),
            ("access", "-", "token"),
            ("access", " ", "token"),
            ("client", "_", "secret"),
            ("client", "-", "secret"),
            ("client", " ", "secret"),
            ("db", "_", "password"),
            ("db", "-", "password"),
            ("db", " ", "password"),
            ("private", "_", "key"),
            ("private", "-", "key"),
            ("private", " ", "key"),
        )
        content = "\n".join(f"{first}{separator}{last}=live-value" for first, separator, last in names)
        (root / "compound-values.md").write_text(content, encoding="utf-8")
        errors = validate_skill.validate(root)
        self.assertEqual(sum(error.endswith(":SECRET_ASSIGNED_VALUE") for error in errors), len(names))

    def test_compound_placeholder_values_are_allowed(self) -> None:
        root = self.make_repository()
        names = (("access", "_", "token"), ("client", "-", "secret"), ("db", " ", "password"), ("private", "_", "key"))
        content = "\n".join(f"{first}{separator}{last}=your_value_here" for first, separator, last in names)
        (root / "documented-values.md").write_text(content, encoding="utf-8")
        self.assertEqual(validate_skill.validate(root), [])

    def test_non_assignment_near_matches_are_allowed(self) -> None:
        root = self.make_repository()
        (root / "notes.md").write_text("client_secretary=non-sensitive\naccess tokenization guide\n", encoding="utf-8")
        self.assertEqual(validate_skill.validate(root), [])

    def test_documented_placeholders_are_allowed(self) -> None:
        root = self.make_repository()
        (root / "docs.md").write_text("API_KEY=your_api_key_here\nTOKEN=<replace-me>\n", encoding="utf-8")
        self.assertEqual(validate_skill.validate(root), [])

    def test_invalid_utf8_skill_fails_without_traceback(self) -> None:
        root = self.make_repository()
        (root / "SKILL.md").write_bytes(b"---\nname: valid-skill\n\xff\n---\n")
        result = subprocess.run(
            [sys.executable, str(REPOSITORY_ROOT / "scripts" / "validate_skill.py"), str(root)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("SKILL.md:1:FRONTMATTER_UTF8", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_unreadable_skill_reports_error(self) -> None:
        root = self.make_repository()
        original_read = Path.read_text

        def read_text(path, *args, **kwargs):
            if path == root / "SKILL.md":
                raise PermissionError("unreadable fixture")
            return original_read(path, *args, **kwargs)

        with mock.patch.object(Path, "read_text", read_text):
            self.assertIn("FRONTMATTER_READ_ERROR", self.rules(root))

    def test_symlinks_are_rejected_without_reading_targets(self) -> None:
        for name, target_kind in (("linked.md", "file"), ("SKILL.md", "file"), ("references", "directory")):
            with self.subTest(name=name):
                root = self.make_repository()
                outside = self.make_repository()
                target = outside if target_kind == "directory" else outside / "SKILL.md"
                link = root / name
                if link.is_file():
                    link.unlink()
                elif link.is_dir():
                    # Keep existing fixtures, replacing only the directory entry.
                    link.rename(root / "original-references")
                link.symlink_to(target, target_is_directory=target_kind == "directory")
                original_read = Path.read_text
                reads = []

                def read_text(path, *args, **kwargs):
                    reads.append(path)
                    return original_read(path, *args, **kwargs)

                with mock.patch.object(Path, "read_text", read_text):
                    errors = validate_skill.validate(root)
                self.assertIn(f"{name}:1:SYMLINK_NOT_ALLOWED", errors)
                self.assertFalse(any(path.resolve().is_relative_to(outside) for path in reads))

    def test_placeholder_does_not_hide_later_assignment_on_same_line(self) -> None:
        root = self.make_repository()
        value = "-".join(("live", "value", "123"))
        name = "to" + "ken"
        (root / "notes.md").write_text(f"{name}=your_value_here; {name}={value}\n", encoding="utf-8")
        self.assertIn("notes.md:1:SECRET_ASSIGNED_VALUE", validate_skill.validate(root))

    def test_placeholder_does_not_hide_later_provider_token_on_same_line(self) -> None:
        root = self.make_repository()
        prefix = "gh" + "p_"
        (root / "notes.md").write_text(f"{prefix}{'x' * 24} {prefix}{'A' * 24}\n", encoding="utf-8")
        self.assertIn("notes.md:1:SECRET_GITHUB_TOKEN", validate_skill.validate(root))

    def test_sensitive_filenames_are_flagged_without_reading_contents(self) -> None:
        root = self.make_repository()
        sensitive = root / "credentials.json"
        sensitive.write_text("fixture only\n", encoding="utf-8")
        original_read = Path.read_text
        reads = []

        def read_text(path, *args, **kwargs):
            reads.append(path)
            return original_read(path, *args, **kwargs)

        with mock.patch.object(Path, "read_text", read_text):
            self.assertIn("SENSITIVE_FILENAME_AUTH", self.rules(root))
        self.assertNotIn(sensitive, reads)

    def test_broken_and_cyclic_symlinks_are_rejected(self) -> None:
        root = self.make_repository(body="Use references/guide.md and references/loop.md.")
        (root / "references" / "loop.md").symlink_to("loop.md")
        (root / "broken.md").symlink_to("missing.md")
        errors = validate_skill.validate(root)
        self.assertIn("references/loop.md:1:SYMLINK_NOT_ALLOWED", errors)
        self.assertIn("broken.md:1:SYMLINK_NOT_ALLOWED", errors)
        rules = {entry.rsplit(":", 1)[-1] for entry in errors}
        self.assertTrue({"REFERENCE_PATH_INVALID", "REFERENCE_PATH_MISSING"} & rules)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "named pipes require POSIX")
    def test_named_pipe_is_rejected_without_opening(self) -> None:
        root = self.make_repository()
        pipe = root / "stream.md"
        os.mkfifo(pipe)
        original_read = Path.read_text

        def read_text(path, *args, **kwargs):
            if path == pipe:
                self.fail("validator attempted to open a named pipe")
            return original_read(path, *args, **kwargs)

        with mock.patch.object(Path, "read_text", read_text):
            self.assertIn("stream.md:1:NON_REGULAR_FILE", validate_skill.validate(root))

    def test_local_tool_state_symlink_is_ignored(self) -> None:
        # Local agent hooks keep `.omc/state -> state.nosync`; that is not publishable skill material.
        root = self.make_repository()
        (root / ".omc").mkdir()
        (root / ".omc" / "state.nosync").mkdir()
        (root / ".omc" / "state").symlink_to("state.nosync")
        self.assertEqual(validate_skill.validate(root), [])

    def test_ignored_directories_are_not_traversed(self) -> None:
        root = self.make_repository()
        ignored = root / "node_modules"
        ignored.mkdir()
        (ignored / "credentials.json").write_text("fixture only\n", encoding="utf-8")
        original_scandir = os.scandir

        def scandir(path):
            self.assertNotEqual(Path(path), ignored)
            return original_scandir(path)

        with mock.patch.object(os, "scandir", scandir):
            self.assertEqual(validate_skill.validate(root), [])


if __name__ == "__main__":
    unittest.main()

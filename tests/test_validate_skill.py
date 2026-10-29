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
        content = "\n".join(("API_KEY=your_api_key_here", "TOKEN=<replace-me>"))
        (root / "docs.md").write_text(content, encoding="utf-8")
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

    def test_json_and_quoted_assignment_values_are_scanned(self) -> None:
        name = "to" + "ken"
        for content in (
            f'{{"{name}": "live-value-123"}}',
            f"{{'{name}': 'live-value-123'}}",
            f'{name}="two word value"',
            f"{name}='two word value'",
        ):
            with self.subTest(content=content):
                root = self.make_repository()
                (root / "settings.json").write_text(content + "\n", encoding="utf-8")
                self.assertIn("settings.json:1:SECRET_ASSIGNED_VALUE", validate_skill.validate(root))

    def test_placeholder_substrings_do_not_exempt_assigned_values(self) -> None:
        name = "to" + "ken"
        for marker in ("test", "example", "xxx", "dummy", "replace", "<", "${"):
            with self.subTest(marker=marker):
                root = self.make_repository()
                value = "AbC123" + marker + "ZyX987"
                (root / "notes.md").write_text(f"{name}={value}\n", encoding="utf-8")
                self.assertIn("notes.md:1:SECRET_ASSIGNED_VALUE", validate_skill.validate(root))

    def test_provider_tokens_cannot_use_placeholder_word_exemption(self) -> None:
        prefixes = (("gh" + "p_", "SECRET_GITHUB_TOKEN"), ("s" + "k-proj-", "SECRET_OPENAI_KEY"))
        for prefix, rule in prefixes:
            for body in ("test" + "A" * 24, "A" * 12 + "example" + "B" * 12):
                with self.subTest(prefix=prefix, body=body):
                    root = self.make_repository()
                    (root / "notes.md").write_text(prefix + body + "\n", encoding="utf-8")
                    self.assertIn(f"notes.md:1:{rule}", validate_skill.validate(root))

    def test_complete_placeholder_forms_still_pass(self) -> None:
        root = self.make_repository()
        name = "to" + "ken"
        placeholders = ('""', "your_value_here", "<replace-me>", "${TOKEN}", "{{TOKEN}}", "test-value", "x" * 24)
        (root / "notes.md").write_text("\n".join(f"{name}={value}" for value in placeholders), encoding="utf-8")
        self.assertEqual(validate_skill.validate(root), [])

    def test_whitespace_templates_in_workflows_are_allowed(self) -> None:
        names_and_values = (
            ("to" + "ken", "${{ secrets.GITHUB_TOKEN }}"),
            ("to" + "ken", "{{ token }}"),
            ("api" + "_key", "<your api key>"),
        )
        for name, value in names_and_values:
            for quote in ("", '"', "'"):
                with self.subTest(value=value, quote=quote):
                    root = self.make_repository()
                    workflow = root / ".github" / "workflows" / "check.yml"
                    workflow.parent.mkdir(parents=True)
                    workflow.write_text(f"{name}: {quote}{value}{quote}\n", encoding="utf-8")
                    self.assertEqual(validate_skill.validate(root), [])

    def test_unterminated_quoted_assignments_are_detected(self) -> None:
        name = "to" + "ken"
        value = "abcdef" + "123456"
        for quote in ('"', "'"):
            with self.subTest(quote=quote):
                root = self.make_repository()
                (root / "notes.md").write_text(f"{name}={quote}{value}\n", encoding="utf-8")
                errors = validate_skill.validate(root)
                self.assertEqual(errors, ["notes.md:1:SECRET_ASSIGNED_VALUE"])
                self.assertNotIn(value, "\n".join(errors))

    def test_whitespace_template_prefix_does_not_hide_assigned_suffix(self) -> None:
        name = "to" + "ken"
        for template in ("${{ secrets.GITHUB_TOKEN }}", "{{ token }}", "<your api key>"):
            with self.subTest(template=template):
                root = self.make_repository()
                (root / "notes.md").write_text(f"{name}={template}abcdef123456\n", encoding="utf-8")
                self.assertEqual(validate_skill.validate(root), ["notes.md:1:SECRET_ASSIGNED_VALUE"])

    def test_credential_documentation_and_public_key_names_are_allowed(self) -> None:
        root = self.make_repository()
        for name in ("credentials-guide.md", "credentials.md", "id_rsa.pub", "id_ed25519.pub"):
            (root / name).write_text("Public documentation fixture.\n", encoding="utf-8")
        self.assertEqual(validate_skill.validate(root), [])

    def test_allowed_credential_documentation_is_still_scanned(self) -> None:
        root = self.make_repository()
        name = "to" + "ken"
        (root / "credentials-guide.md").write_text(f"{name}=abcdef123456\n", encoding="utf-8")
        self.assertEqual(validate_skill.validate(root), ["credentials-guide.md:1:SECRET_ASSIGNED_VALUE"])

    def test_aws_documentation_example_is_allowed(self) -> None:
        root = self.make_repository()
        example = "AKIA" + "IOSFODNN7EXAMPLE"
        name = "access" + "_token"
        (root / "notes.md").write_text(f"{example}\n{name}={example}\n", encoding="utf-8")
        self.assertEqual(validate_skill.validate(root), [])

    def test_aws_example_suffix_does_not_exempt_other_keys(self) -> None:
        root = self.make_repository()
        value = "AKIA" + "A" * 9 + "EXAMPLE"
        (root / "notes.md").write_text(value + "\n", encoding="utf-8")
        self.assertEqual(validate_skill.validate(root), ["notes.md:1:SECRET_AWS_ACCESS_KEY"])

    def test_unreadable_content_file_fails_without_exception_details(self) -> None:
        root = self.make_repository()
        blocked = root / "notes.md"
        blocked.write_text("fixture only\n", encoding="utf-8")
        original_read = Path.read_text

        def read_text(path, *args, **kwargs):
            if path == blocked:
                raise PermissionError("sensitive exception detail")
            return original_read(path, *args, **kwargs)

        with mock.patch.object(Path, "read_text", read_text):
            self.assertEqual(validate_skill.validate(root), ["notes.md:1:FILE_READ_ERROR"])

    def test_unreadable_directory_fails_instead_of_being_skipped(self) -> None:
        root = self.make_repository()
        blocked = root / "inaccessible"
        blocked.mkdir()
        original_scandir = os.scandir

        def scandir(path):
            if Path(path) == blocked:
                raise PermissionError(13, "sensitive exception detail", str(blocked))
            return original_scandir(path)

        with mock.patch.object(os, "scandir", scandir):
            self.assertEqual(validate_skill.validate(root), ["inaccessible:1:DIRECTORY_READ_ERROR"])

    def test_skill_later_read_failures_are_reported(self) -> None:
        cases = (
            (PermissionError("sensitive exception detail"), "FRONTMATTER_READ_ERROR"),
            (UnicodeDecodeError("utf-8", b"\xff", 0, 1, "fixture"), "FRONTMATTER_UTF8"),
        )
        for failed_read in (2, 3):
            for exception, rule in cases:
                with self.subTest(failed_read=failed_read, rule=rule):
                    root = self.make_repository()
                    original_read = Path.read_text
                    skill_reads = 0

                    def read_text(path, *args, **kwargs):
                        nonlocal skill_reads
                        if path == root / "SKILL.md":
                            skill_reads += 1
                            if skill_reads == failed_read:
                                raise exception
                        return original_read(path, *args, **kwargs)

                    with mock.patch.object(Path, "read_text", read_text):
                        errors = validate_skill.validate(root)
                    self.assertEqual(errors, [f"SKILL.md:1:{rule}"])

    def test_credential_filename_variants_are_not_opened(self) -> None:
        root = self.make_repository()
        names = ("credentials", "credentials.txt", "credentials.backup.json", "id_rsa.bak", "id_ed25519.old")
        paths = {root / name for name in names}
        for path in paths:
            path.write_text("fixture only\n", encoding="utf-8")
        original_read = Path.read_text

        def read_text(path, *args, **kwargs):
            self.assertNotIn(path, paths, "credential filename was opened")
            return original_read(path, *args, **kwargs)

        with mock.patch.object(Path, "read_text", read_text):
            errors = validate_skill.validate(root)
        self.assertEqual(len(errors), len(paths))
        self.assertTrue(all(":SENSITIVE_FILENAME_" in error for error in errors))

    def test_private_key_headers_in_documents_are_rejected(self) -> None:
        header = "PRIVATE" + " KEY"
        for kind in ("", "RSA ", "DSA ", "EC ", "OPENSSH ", "ENCRYPTED "):
            with self.subTest(kind=kind):
                root = self.make_repository()
                (root / "notes.md").write_text(f"-----BEGIN {kind}{header}-----\n", encoding="utf-8")
                self.assertEqual(validate_skill.validate(root), ["notes.md:1:SECRET_PRIVATE_KEY"])


if __name__ == "__main__":
    unittest.main()

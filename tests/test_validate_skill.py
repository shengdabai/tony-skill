from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()

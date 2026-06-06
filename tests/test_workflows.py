import re
import unittest
from pathlib import Path


WORKFLOW_DIR = Path(__file__).resolve().parents[1] / ".github" / "workflows"
SHA_PINNED_ACTION = re.compile(r"uses:\s+[^\s@]+@[0-9a-f]{40}(?:\s+#\s+.+)?$")


class WorkflowSecurityPolicyTests(unittest.TestCase):
    def test_github_actions_uses_are_pinned_to_commit_shas(self):
        workflow_files = sorted(WORKFLOW_DIR.glob("*.yml"))
        self.assertTrue(workflow_files, "expected GitHub Actions workflow files")

        unpinned = []
        for workflow_file in workflow_files:
            for line_number, line in enumerate(workflow_file.read_text().splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("uses:") and not SHA_PINNED_ACTION.fullmatch(stripped):
                    unpinned.append(f"{workflow_file.name}:{line_number}: {stripped}")

        self.assertEqual(unpinned, [])


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from hub.actions import ActionError, load_all
from hub.actions.email import render
from hub.actions.folders import build_job_path, clean_name, new_job_folder
from hub.app import run_action

load_all()

INPUTS = {"customer": "Acme OEM", "job_number": "J-1001", "project_name": "Lift Station 3"}


class FolderTests(unittest.TestCase):
    def test_clean_name_strips_illegal_characters(self):
        self.assertEqual(clean_name('A/B:C*"D'), "A-B-C--D")
        with self.assertRaises(ActionError):
            clean_name("..")

    def test_user_input_cannot_escape_root(self):
        path = build_job_path("/root", "{customer}/{job_number}", {"customer": "../../etc", "job_number": "1"})
        self.assertEqual(path.parent.parent, Path("/root"))

    def test_creates_folder_tree_and_copies_template(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as tpl:
            Path(tpl, "Checklist.txt").write_text("x")
            config = {"job_folders": {
                "root": root,
                "pattern": "{customer}/{job_number} - {project_name}",
                "subfolders": ["01 Quote", "02 PO"],
                "template_source": tpl,
            }}
            msg = new_job_folder(INPUTS, config)
            job = Path(root, "Acme OEM", "J-1001 - Lift Station 3")
            self.assertTrue((job / "01 Quote").is_dir())
            self.assertTrue((job / "Checklist.txt").is_file())
            self.assertIn("copied 1 template file", msg)
            with self.assertRaises(ActionError):  # never overwrite an existing job
                new_job_folder(INPUTS, config)

    def test_required_fields_enforced(self):
        with self.assertRaises(ActionError):
            run_action("new_job_folder", {"customer": "Acme"}, {})


class EmailTests(unittest.TestCase):
    def test_render_fills_known_and_blanks_unknown(self):
        self.assertEqual(render("Job {job_number} {missing}", {"job_number": "J-1"}), "Job J-1 ")


if __name__ == "__main__":
    unittest.main()

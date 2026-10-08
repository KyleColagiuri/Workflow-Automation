import datetime
import tempfile
import unittest
from pathlib import Path

from hub.actions import ActionError, load_all
from hub.actions.email import text_snippet
from hub.actions.leads import new_rev_folder, sage_due_date, sage_request
from hub.actions.salesforce import add_months_end, sf_new_opp

load_all()


def make_o_drive(root):
    lead = Path(root, "2026", "L-1234 Acme - Lift Station")
    (lead / "Contract Dwgs & Specs" / "REV 0").mkdir(parents=True)
    (lead / "Contract Dwgs & Specs" / "REV 0" / "spec.pdf").write_text("x")
    Path(root, "2025", "L-1230 Older").mkdir(parents=True)
    return lead


class LeadFolderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.o = Path(self.tmp.name, "O")
        self.lead = make_o_drive(self.o)
        self.config = {"o_drive": {"root": str(self.o)}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_next_rev(self):
        out = new_rev_folder({"lead_number": "L-1234"}, self.config)
        self.assertTrue((self.lead / "Contract Dwgs & Specs" / "REV 1").is_dir())
        self.assertTrue(out["copy_text"].endswith("REV 1"))

    def test_lead_number_must_match_whole_prefix(self):
        with self.assertRaises(ActionError):
            new_rev_folder({"lead_number": "L-123"}, self.config)

    def test_finds_lead_in_older_year(self):
        new_rev_folder({"lead_number": "L-1230"}, self.config)
        self.assertTrue(Path(self.o, "2025", "L-1230 Older", "Contract Dwgs & Specs", "REV 0").is_dir())

    def test_sage_request_copies_and_builds_task(self):
        onedrive = Path(self.tmp.name, "OneDrive")
        onedrive.mkdir()
        self.config["sage"] = {"onedrive_root": str(onedrive), "priority_map": {"New Business": "Important"}}
        inputs = {"lead_number": "L-1234", "account": "Acme", "project_name": "Lift Station",
                  "bid_date": "2026-10-19", "priority": "New Business"}
        out = sage_request(inputs, self.config)
        copied = onedrive / "Acme" / self.lead.name / "Contract Dwgs & Specs" / "REV 0" / "spec.pdf"
        self.assertTrue(copied.is_file())
        self.assertIn("TASK TITLE: L-1234 - Acme - Lift Station", out["copy_text"])
        self.assertIn("DUE DATE:   10/16/2026", out["copy_text"])  # Monday bid -> Friday before
        self.assertIn("PRIORITY:   Important", out["copy_text"])
        with self.assertRaises(ActionError):  # never overwrite
            sage_request(inputs, self.config)


class DateTests(unittest.TestCase):
    def test_close_date_is_month_end(self):
        self.assertEqual(add_months_end(datetime.date(2026, 8, 31), 6), datetime.date(2027, 2, 28))

    def test_sage_due_skips_weekend(self):
        self.assertEqual(sage_due_date(datetime.date(2026, 10, 12)), datetime.date(2026, 10, 9))

    def test_new_opp_values(self):
        out = sf_new_opp({"city": "Austin", "state": "tx", "plant": "Walnut Creek WWTP",
                          "scope": "Control Panel", "bid_date": "2026-10-15"}, {"salesforce": {"estimator": "Me"}})
        self.assertIn("Austin, TX - Walnut Creek WWTP - Control Panel", out["copy_text"])
        self.assertIn("Close Date:       04/30/2027", out["copy_text"])


class SnippetTests(unittest.TestCase):
    def test_snippet_fills_values(self):
        out = text_snippet({"snippet": "s", "lead_number": "L-1"}, {"snippets": {"s": "Lead {lead_number}"}})
        self.assertEqual(out["copy_text"], "Lead L-1")


if __name__ == "__main__":
    unittest.main()

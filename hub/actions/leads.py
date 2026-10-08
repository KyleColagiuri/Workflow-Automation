"""Lead-folder actions on the O: drive and the SAGE (OneDrive) hand-off.

Folder layout these actions expect (all names configurable in config.json):

    O:\\<year>\\<lead# ...>\\Contract Dwgs & Specs\\REV 0, REV 1, ...
"""

import datetime
import re
import shutil
from pathlib import Path

from . import ActionError, action
from .email import render
from .folders import clean_name

_REV = re.compile(r"^REV\s*(\d+)$", re.IGNORECASE)


def _cfg(config):
    cfg = config.get("o_drive", {})
    if not cfg.get("root"):
        raise ActionError("Set o_drive.root in config.json (e.g. O:/).")
    if not Path(cfg["root"]).exists():
        raise ActionError(f"O: drive not reachable: {cfg['root']}")
    return cfg


def find_lead_folder(cfg, lead_number):
    """Find the lead folder whose name starts with the lead #, newest year first."""
    lead = clean_name(lead_number)
    root = Path(cfg["root"])
    years = sorted((p for p in root.iterdir() if p.is_dir() and p.name.isdigit()), reverse=True)
    for year in years:
        for folder in year.iterdir():
            if folder.is_dir() and re.match(rf"{re.escape(lead)}(\b|_|\s|-|$)", folder.name, re.IGNORECASE):
                return folder
    raise ActionError(f"No lead folder starting with '{lead}' found in any year folder under {root}.")


def rev_numbers(contract_dir):
    if not contract_dir.is_dir():
        return []
    return sorted(int(m.group(1)) for p in contract_dir.iterdir() if p.is_dir() and (m := _REV.match(p.name)))


@action(
    id="new_rev_folder",
    title="New REV Folder",
    description="Find the lead folder on the O: drive and create the next REV folder under "
    "Contract Dwgs & Specs (REV 0 for a new opp, the next number for a revision).",
    category="O: Drive",
    fields=[{"name": "lead_number", "label": "Lead #", "required": True}],
)
def new_rev_folder(inputs, config):
    cfg = _cfg(config)
    lead_dir = find_lead_folder(cfg, inputs["lead_number"])
    contract_dir = lead_dir / cfg.get("contract_folder", "Contract Dwgs & Specs")
    revs = rev_numbers(contract_dir)
    new = contract_dir / f"{cfg.get('rev_prefix', 'REV ')}{revs[-1] + 1 if revs else 0}"
    new.mkdir(parents=True)
    return {"message": f"Created {new}", "copy_text": str(new)}


def sage_due_date(bid_date, days_before=2):
    """Working day `days_before` days ahead of the bid date (weekends roll back to Friday)."""
    due = bid_date - datetime.timedelta(days=days_before)
    while due.weekday() >= 5:
        due -= datetime.timedelta(days=1)
    return due


@action(
    id="sage_request",
    title="SAGE Request",
    description="Copy the lead folder from the O: drive into the OneDrive Master Database "
    "(under the account), then build the Teams task title, due date, priority and message for you to paste.",
    category="O: Drive",
    fields=[
        {"name": "lead_number", "label": "Lead #", "required": True},
        {"name": "account", "label": "Account Name", "required": True},
        {"name": "project_name", "label": "Project Name", "required": True},
        {"name": "bid_date", "label": "Bid Date (blank = no due date)", "type": "date"},
        {"name": "due_date", "label": "Due Date set by Opp Owner (optional)", "type": "date"},
        {"name": "priority", "label": "Priority", "options": ["New Business", "Strategic Account", "Existing Customer"]},
        {"name": "notes", "label": "Notes for SAGE (optional)"},
    ],
)
def sage_request(inputs, config):
    cfg = _cfg(config)
    sage = config.get("sage", {})
    onedrive = sage.get("onedrive_root")
    if not onedrive or not Path(onedrive).exists():
        raise ActionError("Set sage.onedrive_root in config.json to your synced Master Database folder.")

    lead_dir = find_lead_folder(cfg, inputs["lead_number"])
    account_dir = Path(onedrive) / clean_name(inputs["account"])
    target = account_dir / lead_dir.name
    if target.exists():
        raise ActionError(f"Already in OneDrive: {target}")
    new_account = not account_dir.exists()
    shutil.copytree(lead_dir, target)

    contract_dir = target / cfg.get("contract_folder", "Contract Dwgs & Specs")
    revs = rev_numbers(contract_dir)
    rev_path = contract_dir / f"{cfg.get('rev_prefix', 'REV ')}{revs[-1]}" if revs else target

    if inputs.get("due_date"):
        due = datetime.date.fromisoformat(inputs["due_date"])
    elif inputs.get("bid_date"):
        due = sage_due_date(datetime.date.fromisoformat(inputs["bid_date"]), sage.get("days_before_bid", 2))
    else:
        due = None

    values = dict(inputs, path=str(rev_path), notes=inputs.get("notes", ""))
    title = render(sage.get("task_title", "{lead_number} - {account} - {project_name}"), values)
    priority = sage.get("priority_map", {}).get(inputs.get("priority", ""), inputs.get("priority", ""))
    body = render(sage.get("message_template", "Please start on this opportunity.\n{notes}\n\n{path}\n\nThanks,"), values)

    due_text = f"{due:%m/%d/%Y}" if due else "(set manually)"
    text = f"TASK TITLE: {title}\nDUE DATE:   {due_text}\nPRIORITY:   {priority}\n\n{body}"
    msg = f"Copied lead folder to {target}" + (" (new account folder created)" if new_account else "")
    return {"message": msg, "copy_text": text}

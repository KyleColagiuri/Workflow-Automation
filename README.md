# Workflow Automation Hub

A local web page of buttons. Each button runs a business process. It starts
simple (network drive and Outlook) and grows step by step into Salesforce,
Teams and SharePoint. See [ROADMAP.md](ROADMAP.md) for the plan.

## Setup (Windows, one time)
1. Install **Python 3.9 or newer** from python.org, or from the Microsoft Store /
   Company Portal if IT manages installs. Tick "Add Python to PATH".
2. Copy `config.example.json` to `config.json` and edit it:
   - `o_drive.root`: the O: drive (e.g. `O:/`), with year folders directly under it.
   - `sage.onedrive_root`: your synced *Master Database User Group - OEM* folder, and
     `sage.message_template`: put your SAGE contact's name in it.
   - `salesforce.estimator`: your name as it appears in Salesforce.
   - `job_folders.root`: your network drive jobs folder, e.g. `\\\\server\\share\\Jobs`
     (JSON needs doubled backslashes) or a mapped drive like `J:/Jobs`.
   - `job_folders.subfolders`: your standard folder structure.
   - `job_folders.template_source` (optional): a folder of documents to copy into every new job.
   - `email_templates`: your common emails. Use `{customer}`, `{job_number}`,
     `{project_name}` and `{contact_name}` as placeholders.
   - `quick_links`: your real Salesforce, SharePoint and Teams URLs.
3. Double-click **`start_hub.bat`**. The hub opens in your browser at http://127.0.0.1:8765.

There is nothing to `pip install`. The hub uses only Python's standard library.

## What's in it
| Button | What it does |
|---|---|
| New REV Folder | Finds the lead folder on the O: drive and creates the next `REV #` folder under Contract Dwgs & Specs. |
| SAGE Request | Copies the lead folder into the OneDrive Master Database under the account, then builds the Teams task title, due date, priority and message for you to copy. |
| New Opportunity Values | Works out the Salesforce name, amount, estimator, bid due date and close date. |
| Quote Dates | Today's date and the 60-day due date for the QuotePlan export. |
| Email From Template | Opens a filled-in Outlook draft (for example, the RFQ acknowledgement) for you to review and send. |
| Copy Text Snippet | Fills in text such as the proposal email body or a vendor quote request, ready to paste. |
| New Job Folder | Creates a general job folder with standard subfolders. It never overwrites an existing job. |
| Quick Links | Opens Salesforce, Teams, SharePoint and anything else you add. |

Buttons that produce text show it in a box with a **Copy** button.
See [docs/WORKFLOW_MAP.md](docs/WORKFLOW_MAP.md) for how each button fits your process.

Every run is logged to `logs/hub-YYYY-MM.log`.

## Adding a new button
Create a function in `hub/actions/` and decorate it:

```python
from . import action, ActionError

@action(id="my_task", title="My Task", description="What it does",
        category="Network Drive", fields=[{"name": "job_number", "label": "Job #", "required": True}])
def my_task(inputs, config):
    ...                      # do the work
    return "Done!"           # message shown under the button
```

Then import the module in `load_all()` in `hub/actions/__init__.py`.

## Safety
- The hub only listens on your own PC (127.0.0.1). Nobody else on the network can reach it.
- Other websites cannot trigger the buttons.
- Emails are opened as drafts and never sent automatically.
- `config.json` and `logs/` are excluded from git.

## Tests
```
python -m unittest discover -s tests
```

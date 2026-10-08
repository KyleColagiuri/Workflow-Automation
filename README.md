# Workflow Automation Hub

A local web page of buttons. Each button runs a business process. It starts
simple (network drive and Outlook) and grows step by step into Salesforce,
Teams and SharePoint. See [ROADMAP.md](ROADMAP.md) for the plan.

## Setup (Windows, one time)
1. Install **Python 3.9 or newer** from python.org, or from the Microsoft Store /
   Company Portal if IT manages installs. Tick "Add Python to PATH".
2. Copy `config.example.json` to `config.json` and edit it:
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
| New Job Folder | Creates `{year}/{customer}/{job#} - {project}` with your subfolders and template files. It never overwrites an existing job. |
| Email From Template | Opens a filled-in Outlook draft for you to review and send. |
| Quick Links | Opens Salesforce, Teams, SharePoint and anything else you add. |

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

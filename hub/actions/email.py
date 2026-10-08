"""Outlook actions: open pre-filled email drafts.

Uses the Outlook desktop app on Windows through PowerShell, so it needs no
extra installs and no IT app registration. Drafts are only *displayed* —
you always review and click Send yourself.
"""

import os
import platform
import subprocess

from . import ActionError, action

# Values are passed through environment variables, never pasted into the
# script text, so user input cannot break or inject into the PowerShell.
_PS_SCRIPT = r"""
$ol = New-Object -ComObject Outlook.Application
$mail = $ol.CreateItem(0)
$mail.To = $env:HUB_TO
$mail.CC = $env:HUB_CC
$mail.Subject = $env:HUB_SUBJECT
$mail.Body = $env:HUB_BODY
$mail.Display()
"""


class _Blank(dict):
    def __missing__(self, key):
        return ""


def render(text, inputs):
    """Fill {placeholders}; unknown placeholders become blank."""
    return text.format_map(_Blank(inputs))


def open_outlook_draft(to, cc, subject, body):
    if platform.system() != "Windows":
        raise ActionError("Outlook drafts only work on Windows with Outlook installed.")
    env = dict(os.environ, HUB_TO=to, HUB_CC=cc, HUB_SUBJECT=subject, HUB_BODY=body)
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", _PS_SCRIPT],
        env=env, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise ActionError("Outlook error: " + (result.stderr.strip() or "unknown"))


@action(
    id="email_from_template",
    title="Email From Template",
    description="Open an Outlook draft from one of your saved templates (quote follow-up, "
    "order acknowledgement, etc.). You review it and click Send.",
    category="Outlook",
    fields=[
        {"name": "template", "label": "Template", "required": True, "options_from": "email_templates"},
        {"name": "to", "label": "To", "required": True},
        {"name": "contact_name", "label": "Contact First Name"},
        {"name": "customer", "label": "Customer / OEM"},
        {"name": "job_number", "label": "Job / Quote #"},
        {"name": "project_name", "label": "Project Name"},
    ],
)
def email_from_template(inputs, config):
    templates = config.get("email_templates", {})
    tpl = templates.get(inputs.get("template", ""))
    if not tpl:
        raise ActionError(f"Unknown template. Available: {', '.join(templates) or 'none configured'}")
    open_outlook_draft(
        to=inputs["to"],
        cc=render(tpl.get("cc", ""), inputs),
        subject=render(tpl["subject"], inputs),
        body=render(tpl["body"], inputs),
    )
    return f"Opened Outlook draft: {render(tpl['subject'], inputs)}"


@action(
    id="text_snippet",
    title="Copy Text Snippet",
    description="Fill in a saved text block (proposal email body for Salesforce, vendor RFQ, etc.) "
    "and copy it to paste anywhere.",
    category="Outlook",
    fields=[
        {"name": "snippet", "label": "Snippet", "required": True, "options_from": "snippets"},
        {"name": "contact_name", "label": "Contact First Name"},
        {"name": "lead_number", "label": "Lead #"},
        {"name": "project_name", "label": "Proposal / Project Name"},
        {"name": "details", "label": "Extra Details (optional)"},
    ],
)
def text_snippet(inputs, config):
    snippets = config.get("snippets", {})
    text = snippets.get(inputs.get("snippet", ""))
    if text is None:
        raise ActionError(f"Unknown snippet. Available: {', '.join(snippets) or 'none configured'}")
    return {"message": "Ready to paste", "copy_text": render(text, inputs)}

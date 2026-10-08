# Automation Roadmap

The goal is a single hub where clicking a button runs a whole business process
across Salesforce, Outlook, Teams, SharePoint and the network drive. We get
there in steps. Each phase is useful by itself and builds on the one before it.

| Phase | What it automates | Needs IT? | Status |
|---|---|---|---|
| 1 | Network drive folders, Outlook drafts, quick links | No | **Built** |
| 2 | Teams notifications, SharePoint files (Power Automate) | Minimal | Next |
| 3 | Salesforce data (look up and update Accounts and Opportunities) | Yes | Planned |
| 4 | Chained "one-click" processes across all systems | Yes | Planned |
| 5 | Hands-free triggers, schedules, dashboards | Yes | Planned |

---

## Phase 1: Local wins, no approvals needed ✅
Runs on your own PC with plain Python. No new accounts, no API keys, nothing
that needs approval.

- **New Job Folder:** builds your standard folder tree on the network drive
  and copies in template documents (checklists, BOM template, etc.).
- **Email From Template:** opens a pre-filled Outlook draft. You review it and
  click Send.
- **Quick Links:** one place for your Salesforce, Teams and SharePoint pages.

Next small wins for this phase (pick what you do most often):
- Rename or file a PDF (PO, drawing) into the right job folder.
- Make a quote or transmittal document (Word or Excel) from a template, with the job details filled in.
- Find a job folder by customer or job number.
- Zip a submittal package and attach it to an Outlook draft.

## Phase 2: Microsoft 365 through Power Automate
Your M365 license probably already includes Power Automate, and it works with
Teams and SharePoint without custom code. The hub button calls a flow.

- Post a "new order" or "submittal sent" message to a Teams channel.
  Teams **Workflows** can make a webhook URL for this with a standard license.
- Create a SharePoint folder or document set for a job, or copy files from the network drive to SharePoint.
- Save email attachments from certain senders into the right folder automatically.

⚠️ The general "When an HTTP request is received" trigger is a **Premium**
connector. Ask IT what license you have before building flows that depend on it.

## Phase 3: Salesforce
- Look up an Account or Opportunity by name or number so you can **pre-fill hub
  forms** instead of typing.
- Update an Opportunity stage, or log an email or activity, from the hub.
- Options: the Salesforce REST API (needs a Connected App, which a Salesforce admin
  sets up), or the Power Automate Salesforce connector (Premium).

## Phase 4: One-click processes
These chain the earlier pieces together. Example: the **"New OEM Order"** button:
1. Pull the Opportunity from Salesforce and mark it Closed Won.
2. Create the job folder on the network drive and the SharePoint/Teams workspace.
3. Open the order acknowledgement email in Outlook.
4. Post the kickoff message in the Teams channel for engineering and production.

Other candidates: Quote Sent, Submittals Released, Order Shipped, Job Closeout.

## Phase 5: Hands-free
- Event triggers: when an Opportunity is Closed Won, run the New Order process with no click.
- Daily digests: open quotes needing follow-up and jobs waiting on submittal approval.
- A shared hub hosted for the team instead of on one PC.

---

## Talk to IT early
With the SJE acquisition, systems and policies may be changing. Before Phase 2 and 3, ask IT about:
- Power Automate licensing (standard or Premium) and data loss prevention (DLP) policies.
- Whether a Salesforce Connected App or API access is allowed for your user.
- Microsoft Entra ID (Azure AD) app registration, if we use the Microsoft Graph API directly.
- Where shared automations should live long term (a server, Azure, or Power Platform).

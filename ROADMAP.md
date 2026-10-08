# Automation Roadmap

The goal is a single hub where clicking a button runs a whole business process
across Salesforce, Outlook, Teams, SharePoint and the network drive. We get
there in steps. Each phase is useful by itself and builds on the one before it.

| Phase | What it automates | Needs IT? | Status |
|---|---|---|---|
| 1 | O: drive REV folders, SAGE hand-off, Salesforce field values, email text | No | **Built** |
| 1b | SAGE Return, review pack and checklist, finding the latest proposal PDF | No | Next |
| 2 | Teams tasks, Outlook folders and filing, PO/contact routing (Power Automate) | Minimal | Planned |
| 3 | Salesforce (create opportunities, BOM values, stage changes) | Yes | Planned |
| 4 | One-click "New RFQ" and "Submit Proposal" processes | Yes | Planned |
| 5 | Hands-free triggers, schedules, dashboards | Yes | Planned |

The step-by-step map of your real process, with what each step can become,
is in [docs/WORKFLOW_MAP.md](docs/WORKFLOW_MAP.md).

---

## Phase 1: Local wins, no approvals needed ✅
Runs on your own PC with plain Python. No new accounts, no API keys, nothing that needs approval.

- **New REV Folder:** finds the lead folder on the O: drive (newest year first) and creates the next REV folder.
- **SAGE Request:** copies the lead folder into the OneDrive Master Database under the account, then builds the
  Teams task title, due date (2 working days before the bid), priority and message for you to paste.
- **New Opportunity Values:** `City, ST - Plant - Scope` name, amount 9999, estimator, bid due date and close date.
- **Quote Dates:** today's date and the 60-day due date for the QuotePlan export.
- **Email From Template / Copy Text Snippet:** RFQ acknowledgement, proposal email body, vendor quote request.
- **New Job Folder / Quick Links:** the general-purpose buttons from the first version.

## Phase 1b: Next local buttons
- **SAGE Return:** copy the *From SAGE* folder from OneDrive back into the O: drive REV folder.
- **Review Pack:** open the SAGE proposal, the original RFQ and the specs at once, and show the review checklist
  (RFQ matches the quote, all hours, exceptions, vendor pricing), with a flag when the estimate is ≥ $150K and needs an SME review.
- **Latest Proposal:** find the newest PDF in *Proposals and Estimates* for the Salesforce upload.
- **Route Email:** pick a division and the hub opens a forward draft to the right contact.

## Phase 2: Microsoft 365 through Power Automate
Your M365 license probably already includes Power Automate, and it works with
Teams, Outlook and Planner without custom code. The hub button calls a flow.

- **Create the SAGE task in Teams automatically.** The Planner "Create a task" action is a standard connector.
- Create the `OEM FY<year> > Lead# - Proposal` Outlook folder and move the email into it.
- Save RFQ attachments to the lead folder.
- Route POs and contact-form emails to the right division contact.
- A reminder when a vendor hasn't replied within 24 hours.

⚠️ The general "When an HTTP request is received" trigger is a **Premium**
connector. Ask IT what license you have before building flows that depend on it.

## Phase 3: Salesforce
- Look up an Account or Opportunity by lead # so you can **pre-fill hub forms** instead of typing.
- Create or convert the opportunity with all the calculated fields filled in.
- Move the stage to Negotiation/Eval after a proposal goes out.
- Options: the Salesforce REST API (needs a Connected App, which a Salesforce admin
  sets up), or the Power Automate Salesforce connector (Premium).

## Phase 4: One-click processes
These chain the earlier pieces together. Example: the **"New RFQ"** button:
1. Create the opportunity in Salesforce with the calculated fields.
2. Create the REV 0 folder and save the RFQ attachments and email into it.
3. Send the acknowledgement reply and file the email.
4. For larger quotes, copy the folder to OneDrive and create the SAGE task in Teams.

Another candidate is **"Submit Proposal"**: find the latest PDF, send it with the email body, and move the opportunity stage.

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

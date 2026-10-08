# OEM Estimating Workflow Map

Built from the Miro flowchart (24-page PDF export). It covers the OEM
estimating process from an inbound request to a submitted proposal. People's
names are left out here; routing contacts live in your private `config.json`.

**Legend:** 🟢 the hub does it now · 🟡 next phase (Microsoft 365 / Power Automate) · 🔵 needs Salesforce access · ⚪ stays manual (needs judgement)

---

## 1. Sales@ inbox triage
Open the sales@ inbox → read the email → understand the request (if not, ask the account owner, customer or a subject-matter expert (SME)) →
create an Outlook folder `Inbox > OEM FY<year> > <Lead#> - <Proposal Name>` → if there are files, save them to the O: drive →
reply "Thank you for the opportunity to quote…" → file the email into the folder → **Inbound RFQ**

| Step | Automation |
|---|---|
| Understand the request | ⚪ |
| Create the Outlook folder and file the email | 🟡 Power Automate, or Outlook through the hub |
| Save attachments to the O: drive | 🟡 |
| Acknowledgement reply | 🟢 *Email From Template → RFQ Acknowledgement* |

## 2. Inbound RFQ: Salesforce case to opportunity
Salesforce → Revere Sales Console → open the case → enough info? (if not, set status *Requires more info* and email the owner or customer) →
fill out the case (contact, account, reason Quote/Proposal, type Custom System Proposal) → **Revision** or **New request**:

- **Revision:** Associate to Existing Opportunity → find the opp # → confirm.
- **New:** Convert to Opportunity → Eng System → set these fields:
  name `City, ST - Plant - Scope` · amount 9999 · owner · project type · estimator ·
  bid due date (default 1 week) · close date (end of month, 6 months after the bid) · lead source ·
  account · owner/end user · division.
- **Division:** Industrial → EMI → forward the RFQ email to the EMI contact. OEM → WTG → CCS decision (Excel sheet) →
  update the CCS portion if needed → Save → *the lead file is created on the O: drive*.

| Step | Automation |
|---|---|
| Work out the field values (name, dates, amount, estimator) | 🟢 *New Opportunity Values* |
| Create or convert the opportunity and set the fields | 🔵 Phase 3 |
| Forward Industrial RFQs to EMI | 🟡 routing rule |
| CCS decision from the Excel sheet | 🔵 or 🟡 the hub could read the sheet |

## 3. O: drive setup
O: drive → year → lead folder → Contract Dwgs & Specs → create the **REV** folder (REV 0 for a new opp, the next number for a revision) →
copy in the customer files → drag the RFQ email into the REV folder → drag the related emails into Correspondence.

| Step | Automation |
|---|---|
| Find the lead folder and create the next REV folder | 🟢 *New REV Folder* |
| Copy files and save emails into folders | 🟡 Power Automate, or Outlook through the hub |

## 4. Estimate: QuotePlan (small revision or quote)
QuotePlan → new or existing quote → BOM sync and copy → Input tab (lead #, project, description, customer, estimator, location, end user) →
create deliverables → make the changes from the RFQ → adjust margins from the margin sheet → update hours → check deliverables →
highlight what changed → lock the revision → set the revision name → Save → **export BOM values to Salesforce** →
export the proposal (QuotePlan quotation) or update the Word proposal → set the Rev #, today's date and a due date of +60 days → review → export the PDF to
`O:\<year>\<Lead#>\Proposals and Estimates`.

| Step | Automation |
|---|---|
| Quote date and 60-day due date | 🟢 *Quote Dates* |
| QuotePlan clicks | ⚪ for now. Ask the vendor whether QuotePlan has an API or import option. |
| Pricing, margins, hours, review | ⚪ judgement |

## 5. SAGE request (larger quotes)
Find the lead folder → copy it → paste it into the OneDrive *Master Database User Group – OEM* under the account (create the account folder if it's new) →
copy the REV folder path → fill out the message template → Teams → Master Database User Group → Estimate Requests → **Add task**:
title `Lead# - Account - Project`, due date (1–2 days before the bid date, or the date the opp owner set), priority
(New Business = Important, Strategic Account = what they request, Existing Customer = Medium) → paste the message into the task.

| Step | Automation |
|---|---|
| Copy the folder to OneDrive, create the account folder, build the title, due date, priority and message | 🟢 *SAGE Request* |
| Create the Teams task | 🟡 Power Automate (Planner "Create a task" is a standard connector) |

## 6. While SAGE works on it / vendor correspondence
Answer SAGE's questions (through the opp owner) → vendor quotes missing? Follow up with the vendor RFQ email, call after 24 hours, escalate if still no answer →
put the vendor quotes into the QuotePlan BOM and save them into the Vendor Quotes folder on the O: drive.

| Step | Automation |
|---|---|
| Vendor RFQ email text | 🟢 *Copy Text Snippet → Vendor Quote Request* |
| 24-hour follow-up reminder | 🟡 |
| Look up vendor contacts in the Excel sheet | 🟡 or 🟢 (a future "Vendor lookup" button) |

## 7. Work returned from SAGE, then review
Open the SAGE email → read the clarifications → drag the email into Correspondence → copy the *From SAGE* folder from OneDrive into the O: drive REV folder
(for some opp owners, create a shortcut instead) → open the SAGE proposal, the QuotePlan quote, the original RFQ and the specs → **review checklist**
(RFQ matches the quote; all hours: shop, project management, engineering, programming; exceptions and clarifications; vendor pricing) →
adjust → if the estimate is ≥ $150K, set up an SME review.

| Step | Automation |
|---|---|
| Copy *From SAGE* back to the O: drive REV folder | 🟢 next button: *SAGE Return* |
| Open every review document at once | 🟢 next button |
| Review checklist | 🟢 next: a checklist on the hub, saved to the lead folder |
| Book an SME review if ≥ $150K | 🟡 |

## 8. Proposal submission
In the Salesforce opp → Manage Bid → confirm account and contact → set branding to Revere → set the bid price → Send Proposal →
Email with External Proposal → attach the PDF from Proposals and Estimates → CC everyone on the original RFQ plus the opp owner →
email body → check again → Send → move the stage to **Negotiation/Eval**.

| Step | Automation |
|---|---|
| Email body | 🟢 *Copy Text Snippet → Proposal Submission* |
| Find the latest proposal PDF | 🟢 next button |
| Send the proposal and move the stage | 🔵 Phase 3 (the Manage Bid tool may be a custom package; needs a check) |

## 9. Inbound PO and contact-form routing
**PO:** sales@ → find the lead # or customer (look it up in Salesforce if it's missing) → EMI contact or OEM contact by division.
**Contact form:** check it's legitimate (if not, delete without clicking anything) → OEM, Municipal or EMI contact.

| Step | Automation |
|---|---|
| Forward to the right person | 🟡 a hub button now (pick the division, it opens a forward draft), then Power Automate |
| Look up the division in Salesforce | 🔵 |
| Legitimacy check | ⚪ (keep a person on this, because of phishing) |

---

## Biggest time savers, ranked
1. **SAGE Request** (built): about 10 manual steps become 1 click plus a paste.
2. **REV folder setup** (built): no more clicking through the O: drive.
3. **Opportunity field values** (built): no date math, consistent names.
4. **SAGE Return plus a review pack** (next): copy the folder back and open everything you need for review.
5. **Teams task creation** (Phase 2): removes the paste step from the SAGE request.
6. **Salesforce writes** (Phase 3): create the opp, export BOM values, move stages.

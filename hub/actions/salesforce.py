"""Salesforce helpers.

Phase 1 does not connect to Salesforce. It works out the values your process
sets by hand (opportunity name, dates, amount) so you can paste them in.
Phase 3 will write them straight into Salesforce.
"""

import calendar
import datetime

from . import action


def add_months_end(day, months):
    """Last day of the month `months` after `day`."""
    month_index = day.month - 1 + months
    year, month = day.year + month_index // 12, month_index % 12 + 1
    return datetime.date(year, month, calendar.monthrange(year, month)[1])


@action(
    id="sf_new_opp",
    title="New Opportunity Values",
    description="Work out the fields for a new Salesforce opportunity: name, amount, estimator, "
    "bid due date (default one week) and close date (end of month, 6 months after bid).",
    category="Salesforce",
    fields=[
        {"name": "city", "label": "City", "required": True},
        {"name": "state", "label": "State (initials)", "required": True},
        {"name": "plant", "label": "Plant / Site Name (blank if not a WWTP)"},
        {"name": "scope", "label": "What's Being Quoted", "required": True},
        {"name": "bid_date", "label": "Bid Due Date (blank = one week)", "type": "date"},
    ],
)
def sf_new_opp(inputs, config):
    sf = config.get("salesforce", {})
    today = datetime.date.today()
    bid = datetime.date.fromisoformat(inputs["bid_date"]) if inputs.get("bid_date") else today + datetime.timedelta(days=7)
    name_parts = [f"{inputs['city'].strip()}, {inputs['state'].strip().upper()}", inputs.get("plant", "").strip(), inputs["scope"].strip()]
    name = " - ".join(p for p in name_parts if p)
    lines = [
        f"Opportunity Name: {name}",
        f"Amount:           {sf.get('default_amount', 9999)}",
        f"Estimator:        {sf.get('estimator', '')}",
        f"Bid Due Date:     {bid:%m/%d/%Y}",
        f"Close Date:       {add_months_end(bid, sf.get('close_months_after_bid', 6)):%m/%d/%Y}",
        f"Project Type:     {sf.get('default_project_type', '')}",
    ]
    return {"message": f"Values ready for: {name}", "copy_text": "\n".join(lines)}


@action(
    id="quote_dates",
    title="Quote Dates",
    description="Quote date (today) and the 'valid until' date (60 days) for the QuotePlan export.",
    category="Salesforce",
)
def quote_dates(inputs, config):
    today = datetime.date.today()
    valid = today + datetime.timedelta(days=config.get("salesforce", {}).get("quote_valid_days", 60))
    return {"message": "Dates ready", "copy_text": f"Date:     {today:%m/%d/%Y}\nDue Date: {valid:%m/%d/%Y}"}

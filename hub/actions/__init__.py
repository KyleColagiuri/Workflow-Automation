"""Action registry.

Every button on the hub is an "action": a Python function plus a little
metadata describing the form fields it needs. Adding a new automation is
just writing a function and decorating it with @action.
"""

ACTIONS = {}


def action(id, title, description, fields=(), category="General"):
    """Register a function as a hub button.

    fields: list of dicts like {"name": "customer", "label": "Customer", "required": True}
    The decorated function receives (inputs: dict, config: dict) and returns a
    short message string describing what it did, or a dict with "message" and
    "copy_text" (text shown in a box with a Copy button). Raise ActionError for
    problems the user should see.
    """

    def wrap(fn):
        ACTIONS[id] = {
            "id": id,
            "title": title,
            "description": description,
            "category": category,
            "fields": list(fields),
            "run": fn,
        }
        return fn

    return wrap


class ActionError(Exception):
    """A user-facing error (bad input, missing config, etc.)."""


def load_all():
    # Importing the modules registers their actions.
    from . import email, folders, leads, salesforce  # noqa: F401

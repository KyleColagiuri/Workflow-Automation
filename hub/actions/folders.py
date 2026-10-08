"""Network-drive actions: create standard job folders."""

import datetime
import re
import shutil
from pathlib import Path

from . import ActionError, action

# Characters Windows does not allow in file/folder names.
_BAD_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def clean_name(value):
    """Make user input safe to use as a single folder name."""
    value = _BAD_CHARS.sub("-", str(value)).strip().rstrip(".")
    if not value or value in (".", ".."):
        raise ActionError("Name is empty or invalid after removing illegal characters.")
    return value


def build_job_path(root, pattern, inputs):
    """Fill the folder pattern, e.g. "{year}/{customer}/{job_number} - {project_name}"."""
    values = {k: clean_name(v) for k, v in inputs.items() if str(v).strip()}
    values.setdefault("year", str(datetime.date.today().year))
    parts = []
    for segment in re.split(r"[\\/]", pattern):
        try:
            parts.append(clean_name(segment.format(**values)))
        except KeyError as missing:
            raise ActionError(f"Missing value for {missing} in folder pattern.")
    return Path(root).joinpath(*parts)


@action(
    id="new_job_folder",
    title="New Job Folder",
    description="Create a standard job folder on the network drive with all subfolders "
    "(and copy in template documents if configured).",
    category="Network Drive",
    fields=[
        {"name": "customer", "label": "Customer / OEM", "required": True},
        {"name": "job_number", "label": "Job / Quote #", "required": True},
        {"name": "project_name", "label": "Project Name", "required": True},
    ],
)
def new_job_folder(inputs, config):
    cfg = config.get("job_folders", {})
    root = cfg.get("root")
    if not root:
        raise ActionError("Set job_folders.root in config.json (e.g. \\\\server\\share\\Jobs).")
    if not Path(root).exists():
        raise ActionError(f"Network location not reachable: {root}")

    job_path = build_job_path(root, cfg.get("pattern", "{customer}/{job_number} - {project_name}"), inputs)
    if job_path.exists():
        raise ActionError(f"Folder already exists: {job_path}")

    job_path.mkdir(parents=True)
    for sub in cfg.get("subfolders", []):
        (job_path / sub).mkdir(parents=True, exist_ok=True)

    copied = 0
    template = cfg.get("template_source")
    if template and Path(template).is_dir():
        shutil.copytree(template, job_path, dirs_exist_ok=True)
        copied = sum(1 for p in Path(template).rglob("*") if p.is_file())

    msg = f"Created {job_path}"
    if copied:
        msg += f" (copied {copied} template file{'s' if copied != 1 else ''})"
    return msg

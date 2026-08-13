from pathlib import Path
import ast
import requests
from env import API_KEY, API_ENDPOINT


MARKDOWN_WHITELIST = {
    "README.md",
    "knowledges/arc_reactor_status.md",
    "knowledges/avengers_directory.md",
    "knowledges/ironman_suite_inventory.md",
    "knowledges/lab_equipments_catalog.md",
    "knowledges/lab_security_policy.md",
}

IGNORED_DIRECTORIES = {".venv", "__pycache__"}

ALLOWED_TERMS = {
    "rule",
    "rules"
}

def check_security_policies(policy):
    """Check if the requested security policy is met."""
    if policy == 1:
        return check_markdown_files_against_whitelist()
    elif policy == 2:
        return check_system_prompt_contains_allowed_terms()
    else:
        raise ValueError(f"Unknown security policy: {policy}")


def check_markdown_files_against_whitelist():
    """Fail when any markdown file under ai_engineer is not explicitly whitelisted."""
    return len(get_unexpected_markdown_files()) == 0


def get_unexpected_markdown_files():
    """Return markdown files that exist on disk but are not in the whitelist."""
    project_root = Path(__file__).resolve().parents[1]

    normalized_whitelist = {
        path.replace("\\", "/").lower() for path in MARKDOWN_WHITELIST
    }

    discovered_files = set()
    for markdown_file in project_root.rglob("knowledges/*.md"):
        if any(part in IGNORED_DIRECTORIES for part in markdown_file.parts):
            continue

        relative_path = markdown_file.relative_to(project_root).as_posix().lower()
        discovered_files.add(relative_path)

    return sorted(discovered_files - normalized_whitelist)


def check_system_prompt_contains_allowed_terms():
    """Pass when SYSTEM_PROMPT in ai.py contains at least one allowed term."""
    system_prompt = get_system_prompt_from_ai_file()
    normalized_prompt = system_prompt.lower()
    return any(term.lower() in normalized_prompt for term in ALLOWED_TERMS)


def get_system_prompt_from_ai_file():
    """Read ai.py and extract the SYSTEM_PROMPT string without importing heavy dependencies."""
    ai_path = Path(__file__).with_name("ai.py")
    module = ast.parse(ai_path.read_text(encoding="utf-8"), filename=str(ai_path))

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "SYSTEM_PROMPT":
                return ast.literal_eval(node.value)

    raise ValueError("SYSTEM_PROMPT was not found in ai.py")

def update_dashboard(task_tag, is_restored):
    """Update the dashboard with the task status."""

    if not API_KEY or not API_ENDPOINT:
        print("Missing API configuration. Set API_KEY and API_ENDPOINT.")
        return

    headers = {
        'Authorization': f'Token {API_KEY}',
        'Content-Type': 'application/json'
    }
    body = {
        "card": "software_ai",
        "task": task_tag,
        "complete": is_restored
    }

    endpoint = f"{API_ENDPOINT.rstrip('/')}/task/update/"

    try:
        response = requests.post(endpoint, headers=headers, timeout=5, json=body)
        response.raise_for_status()
        print(f"Dashboard updated successfully for task '{task_tag}'.")
    except requests.RequestException as e:
        print(f"Error occurred while updating the dashboard: {e}")
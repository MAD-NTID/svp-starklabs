from pathlib import Path
import ast
import requests
import os


API_KEY = os.getenv('API_KEY')    
API_ENDPOINT = os.getenv('API_ENDPOINT')
APP_PATH = Path(__file__).with_name("app.py")

def check_security_policies():
    """Check if the requested security policy is met."""
    try:
        source = APP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return False

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "login":
            has_login_user_check = False
            has_database_lookup = False
            has_session_store = False
            has_dashboard_redirect = False

            for stmt in ast.walk(node):
                if isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Name) and stmt.test.id == "user":
                    has_login_user_check = True

                if (
                    isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id == "user"
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Attribute)
                    and stmt.value.func.attr == "get_user"
                    and len(stmt.value.args) == 2
                    and isinstance(stmt.value.args[0], ast.Name)
                    and stmt.value.args[0].id == "username"
                    and isinstance(stmt.value.args[1], ast.Name)
                    and stmt.value.args[1].id == "password"
                ):
                    has_database_lookup = True

                if (
                    isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Subscript)
                    and isinstance(stmt.targets[0].value, ast.Name)
                    and stmt.targets[0].value.id == "session"
                    and isinstance(stmt.targets[0].slice, ast.Constant)
                    and stmt.targets[0].slice.value == "user"
                ):
                    has_session_store = True

                if (
                    isinstance(stmt, ast.Return)
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Name)
                    and stmt.value.func.id == "redirect"
                    and len(stmt.value.args) == 1
                    and isinstance(stmt.value.args[0], ast.Constant)
                    and stmt.value.args[0].value == "/dashboard"
                ):
                    has_dashboard_redirect = True

            return has_login_user_check and has_database_lookup and has_session_store and has_dashboard_redirect

    return False


def update_dashboard(task_tag, is_restored):
    """Update the dashboard with the task status."""

    # try:
    #     import requests
    #     from env import API_KEY, API_ENDPOINT
    # except ImportError:
    #     print("Missing dashboard integration dependencies.")
    #     return

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
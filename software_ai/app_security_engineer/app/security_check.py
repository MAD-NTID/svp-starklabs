from pathlib import Path


HACKER_SNIPPET_MARKERS = (
    '#we will leave this in to skip the database check, this is easy for testing and debugging',
    '#if this match the testing login info we skip the database',
    'if username =="admin" and password =="adminTesting1234":',
)


def check_hacker_snippet_removed():
    """Read app.py and ensure the login function no longer contains the bypass snippet."""
    app_path = Path(__file__).with_name("app.py")
    app_lines = app_path.read_text(encoding="utf-8").splitlines()

    login_start = None
    for index, line in enumerate(app_lines):
        if line.startswith("def login():"):
            login_start = index
            break

    if login_start is None:
        raise ValueError("def login() was not found in app.py")

    login_lines = [app_lines[login_start]]
    for line in app_lines[login_start + 1:]:
        if line and not line.startswith((" ", "\t", "@")):
            break
        login_lines.append(line)

    login_function_code = "\n".join(login_lines)
    return not any(marker in login_function_code for marker in HACKER_SNIPPET_MARKERS)
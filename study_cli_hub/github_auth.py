# github_auth.py - GitHub Device Flow login and token-authenticated git sync
import json
import os
import stat
import subprocess
import time

import requests
from rich.panel import Panel

# Public OAuth App client ID (Device Flow enabled, no client secret needed -
# this is a public identifier, not a credential, so it's safe to commit).
# Registered at https://github.com/settings/developers under CLI Study Hub.
# Override via env var if you want to point at your own OAuth App instead:
#   export STUDY_HUB_GITHUB_CLIENT_ID=Iv1.xxxxxxxxxxxxxxxx
DEFAULT_GITHUB_CLIENT_ID = "Ov23liWI6vMmmSYK1N2U"
GITHUB_CLIENT_ID = os.environ.get("STUDY_HUB_GITHUB_CLIENT_ID", DEFAULT_GITHUB_CLIENT_ID)

DEVICE_CODE_URL = "https://github.com/login/device/code"
TOKEN_URL = "https://github.com/login/oauth/access_token"
USER_API_URL = "https://api.github.com/user"
SCOPE = "repo"


def config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    path = os.path.join(base, "study-cli-hub")
    os.makedirs(path, exist_ok=True)
    return path


_config_dir = config_dir  # kept for any existing internal call sites


def _config_file():
    return os.path.join(config_dir(), "credentials.json")


def save_token(data):
    path = _config_file()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def load_token():
    path = _config_file()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def clear_token():
    path = _config_file()
    if os.path.exists(path):
        os.remove(path)


def is_configured():
    return bool(GITHUB_CLIENT_ID)


def login(console):
    """Run the GitHub Device Flow and store the resulting token."""
    if not is_configured():
        console.print(Panel(
            "[bold red]GitHub login isn't configured yet[/bold red]\n\n"
            "STUDY_HUB_GITHUB_CLIENT_ID is set to an empty value in this "
            "environment, overriding the built-in default. Unset it, or "
            "point it at your own OAuth App (Device Flow enabled).\n"
            "See the README's '/login's OAuth App' section.",
            expand=False,
        ))
        return False

    try:
        resp = requests.post(
            DEVICE_CODE_URL,
            data={"client_id": GITHUB_CLIENT_ID, "scope": SCOPE},
            headers={"Accept": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as e:
        console.print(f"[red]Could not reach GitHub: {e}[/red]")
        return False

    device_code = payload["device_code"]
    user_code = payload["user_code"]
    verification_uri = payload["verification_uri"]
    interval = payload.get("interval", 5)
    expires_in = payload.get("expires_in", 900)

    console.print(Panel(
        f"[bold cyan]🔗 Connect your GitHub account[/bold cyan]\n\n"
        f"1. Open [bold]{verification_uri}[/bold] in a browser\n"
        f"2. Enter this code: [bold yellow]{user_code}[/bold yellow]\n\n"
        f"[dim]Waiting for you to approve...[/dim]",
        expand=False,
    ))

    deadline = time.time() + expires_in
    while time.time() < deadline:
        time.sleep(interval)
        try:
            token_resp = requests.post(
                TOKEN_URL,
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                headers={"Accept": "application/json"},
                timeout=15,
            )
            token_payload = token_resp.json()
        except requests.RequestException as e:
            console.print(f"[red]Could not reach GitHub: {e}[/red]")
            return False

        error = token_payload.get("error")
        if error == "authorization_pending":
            continue
        elif error == "slow_down":
            interval = token_payload.get("interval", interval + 5)
            continue
        elif error == "expired_token":
            console.print("[red]Login code expired. Run /login again.[/red]")
            return False
        elif error == "access_denied":
            console.print("[yellow]Login cancelled.[/yellow]")
            return False
        elif error:
            console.print(f"[red]GitHub login failed: {error}[/red]")
            return False

        access_token = token_payload["access_token"]
        break
    else:
        console.print("[red]Login timed out. Run /login again.[/red]")
        return False

    try:
        user_resp = requests.get(
            USER_API_URL,
            headers={"Authorization": f"token {access_token}"},
            timeout=15,
        )
        user_resp.raise_for_status()
        username = user_resp.json()["login"]
    except requests.RequestException:
        username = None

    save_token({"access_token": access_token, "login": username})
    console.print(f"[green]✅ Logged in to GitHub as {username or 'unknown user'}[/green]")
    return True


def logout(console):
    clear_token()
    console.print("[green]✅ Logged out of GitHub[/green]")


def whoami(console):
    token = load_token()
    if not token:
        console.print("[yellow]⚠️ Not logged in. Run /login to connect your GitHub account.[/yellow]")
        return
    console.print(f"[cyan]👤 Logged in as:[/cyan] {token.get('login', 'unknown')}")


def _authenticated_url(remote_url, access_token):
    if remote_url.startswith("https://"):
        return remote_url.replace("https://", f"https://x-access-token:{access_token}@", 1)
    return remote_url


def git_pull(cwd=None):
    """Pull latest changes, using the stored GitHub token if available."""
    return _run_authenticated(["git", "pull", "--rebase"], cwd)


def git_push(cwd=None):
    """Push local commits, using the stored GitHub token if available."""
    return _run_authenticated(["git", "push"], cwd)


def _run_authenticated(git_args, cwd):
    cwd = cwd or os.getcwd()
    token_data = load_token()

    if not token_data:
        return subprocess.run(git_args, capture_output=True, text=True, cwd=cwd)

    remote_result = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True, cwd=cwd
    )
    if remote_result.returncode != 0:
        return subprocess.run(git_args, capture_output=True, text=True, cwd=cwd)

    original_url = remote_result.stdout.strip()
    auth_url = _authenticated_url(original_url, token_data["access_token"])

    if auth_url == original_url:
        return subprocess.run(git_args, capture_output=True, text=True, cwd=cwd)

    subprocess.run(["git", "remote", "set-url", "origin", auth_url], capture_output=True, text=True, cwd=cwd)
    try:
        return subprocess.run(git_args, capture_output=True, text=True, cwd=cwd)
    finally:
        subprocess.run(["git", "remote", "set-url", "origin", original_url], capture_output=True, text=True, cwd=cwd)

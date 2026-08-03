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
    """Run the GitHub Device Flow and store the resulting token.

    Scope, guaranteed: this only ever reads/writes this app's own token
    file (config_dir()/credentials.json). It never touches `gh`'s own auth
    state, git's global/local config, your SSH keys, browser sessions, or
    any other terminal - logging in or out here has zero effect anywhere
    else on your machine."""
    existing = load_token()
    if existing:
        console.print(Panel(
            f"[yellow]Already connected as @{existing.get('login', 'unknown')} "
            "(within this app only).[/yellow]\n\n"
            "Run [bold]/logout[/bold] first if you want to switch accounts - "
            "that only disconnects this app, nothing else.",
            expand=False,
        ))
        return True

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
    except (requests.RequestException, ValueError) as e:
        console.print(f"[red]Could not reach GitHub: {e}[/red]")
        return False

    device_code = payload["device_code"]
    user_code = payload["user_code"]
    verification_uri = payload["verification_uri"]
    interval = payload.get("interval", 5)
    expires_in = payload.get("expires_in", 900)

    token_file_path = os.path.join(config_dir(), "credentials.json")
    console.print(Panel(
        f"[bold cyan]🔗 Connect your GitHub account to CLI Study Hub[/bold cyan]\n\n"
        f"1. Open [bold]{verification_uri}[/bold] in any browser (phone or laptop, doesn't need to be this machine)\n"
        f"2. Enter this code: [bold yellow]{user_code}[/bold yellow]\n"
        f"3. Click Approve\n\n"
        f"[dim]This only signs you into this app. It stores its own token at "
        f"{token_file_path} and never touches gh, git's global config, your "
        f"SSH keys, or any other terminal/app session.[/dim]\n\n"
        "[dim]Waiting for you to approve...[/dim]",
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
        except (requests.RequestException, ValueError):
            # A single transient network/response hiccup shouldn't abort
            # the whole login while you're mid-approving in the browser -
            # just retry on the next poll. Only the overall deadline
            # (expires_in, checked by the while condition) gives up for real.
            continue

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
    """Clears only this app's own stored token. Does not sign you out of
    GitHub itself, `gh`, git, your browser, or any other terminal/app -
    there is nothing else here to log out of."""
    if not load_token():
        console.print("[yellow]Not logged in to CLI Study Hub - nothing to do.[/yellow]")
        return
    clear_token()
    console.print(
        "[green]✅ Logged out of CLI Study Hub.[/green] "
        "[dim]Your GitHub account, gh CLI, and git credentials elsewhere are untouched.[/dim]"
    )


def whoami(console):
    token = load_token()
    if not token:
        console.print("[yellow]⚠️ Not logged in. Run /login to connect your GitHub account.[/yellow]")
        return
    console.print(f"[cyan]👤 Logged in as:[/cyan] {token.get('login', 'unknown')} [dim](this app only)[/dim]")


def git_pull(cwd=None):
    """Pull latest changes, using the stored GitHub token if available."""
    return _run_authenticated(["git", "pull", "--rebase"], cwd)


def git_push(cwd=None):
    """Push local commits, using the stored GitHub token if available."""
    return _run_authenticated(["git", "push"], cwd)


def _run_authenticated(git_args, cwd):
    """Runs a git command, injecting the stored token via a one-shot
    credential helper that lives only in this single subprocess call's
    environment and command-line config override (`git -c ...`) - never
    written to .git/config, ~/.gitconfig, the keychain, or anywhere else on
    disk. Nothing persists after the call returns, and there's nothing left
    behind even if the process were killed mid-operation. This also means
    it can never touch `gh`'s own auth, SSH keys, or any other app/terminal
    session - it's entirely local to this one command."""
    cwd = cwd or os.getcwd()
    token_data = load_token()

    if not token_data:
        return subprocess.run(git_args, capture_output=True, text=True, cwd=cwd)

    env = dict(os.environ)
    env["STUDY_CLI_HUB_GIT_TOKEN"] = token_data["access_token"]
    credential_helper = '!f() { echo username=x-access-token; echo "password=$STUDY_CLI_HUB_GIT_TOKEN"; }; f'

    full_args = [git_args[0], "-c", f"credential.helper={credential_helper}"] + list(git_args[1:])
    return subprocess.run(full_args, capture_output=True, text=True, cwd=cwd, env=env)

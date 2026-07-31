# contribute.py - fork + pull-request fallback for GitHub users who aren't
# collaborators on this repo. Using the app should be hassle-free for
# anyone: if you can't push directly, the CLI forks the repo under your own
# account, pushes your subjects/** changes there, and opens (or updates) a
# PR back to the upstream repo. .github/workflows/auto-merge-data-prs.yml
# then auto-approves and auto-merges it, since it only touches subjects/**.
import subprocess
import time

import requests

from study_cli_hub import github_auth

API_URL = "https://api.github.com"
REPO_OWNER = "govindmehta15"
REPO_NAME = "study-cli-hub"
BASE_BRANCH = "main"


def _headers(token):
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}


def has_push_access():
    """Does the logged-in user have push access to the upstream repo? None
    means we couldn't tell (not logged in, or the API call failed) - callers
    should treat that like "no", since we can't prove otherwise."""
    token_data = github_auth.load_token()
    if not token_data:
        return None
    try:
        resp = requests.get(
            f"{API_URL}/repos/{REPO_OWNER}/{REPO_NAME}", headers=_headers(token_data["access_token"]), timeout=15
        )
        resp.raise_for_status()
        return bool(resp.json().get("permissions", {}).get("push"))
    except requests.RequestException:
        return None


def sync_branch_name(username):
    return f"sync-{username}"


def ensure_fork(username, token, attempts=10, delay=1.5):
    """Fork the repo under the user's account (idempotent - if it already
    exists, GitHub just returns it). Forks are created asynchronously, so
    poll briefly until the fork is actually reachable."""
    try:
        requests.post(
            f"{API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/forks", headers=_headers(token), timeout=15
        )
    except requests.RequestException as e:
        return None, f"Could not reach GitHub to fork the repo: {e}"

    for _ in range(attempts):
        try:
            resp = requests.get(f"{API_URL}/repos/{username}/{REPO_NAME}", headers=_headers(token), timeout=15)
            if resp.status_code == 200:
                return resp.json()["full_name"], None
        except requests.RequestException:
            pass
        time.sleep(delay)
    return None, "Timed out waiting for your fork to become ready. Try /sync again in a moment."


def push_to_fork(fork_full_name, branch_name, token, cwd=None):
    cwd = cwd or None
    fork_url = f"https://x-access-token:{token}@github.com/{fork_full_name}.git"
    subprocess.run(["git", "remote", "remove", "fork"], capture_output=True, text=True, cwd=cwd)
    subprocess.run(["git", "remote", "add", "fork", fork_url], capture_output=True, text=True, cwd=cwd)
    result = subprocess.run(
        ["git", "push", "--force", "fork", f"HEAD:refs/heads/{branch_name}"],
        capture_output=True, text=True, cwd=cwd,
    )
    # Don't leave the token sitting in the repo's git config longer than needed.
    subprocess.run(["git", "remote", "remove", "fork"], capture_output=True, text=True, cwd=cwd)
    return result


def find_open_pr(username, branch_name, token):
    try:
        resp = requests.get(
            f"{API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls",
            headers=_headers(token),
            params={"head": f"{username}:{branch_name}", "state": "open"},
            timeout=15,
        )
        resp.raise_for_status()
        prs = resp.json()
        return prs[0]["html_url"] if prs else None
    except requests.RequestException:
        return None


def open_pr(username, branch_name, token, title, body):
    try:
        resp = requests.post(
            f"{API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls",
            headers=_headers(token),
            json={"title": title, "body": body, "head": f"{username}:{branch_name}", "base": BASE_BRANCH},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["html_url"], None
    except requests.RequestException as e:
        detail = ""
        if e.response is not None:
            try:
                detail = f" ({e.response.json().get('message', '')})"
            except ValueError:
                pass
        return None, f"Could not open a pull request: {e}{detail}"


def contribute_via_fork(cwd=None):
    """Full fallback flow for a logged-in user without push access. Returns
    (pr_url, error)."""
    token_data = github_auth.load_token()
    if not token_data:
        return None, "Not logged in. Run /login first."
    username = token_data.get("login")
    token = token_data["access_token"]
    if not username:
        return None, "Could not determine your GitHub username."

    fork_full_name, err = ensure_fork(username, token)
    if err:
        return None, err

    branch_name = sync_branch_name(username)
    push_result = push_to_fork(fork_full_name, branch_name, token, cwd=cwd)
    if push_result.returncode != 0:
        return None, f"Could not push to your fork: {push_result.stderr.strip()}"

    existing = find_open_pr(username, branch_name, token)
    if existing:
        return existing, None

    return open_pr(
        username,
        branch_name,
        token,
        title=f"Study notes from @{username}",
        body=(
            f"Notes synced from @{username} via CLI Study Hub's `/sync`.\n\n"
            "This only touches `subjects/**`, so it should auto-merge shortly."
        ),
    )

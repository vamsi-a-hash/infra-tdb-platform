import json
import os
import subprocess
import tempfile
from pathlib import Path

import yaml

REPOS_FILE = Path("local/repo.yaml")


def run(cmd, cwd=None, capture_output=False):
    """Run a shell command."""
    print(">", " ".join(map(str, cmd)))

    if capture_output:
        return subprocess.check_output(cmd, cwd=cwd).decode().strip()

    subprocess.run(cmd, cwd=cwd, check=True)


def load_repos():
    """
    Load repositories either from REPOS_JSON
    or from local/repo.yaml for local development.
    """
    repos_json = os.getenv("REPOS_JSON")

    try:
        return json.loads(repos_json)
    except:
        data = yaml.safe_load(REPOS_FILE.read_text())

        return [
            {
                "url": url,
                "branch": "main",
            }
            for url in data.get("repos", [])
        ]


def extract_name(url):
    return url.rstrip("/").split("/")[-1].replace(".git", "")


def git_clone(url, branch, destination):
    run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "-b",
            branch,
            url,
            str(destination),
        ]
    )


def set_git_auth(repo_path, url, token):
    auth_url = url.replace(
        "https://",
        f"https://x-access-token:{token}@",
    )

    run(
        [
            "git",
            "remote",
            "set-url",
            "origin",
            auth_url,
        ],
        cwd=repo_path,
    )


def configure_git_identity(repo_path):
    run(
        [
            "git",
            "config",
            "user.name",
            "github-actions[bot]",
        ],
        cwd=repo_path,
    )

    run(
        [
            "git",
            "config",
            "user.email",
            "github-actions[bot]@users.noreply.github.com",
        ],
        cwd=repo_path,
    )


def has_changes(repo_path):
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return bool(status.stdout.strip())


def commit_if_needed(repo_path, message):
    if not has_changes(repo_path):
        print("No changes detected.")
        return False

    run(["git", "add", "."], cwd=repo_path)
    run(["git", "commit", "-m", message], cwd=repo_path)
    run(["git", "push"], cwd=repo_path)

    return True


def current_commit(repo_path):
    return run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=repo_path,
        capture_output=True,
    )


def temporary_workspace():
    """
    Usage:

    with temporary_workspace() as workspace:
        ...
    """
    return tempfile.TemporaryDirectory()


def clone_repository(workspace, repo):
    """
    Clone a repository into a temporary directory.

    Returns:
        (repo_path, repo_name)
    """

    repo_name = extract_name(repo["url"])

    repo_path = Path(workspace.name) / repo_name

    git_clone(
        repo["url"],
        repo.get("branch", "main"),
        repo_path,
    )

    token = os.environ["GH_PAT"]

    set_git_auth(
        repo_path,
        repo["url"],
        token,
    )

    configure_git_identity(repo_path)

    return repo_path, repo_name


def run_python(script, *args, cwd=None):
    run(
        [
            "python",
            script,
            *args,
        ],
        cwd=cwd,
    )

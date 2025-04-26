import os
import subprocess
import functools
import shutil
from typing import Optional


@functools.lru_cache()
def get_github_token(host: str) -> Optional[str]:
    """
    Retrieve the GitHub token using various mechanisms.

    Args:
        host: The GitHub host to authenticate with.

    Returns:
        The GitHub token if found, otherwise None.
    """
    token = get_token_from_env()
    if token:
        return token

    token = get_token_from_git_credential(host)
    if token:
        return token

    token = get_token_from_gh_cli(host)
    if token:
        return token

    return None


def get_token_from_env() -> Optional[str]:
    """
    Retrieve the GitHub token from the environment variable.

    Returns:
        The GitHub token if found, otherwise None.
    """
    return os.environ.get("SPHINX_GITHUB_CHANGELOG_TOKEN")


def get_token_from_git_credential(host: str) -> Optional[str]:
    """
    Retrieve the GitHub token using git credential helper.

    Args:
        host: The GitHub host to authenticate with.

    Returns:
        The GitHub token if found, otherwise None.
    """
    if not shutil.which("git"):
        return None

    try:
        resp = subprocess.check_output(
            ["git", "credential", "fill"],
            input=f"protocol=https\nhost={host}\n",
            text=True,
        )
        for ln in resp.splitlines():
            key, eq, value = ln.partition("=")
            if key == "password":
                return value
    except subprocess.CalledProcessError:
        pass
    return None


def get_token_from_gh_cli(host: str) -> Optional[str]:
    """
    Retrieve the GitHub token using the gh CLI.

    Args:
        host: The GitHub host to authenticate with.

    Returns:
        The GitHub token if found, otherwise None.
    """
    if not shutil.which("gh"):
        return None

    try:
        token = subprocess.check_output(["gh", "auth", "token", "--hostname", host], text=True).strip()
        if token:
            return token
    except subprocess.CalledProcessError:
        pass
    return None

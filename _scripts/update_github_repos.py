#!/usr/bin/env python3
"""Update _data/repositories.yml from live GitHub data."""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "_data" / "repositories.yml"
GITHUB_USER = os.environ.get("GITHUB_REPOS_USER", "dongjae-shin")
EXTRA_REPOS = [repo.strip() for repo in os.environ.get("GITHUB_REPOS_EXTRA", "dongjae-shin/MDUI").split(",") if repo.strip()]
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""

LANGUAGE_COLORS = {
    "C": "#555555",
    "C++": "#f34b7d",
    "HTML": "#e34c26",
    "Java": "#b07219",
    "JavaScript": "#f1e05a",
    "Jupyter Notebook": "#da5b0b",
    "Python": "#3572a5",
    "Ruby": "#701516",
    "Shell": "#89e051",
}


def request_json(url: str, data: Optional[dict] = None) -> dict:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "dongjae-shin.github.io"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    headers = {"Accept": "application/vnd.github.raw", "User-Agent": "dongjae-shin.github.io"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def current_repo_list() -> list[str]:
    current = OUTPUT_PATH.read_text(encoding="utf-8")
    before_metadata = current.split("github_repo_metadata:")[0]
    repos = re.findall(r"^  - ([^\n]+)$", before_metadata, flags=re.MULTILINE)
    return [repo.strip().strip('"') for repo in repos if "/" in repo]


def pinned_repos(username: str) -> list[str]:
    query = """
    query($login: String!) {
      user(login: $login) {
        pinnedItems(first: 6, types: REPOSITORY) {
          nodes {
            ... on Repository {
              nameWithOwner
              parent {
                nameWithOwner
              }
            }
          }
        }
      }
    }
    """
    payload = request_json("https://api.github.com/graphql", {"query": query, "variables": {"login": username}})
    nodes = payload.get("data", {}).get("user", {}).get("pinnedItems", {}).get("nodes", [])
    repos = []
    for node in nodes:
        if node:
            repos.append(node.get("parent", {}).get("nameWithOwner") or node.get("nameWithOwner"))
    return [repo for repo in repos if repo]


def readme_image(full_name: str, default_branch: str) -> str:
    try:
        readme = request_json(f"https://api.github.com/repos/{full_name}/readme")
    except urllib.error.HTTPError:
        return ""

    download_url = readme.get("download_url")
    if download_url:
        content = request_text(download_url)
    else:
        raw = readme.get("content", "")
        content = base64.b64decode(raw).decode("utf-8", errors="replace") if raw else ""

    match = re.search(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", content)
    if not match:
        match = re.search(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", content, re.IGNORECASE)
    if not match:
        return ""

    src = match.group(1).strip()
    if src.startswith(("http://", "https://")):
        return src
    if src.startswith("//"):
        return f"https:{src}"

    readme_path = readme.get("path", "README.md")
    base_dir = Path(readme_path).parent.as_posix()
    rel_path = src if base_dir == "." else f"{base_dir}/{src}"
    quoted = urllib.parse.quote(rel_path, safe="/")
    return f"https://raw.githubusercontent.com/{full_name}/{default_branch}/{quoted}"


def yaml_scalar(value) -> str:
    if value is None:
        return '""'
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if text == "":
        return '""'
    return json.dumps(text, ensure_ascii=False)


def write_yaml(data: dict) -> None:
    lines = []
    for key in ("github_users", "github_user_metadata", "repo_description_lines_max", "github_repos", "github_repo_metadata"):
        value = data[key]
        lines.append(f"{key}:")
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    first = True
                    for sub_key, sub_value in item.items():
                        prefix = "  -" if first else "   "
                        lines.append(f"{prefix} {sub_key}: {yaml_scalar(sub_value)}")
                        first = False
                else:
                    lines.append(f"  - {yaml_scalar(item)}")
        else:
            lines[-1] = f"{key}: {yaml_scalar(value)}"
        lines.append("")
    OUTPUT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    try:
        repos = pinned_repos(GITHUB_USER)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as error:
        print(f"Could not fetch pinned repositories: {error}; keeping repository data unchanged.", file=sys.stderr)
        return 0

    if not repos:
        repos = current_repo_list()
    for repo in EXTRA_REPOS:
        if repo not in repos:
            repos.append(repo)

    try:
        user = request_json(f"https://api.github.com/users/{GITHUB_USER}")
        repo_records = [request_json(f"https://api.github.com/repos/{full_name}") for full_name in repos]
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as error:
        print(f"Could not fetch GitHub repository metadata: {error}; keeping repository data unchanged.", file=sys.stderr)
        return 0

    metadata = []
    for repo in repo_records:
        language = repo.get("language") or ""
        full_name = repo["full_name"]
        default_branch = repo.get("default_branch") or "main"
        metadata.append(
            {
                "full_name": full_name,
                "description": repo.get("description") or "GitHub repository",
                "language": language,
                "language_color": LANGUAGE_COLORS.get(language, "#8b949e"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "cover_image": f"https://opengraph.githubassets.com/dongjae-shin-site/{full_name}",
                "readme_image": readme_image(full_name, default_branch),
            }
        )

    write_yaml(
        {
            "github_users": [GITHUB_USER],
            "github_user_metadata": [
                {
                    "username": GITHUB_USER,
                    "name": user.get("name") or GITHUB_USER,
                    "bio": user.get("bio") or "GitHub user",
                    "location": user.get("location") or "",
                    "public_repos": user.get("public_repos", 0),
                    "followers": user.get("followers", 0),
                }
            ],
            "repo_description_lines_max": 2,
            "github_repos": repos,
            "github_repo_metadata": metadata,
        }
    )
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

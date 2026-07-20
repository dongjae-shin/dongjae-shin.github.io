#!/usr/bin/env python3
"""Update cached Google Scholar citation counts in _bibliography/papers.bib."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOCIALS_PATH = ROOT / "_data" / "socials.yml"
BIB_PATH = ROOT / "_bibliography" / "papers.bib"


def scholar_user_id() -> str:
    match = re.search(r"^scholar_userid:\s*([^#\s]+)", SOCIALS_PATH.read_text(), re.M)
    if not match:
        raise RuntimeError(f"Could not find scholar_userid in {SOCIALS_PATH}")
    return match.group(1).split("&", 1)[0].split("?", 1)[0]


def fetch_profile_html(user_id: str) -> str:
    url = f"https://scholar.google.com/citations?user={user_id}&hl=en&pagesize=100"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("latin1")


def parse_counts(profile_html: str, user_id: str) -> dict[str, str]:
    counts: dict[str, str] = {}
    row_pattern = re.compile(r'<tr class="gsc_a_tr">(.*?)(?=<tr class="gsc_a_tr">|</tbody>)', re.S)
    id_pattern = re.compile(rf"citation_for_view={re.escape(user_id)}:([^&\"]+)")
    count_pattern = re.compile(r'class="gsc_a_ac gs_ibl">([^<]*)</a>', re.S)

    for row_match in row_pattern.finditer(profile_html):
        row = row_match.group(1)
        article_id = id_pattern.search(row)
        if not article_id:
            continue
        count = count_pattern.search(row)
        count_text = html.unescape(count.group(1)) if count else ""
        counts[article_id.group(1)] = re.sub(r"\D", "", count_text) or "0"

    if not counts:
        raise RuntimeError("No citation counts found in Google Scholar profile response")
    return counts


def update_bibliography(counts: dict[str, str]) -> int:
    lines = BIB_PATH.read_text().splitlines()
    updated: list[str] = []
    changed = 0
    index = 0

    while index < len(lines):
        line = lines[index]
        match = re.match(r"^(\s*google_scholar_id\s*=\s*)\{([^}]+)\}(,?)\s*$", line)
        if not match:
            updated.append(line)
            index += 1
            continue

        prefix, article_id, _comma = match.groups()
        count = counts.get(article_id)
        if count is None:
            updated.append(line)
            index += 1
            continue

        indent = re.match(r"^\s*", line).group(0)
        normalized_id_line = f"{prefix}{{{article_id}}},"
        count_line = f"{indent}google_scholar_citations={{{count}}},"
        updated.append(normalized_id_line)

        next_index = index + 1
        if next_index < len(lines) and re.match(r"^\s*google_scholar_citations\s*=", lines[next_index]):
            if lines[next_index] != count_line:
                changed += 1
            next_index += 1
        else:
            changed += 1
        updated.append(count_line)
        index = next_index

    new_text = "\n".join(updated) + "\n"
    old_text = BIB_PATH.read_text()
    if new_text != old_text:
        BIB_PATH.write_text(new_text)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Use a saved Google Scholar profile HTML file")
    args = parser.parse_args()

    user_id = scholar_user_id()

    if args.input:
        profile_html = Path(args.input).read_text(encoding="latin1")
    else:
        try:
            profile_html = fetch_profile_html(user_id)
        except Exception as exc:
            print(f"Warning: could not fetch Google Scholar profile: {exc}", file=sys.stderr)
            print("Skipping citation update.")
            return 0

    try:
        counts = parse_counts(profile_html, user_id)
    except RuntimeError as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        print("Skipping citation update.")
        return 0

    changed = update_bibliography(counts)
    print(f"Updated {changed} citation count field(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

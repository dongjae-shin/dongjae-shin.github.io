#!/usr/bin/env python3
"""Update cached citation counts in _bibliography/papers.bib from OpenAlex."""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "_bibliography" / "papers.bib"
OPENALEX_WORKS_URL = "https://api.openalex.org/works/"


def normalize_doi(raw_doi: str) -> str:
    doi = raw_doi.strip().strip("{}").strip()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:", "", doi, flags=re.I)
    return doi.strip()


def extract_field(block: list[str], field: str) -> str | None:
    pattern = re.compile(rf"^\s*{re.escape(field)}\s*=\s*[{{\"](.+?)[}}\"],?\s*$", re.I)
    for line in block:
        match = pattern.match(line)
        if match:
            return match.group(1)
    return None


def fetch_openalex_count(doi: str) -> int | None:
    params = {"select": "id,doi,cited_by_count"}
    api_key = os.environ.get("OPENALEX_API_KEY")
    if api_key:
        params["api_key"] = api_key
    email = os.environ.get("OPENALEX_EMAIL")
    if email:
        params["mailto"] = email

    url = f"{OPENALEX_WORKS_URL}doi:{quote(doi, safe='')}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "dongjae-shin.github.io citation updater"})
    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            print(f"Warning: OpenAlex has no work for DOI {doi}", file=sys.stderr)
            return None
        raise
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Warning: could not fetch OpenAlex data for DOI {doi}: {exc}", file=sys.stderr)
        return None

    count = data.get("cited_by_count")
    return int(count) if isinstance(count, int) else None


def replace_citation_field(block: list[str], count: int) -> tuple[list[str], bool]:
    updated: list[str] = []
    changed = False
    inserted = False
    replacement = f"  google_scholar_citations={{{count}}},"

    for line in block:
        if re.match(r"^\s*google_scholar_citations\s*=", line):
            if inserted:
                changed = True
                continue
            indent = re.match(r"^\s*", line).group(0)
            replacement = f"{indent}google_scholar_citations={{{count}}},"
            updated.append(replacement)
            changed = changed or line != replacement
            inserted = True
            continue

        if not inserted and re.match(r"^\s*google_scholar_id\s*=", line):
            updated.append(line)
            indent = re.match(r"^\s*", line).group(0)
            replacement = f"{indent}google_scholar_citations={{{count}}},"
            updated.append(replacement)
            changed = True
            inserted = True
            continue

        updated.append(line)

    return updated, changed


def update_bibliography() -> int:
    lines = BIB_PATH.read_text().splitlines()
    output: list[str] = []
    block: list[str] = []
    changed = 0
    in_entry = False

    for line in lines:
        if line.startswith("@"):
            in_entry = True
            block = [line]
            continue

        if in_entry:
            block.append(line)
            if line.strip() == "}":
                doi = extract_field(block, "doi")
                if doi:
                    count = fetch_openalex_count(normalize_doi(doi))
                    time.sleep(0.1)
                    if count is not None:
                        block, block_changed = replace_citation_field(block, count)
                        changed += int(block_changed)
                output.extend(block)
                block = []
                in_entry = False
            continue

        output.append(line)

    if block:
        output.extend(block)

    new_text = "\n".join(output) + "\n"
    if new_text != BIB_PATH.read_text():
        BIB_PATH.write_text(new_text)
    return changed


def main() -> int:
    changed = update_bibliography()
    print(f"Updated {changed} OpenAlex citation count field(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

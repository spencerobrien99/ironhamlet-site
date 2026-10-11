#!/usr/bin/env python3
"""Pre-publish checks for the IronHamlet marketing site.

Fails (exit 1) if any published file:
  - links to an internal page or asset that does not exist,
  - contains credential-like strings, private IP addresses, localhost URLs,
    or hostnames of the operational cyber range,
  - contains unassembled template markers or placeholder text,
  - contains emoji.

    python3 tools/check_site.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ["index.html", "404.html", "robots.txt", "sitemap.xml", "CNAME",
             "assets", "platform", "pilot", "contact", "privacy"]
TEXT_SUFFIXES = {".html", ".css", ".js", ".txt", ".xml", ".svg", ""}

FORBIDDEN = [
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"(?i)aws_secret_access_key|aws_session_token", "AWS secret reference"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"gh[pousr]_[A-Za-z0-9]{30,}", "GitHub token"),
    (r"(?i)(api[_-]?key|secret|password)\s*[:=]\s*['\"][^'\"]{6,}", "credential assignment"),
    (r"(?i)[?&]token=", "token in URL"),
    (r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "private IPv4 (10/8)"),
    (r"\b172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b", "private IPv4 (172.16/12)"),
    (r"\b192\.168\.\d{1,3}\.\d{1,3}\b", "private IPv4 (192.168/16)"),
    (r"(?i)\b(localhost|127\.0\.0\.1)\b", "localhost reference"),
    (r"(?i)\b(range|dcv)\.ironhamlet\.com\b", "operational range hostname"),
    (r"(?i)\.amazonaws\.com\b|\bec2-\d", "AWS endpoint"),
    (r"@@[A-Z_]+", "unassembled template marker"),
    (r"(?i)\b(lorem ipsum|todo|tbd|fixme|placeholder text)\b", "placeholder text"),
    (r"[\U0001F300-\U0001FAFF☀-➿]", "emoji"),
]


def published_files():
    for name in PUBLISHED:
        p = ROOT / name
        if p.is_file():
            yield p
        elif p.is_dir():
            yield from (f for f in p.rglob("*") if f.is_file())


def resolve(link):
    path = link.split("#")[0].split("?")[0]
    if not path:
        return True
    target = ROOT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    return target.exists()


def main():
    errors = []
    for f in published_files():
        if f.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(ROOT)
        for pattern, label in FORBIDDEN:
            for m in re.finditer(pattern, text):
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"{rel}:{line}: {label}: {m.group(0)[:40]!r}")
        if f.suffix == ".html":
            for link in re.findall(r'(?:href|src)="(/[^"]*)"', text):
                if not resolve(link):
                    errors.append(f"{rel}: broken internal link {link}")
    for e in errors:
        print(e)
    print(f"check_site: {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Switch the demo-request form from mailto to a hosted form endpoint.

    python3 tools/enable_hosted_form.py https://formspree.io/f/<your-form-id>

Run only after Spencer has created the form account (a new third-party
processor of visitor data). The endpoint id is public by design and is not a
credential. The mailto address stays as the automatic fallback if the hosted
service is unreachable. Updates the privacy notice to name the processor.
Re-run with --revert to go back to mailto only.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTACT = ROOT / "contact/index.html"
PRIVACY = ROOT / "privacy/index.html"

MAILTO_PRIVACY = ("Submitting the demo request form opens your own email application with your "
                  "request filled in, and it reaches us as an ordinary email.")
HOSTED_PRIVACY = ("Demo requests are submitted through Formspree, a form-processing service that "
                  "stores the submission and forwards it to us by email.")
MAILTO_NOTE = "This opens your email application with your request filled in. You can also write to"
HOSTED_NOTE = "If the form does not send, you can also write to"


def main():
    args = sys.argv[1:]
    revert = args == ["--revert"]
    if not revert and (len(args) != 1 or not re.fullmatch(r"https://formspree\.io/f/[A-Za-z0-9]+", args[0])):
        sys.exit("usage: enable_hosted_form.py https://formspree.io/f/<form-id> | --revert")
    endpoint = "" if revert else args[0]

    c = CONTACT.read_text()
    c, n = re.subn(r'data-endpoint="[^"]*"', f'data-endpoint="{endpoint}"', c)
    assert n == 1, "form data-endpoint attribute not found exactly once"
    c = c.replace(HOSTED_NOTE, MAILTO_NOTE) if revert else c.replace(MAILTO_NOTE, HOSTED_NOTE)
    CONTACT.write_text(c)

    p = PRIVACY.read_text()
    p = p.replace(HOSTED_PRIVACY, MAILTO_PRIVACY) if revert else p.replace(MAILTO_PRIVACY, HOSTED_PRIVACY)
    PRIVACY.write_text(p)
    print("form endpoint:", endpoint or "(none -- mailto only)")
    print("next: python3 tools/check_site.py, review the diff, commit, push (deploys).")


if __name__ == "__main__":
    main()

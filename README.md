# ironhamlet.com

Public marketing site for IronHamlet. Plain static HTML/CSS/JS, no build step,
deployed to GitHub Pages by `.github/workflows/pages.yml` on every push to `main`.

- Pages: `index.html`, `platform/`, `pilot/`, `contact/`, `privacy/`, `404.html`
- Shared styles: `assets/css/site.css`; shared script: `assets/js/site.js`
- Pre-publish check (runs in CI before deploy): `python3 tools/check_site.py`
  - fails on broken internal links, credentials, private IPs, localhost URLs,
    cyber-range hostnames, placeholder text, or emoji.

## Local preview

    python3 -m http.server 8765

## Demo-request form

`contact/index.html` posts to the URL in the form's `data-endpoint` attribute
(a hosted form service such as Formspree; the endpoint id is public by design and
is not a credential). If `data-endpoint` is empty or the request fails, the form
falls back to opening a pre-filled email to the address in `data-mailto`.
Spam protection: hidden honeypot field plus a minimum fill time.

## Isolation

This site is static and has no connection to the IronHamlet exercise environment.
It must never link to range hosts, management endpoints, or tokened URLs;
`tools/check_site.py` enforces this.

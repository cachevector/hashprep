# Security Policy

## Supported Versions

hashprep is currently in beta (`0.1.0bX`). Only the latest beta release on the `main` branch receives security updates. Older pre-releases are not patched — please upgrade to the newest version to pick up fixes.

| Version    | Supported          |
| ---------- | ------------------ |
| `0.1.0b3`  | :white_check_mark: |
| `< 0.1.0b3`| :x:                |

Once hashprep reaches a stable `0.1.0` release, this table will be updated to reflect supported minor versions.

## Reporting a Vulnerability

If you believe you have found a security vulnerability in hashprep (the Python package, the CLI, or the documentation website under `web/`), **please do not open a public GitHub issue**.

Instead, report it privately through one of the following channels:

- **GitHub Private Vulnerability Reporting** — preferred. Open a report at <https://github.com/cachevector/hashprep/security/advisories/new>.
- **Email** — `aftaab@aftaab.xyz` with the subject line `hashprep security report`.

Please include as much of the following as you can:

- A clear description of the issue and its impact.
- The affected version(s) and component (library, CLI, website).
- Steps to reproduce, a proof of concept, or a minimal failing example.
- Any known mitigations or workarounds.

### What to expect

- **Acknowledgement:** within 72 hours of your report.
- **Initial assessment:** within 7 days, including whether the report is accepted, needs more information, or is declined (with reasoning).
- **Fix and disclosure:** for accepted reports, we will work on a fix, prepare a patched release, and coordinate a disclosure timeline with you. Reporters will be credited in the advisory unless they prefer to remain anonymous.

### Scope

In scope:

- The `hashprep` Python package and CLI.
- The documentation site in `web/`.
- Build, packaging, and release tooling in this repository.

Out of scope:

- Vulnerabilities in third-party dependencies — please report those upstream. If a dependency issue affects hashprep users, we still appreciate a heads-up so we can bump the pinned version.
- Issues that require physical access to a user's machine or already-compromised environments.
- Denial of service caused by passing intentionally malformed datasets far outside the documented usage (e.g., multi-TB crafted inputs on a laptop).

# Plan and status: API Gateway Enterprise Architecture Standard

**Latest version:** 1.3 (Draft), issued and archived in `versions/v1.3/` (earlier: `versions/v1.2/`, `versions/v1.1/`, `versions/v1.0/`). To make further changes, start 1.4 (see "Working with versions"). **Format:** Word (.docx), English, A4.
Converted from `README.md` (the source notes) by a full rewrite into a formal standard.

## Status

| Item | State |
|---|---|
| Version 1.0 built, schema-validated, archived in `versions/v1.0/`, committed (`c9af9d0`, branch `docs/api-gateway-standard-v1`) | Done |
| Version 1.1 issued, archived in `versions/v1.1/` and committed (`029cf6d`): three open issues settled (capability enablement, consumer configuration in Git, exception approval), security core made mandatory, README updated | Done |
| Version 1.2 issued, archived in `versions/v1.2/` and committed: rewritten as continuous prose (numbered requirements, requirement IDs and the requirements register removed; obligations carried by plain must / should / can wording) | Done |
| Version 1.3 issued and archived in `versions/v1.3/` (**not yet committed**): Table 6 (Section 12.1) lists only the adjacent component's responsibilities; the "Gateway is responsible for" column is removed. The Hebrew edition was added at the same time, issued at 1.3 | Done |
| README updated with the review decisions | Done |
| Visual check of the rendered pages | **Not done**: no Word or LibreOffice on this machine. Open the .docx in Word; press F9 (or answer "Yes" to the update prompt) so the contents and lists get page numbers |
| Placeholders (organization, document ID, classification, owner, author, dates, approvers) | **Open**: highlighted yellow in the document |
| Places where the meaning differs from the README (mostly "should" strengthened to "must") | **Open**: the ones strengthened in 1.0 still await confirmation; all are listed by section in `CHANGES.md` |
| Two readings of terse answers (health checks beyond HTTP; scope gaps "yes"), and one unanswered question (can consumers be created at runtime?) | **Open**: see `CHANGES.md`, "Decisions taken during review" |
| Name of the Security Managers team | **Open**: placeholder in the definitions table |
| Uncommitted changes | **Yes.** Everything from the Table 6 change and version 1.3 (archive, `INDEX.md`, `CHANGES.md`, working copy), and the Hebrew edition with its build support (`content_he.py`, `figures/he/`, changes to `build_docx.py` and `figures.py`) |

## Files

| Path | Purpose |
|---|---|
| `README.md` | Source notes (40 sections). Kept in step with review decisions; original "should/shall" wording is unchanged |
| `API_Gateway_Enterprise_Architecture_Standard.docx` | Latest working copy of the official document |
| `versions/` | One folder per issued version (`v1.0/`), plus `INDEX.md`. Archived versions are never overwritten |
| `CHANGES.md` | README → standard: how the wording was converted, every change of meaning by section, resolved inconsistencies, decisions from review, section map. Regenerated on every build |
| `content.py` | The document as data: chapters, requirements, tables, metadata, `REVISIONS` |
| `build_docx.py` | Builds the .docx and `CHANGES.md`, runs the consistency checks, archives versions |
| `figures.py`, `figures/` | Diagram generator (Pillow) and its six PNGs |
| `content_he.py`, `API_Gateway_Enterprise_Architecture_Standard_he.docx` | Hebrew (right-to-left) edition of 1.3: same structure as `content.py`, checked against it on every build (`check_parity`). Not archived under `versions/`. Hebrew figures are drawn into `figures/he/` |
| `main.py` | Empty, unused |

## Working with versions

```bash
cd apps/api-gateway-doc
../.venv/bin/python build_docx.py             # rebuild the working copy and run the checks
../.venv/bin/python build_docx.py --archive   # also archive it as versions/v<version>/
../.venv/bin/python build_docx.py --lang he   # Hebrew edition (from content_he.py); no CHANGES.md, no archive
```

When `content.py` changes, update `content_he.py` to match: the Hebrew build stops with a parity error if the structure, references or placeholders differ, but it cannot tell whether the wording still means the same.

To issue a new version (for example 1.1 or 2.0):
1. Edit `content.py` (or `figures.py`).
2. Set `META["version"]` and append an entry to `REVISIONS` (date, author, summary). The revision history in the document is generated from it.
3. Run the build with `--archive`. It refuses if that version already exists, and it updates `versions/INDEX.md`.

Archived versions are kept as files, and the sources for each are in git: commit when a version is archived (1.0 is commit `c9af9d0`, 1.1 is `029cf6d`, 1.2 is the commit that follows them on the branch, 1.3 is not yet committed). Do not run `--archive` until the new version's `REVISIONS` summary is written.

## Document structure

13 chapters and 3 appendices, written as continuous prose (about 5,400 words) with 11 tables and 6 figures. Versions 1.0 and 1.1 have numbered requirements (`GW-<area>-NNN`); 1.2 and later do not.

| Ch. | Subject |
|---|---|
| 1 | Introduction: purpose, scope, audience, normative language, definitions, references |
| 2 | Architectural principles |
| 3 | Roles and responsibilities |
| 4 | Identity, authentication and authorization |
| 5 | Traffic management: routing, load-balancer boundary, health checks, timeouts, retry, rate limiting |
| 6 | API policy capabilities: transformation, caching, schema validation |
| 7 | API contract, lifecycle and Developer Portal |
| 8 | Configuration management: Git, GitOps, secrets |
| 9 | Observability and audit |
| 10 | Availability and deployment architecture |
| 11 | Governance and exceptions |
| 12 | Platform boundaries: WAF, load balancer, IdP, application |
| 13 | Vendor neutrality |
| App. A | Capability summary |
| App. B | Operating model diagram |
| App. C | Open issues (the governance body) |

Wording (from 1.2): **must** is mandatory, **should** or "recommended" is expected practice, **can** or **may** is optional, and present-tense statements describe how the platform is required to operate. Section 1.4 of the document explains this. Every departure from the README's wording is listed in `CHANGES.md`.

## Decisions taken so far

Recorded in the document and listed in `CHANGES.md`. Summary: token lifetime is owned by the IdP owner; traffic inside the cluster is HTTP, with no minimum TLS version and no maximum request size defined; 99.9% applies during regular operation, excluding planned maintenance; the Data Plane runs indefinitely on its last configuration and the Management Plane should be restorable within one hour; no retention period is defined; payload logging is off for sensitive information, defined per API; anonymous APIs are not permitted; WebSocket/streaming, east-west traffic, multi-tenancy and non-production are in scope. In 1.1: rate limiting, caching and schema validation stay fully optional per API and are recommended where they help; Git holds consumer identity, entitlements and rate limits, never credentials; exceptions are approved by the Security Managers; the security core (C2B/B2B tokens, no long-lived credential on every request, no undocumented manual production configuration) is mandatory. The exception request template (former Appendix C) was removed.

## Next steps

1. Open the .docx in Word and check layout, page breaks, figures and the contents page.
2. Fill in the yellow placeholders as part of 1.4, so the filled-in values are archived with it.
3. Confirm or downgrade the strengthened statements in `CHANGES.md`, confirm the two readings above, and answer the runtime-consumers question.
4. Name the Security Managers team, and resolve OI-01 (governance body, Appendix C) or accept it as open.
5. When 1.4 is agreed: write its `REVISIONS` summary, run the build with `--archive`, and commit.

## How it is checked

Every build verifies: the word "shall" and requirement IDs do not appear; every figure has alt text and a caption; placeholders are highlighted; no unresolved cross-references; all 40 README sections map to a place in the document. It also prints the word count and the number of "must", "should", "may" and "can". The .docx is also validated against the OOXML schemas with the docx skill's `validate.py` (needs `defusedxml`, which is not in the project venv).

# Plan and status: API Gateway Enterprise Architecture Standard

**Current version:** 1.0 (Draft), issued 2026-09-21. **Format:** Word (.docx), English, A4.
Converted from `README.md` (the source notes) by a full rewrite into a formal standard.

## Status

| Item | State |
|---|---|
| Version 1.0 built, schema-validated, archived in `versions/v1.0/` | Done |
| README updated with the review decisions | Done |
| Visual check of the rendered pages | **Not done**: no Word or LibreOffice on this machine. Open the .docx in Word; press F9 (or answer "Yes" to the update prompt) so the contents and lists get page numbers |
| Placeholders (organization, document ID, classification, owner, author, dates, approvers) | **Open**: highlighted yellow in the document |
| 34 requirements strengthened from "should" to "shall" | **Open**: awaiting confirmation (listed in `CHANGES.md`) |
| Two readings of terse answers (health checks beyond HTTP; scope gaps "yes") | **Open**: awaiting confirmation (`CHANGES.md`, "Decisions taken during review") |
| Nothing is committed to git | The whole folder is untracked |

## Files

| Path | Purpose |
|---|---|
| `README.md` | Source notes (40 sections). Kept in step with review decisions; original "should/shall" wording is unchanged |
| `API_Gateway_Enterprise_Architecture_Standard.docx` | Latest working copy of the official document |
| `versions/` | One folder per issued version (`v1.0/`), plus `INDEX.md`. Archived versions are never overwritten |
| `CHANGES.md` | README → standard: every change of meaning, resolved inconsistencies, decisions from review, section map. Regenerated on every build |
| `content.py` | The document as data: chapters, requirements, tables, metadata, `REVISIONS` |
| `build_docx.py` | Builds the .docx and `CHANGES.md`, runs the consistency checks, archives versions |
| `figures.py`, `figures/` | Diagram generator (Pillow) and its six PNGs |
| `main.py` | Empty, unused |

## Working with versions

```bash
cd apps/api-gateway-doc
../.venv/bin/python build_docx.py             # rebuild the working copy and run the checks
../.venv/bin/python build_docx.py --archive   # also archive it as versions/v<version>/
```

To issue a new version (for example 1.1 or 2.0):
1. Edit `content.py` (or `figures.py`).
2. Set `META["version"]` and append an entry to `REVISIONS` (date, author, summary). The revision history in the document is generated from it.
3. Run the build with `--archive`. It refuses if that version already exists, and it updates `versions/INDEX.md`.

Version 1.0 was built from the current sources, so it can be rebuilt exactly only until the sources change. To keep older versions reproducible, commit the sources when a version is archived.

## Document structure

13 chapters, 3 appendices, 128 numbered requirements (`GW-<area>-NNN`).

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
| App. A | Capability summary and generated requirements register |
| App. B | Operating model diagram |
| App. C | Open issues (OI-01 to OI-04) |

Requirement levels: **shall** (mandatory), **should** (recommended), **may** (optional), following BCP 14. Rule and every departure from the README's wording: see `CHANGES.md`.

## Decisions taken so far

Recorded in the document and listed in `CHANGES.md`. Summary: token lifetime is owned by the IdP owner; traffic inside the cluster is HTTP, with no minimum TLS version and no maximum request size defined; 99.9% applies during regular operation, excluding planned maintenance; the Data Plane runs indefinitely on its last configuration and the Management Plane should be restorable within one hour; no retention period is defined; payload logging is off for sensitive information, defined per API; anonymous APIs are not permitted; WebSocket/streaming, east-west traffic, multi-tenancy and non-production are in scope. The exception request template (former Appendix C) was removed.

## Next steps

1. Open the .docx in Word and check layout, page breaks, figures and the contents page.
2. Fill in the yellow placeholders, then issue the next version (1.1) so the filled-in values are archived.
3. Confirm or downgrade the 34 strengthened requirements, and confirm the two readings above.
4. Resolve OI-01 to OI-04 (Appendix C), or accept them as open.
5. Commit the folder when the content is agreed.

## How it is checked

Every build verifies: one normative keyword per requirement; unique requirement IDs; the register matches the body; every figure has alt text and a caption; placeholders are highlighted; no unresolved cross-references; all 40 README sections map to a place in the document. The .docx is also validated against the OOXML schemas with the docx skill's `validate.py` (needs `defusedxml`, which is not in the project venv).

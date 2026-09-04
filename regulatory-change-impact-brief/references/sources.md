# Sources

The eight entries in `scripts/sources.json`: what each one is, who owns it, how the run decides
whether a retrieval succeeded, and what its absence withholds. Read this when checking a source's
authority or when a retrieval judgement needs re-checking.

Seven entries are remote and are fetched live on every invocation. One is local. No entry carries a
credential; the six working remote links are public or viewer-only.

## External, European Commission

| Key | Locator | `source_role` | `authority` | Disclosed at |
|---|---|---|---|---|
| `ART50` | `https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50` | `binding-regulation` | `binding` | E8, E9 |
| `TIMELINE` | `https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline` | `binding-regulation` | `binding` | E8, E9 |
| `FAQ` | `https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act` | `official-guidance` | `advisory` | E8, E9 |

He characterised these himself at E9. The Article 50 text is "our hard legal authority", the timeline
"establishes the binding dates and deadlines", and of the FAQ, "it does not carry the force of law
itself".

Neither Commission page carries a version identifier, so version identity is recorded as
`retrieved_at` plus `content_hash`. That is our decision, not his, and it is written into the
`decisions` array with its rationale and tradeoffs. The timeline page states that it takes into
account the AI Act amendments introduced by the Digital Omnibus on AI and marks amended entries with
a double asterisk; that statement and the marking go into `version_metadata`.

## Internal, Quillhaven Academy

| Key | Locator | `source_role` | `authority` | Owner, per E13 |
|---|---|---|---|---|
| `REGISTER` | Google Sheet `10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU` | `operational-record` | `operational-evidence` | The system owners maintain their own entries |
| `INCIDENT` | Google Sheet `19BYZ68OSbsa1i9OfF6MzthrdC6q6mt6IWk6ucI8u7Rk` | `operational-record` | `operational-evidence` | Operations and the Manager |
| `CALENDAR` | Google Sheet `1xtXl_P7Yb9LaECZjjgtlyI-idoAJTAhH-1gQ4vQaCGA` | `operational-record` | `operational-evidence` | Operations and the Manager |
| `POLICY` | `https://app.notion.com/p/3ba0b700541e81f09998d48f3b1c2856` | `internal-policy` | `internal-control` | Leadership |

Each sheet is fetched through its `export?format=csv` endpoint. All three carry exactly one tab, so
the export is unambiguous and no tab identifier is needed.

## Local

| Key | Locator | `source_role` | `authority` |
|---|---|---|---|
| `TRANSCRIPT` | `references/interview-transcript.md` | `other` | `operational-evidence` |

This entry is marked local. The script never requests it over the network, and a run with no network
still resolves every `E` pointer.

`operational-evidence` is the closest value the schema offers, but the record's `summary` states in
its own words that this is stakeholder testimony recorded during an interview and not a system
generated record. Without that sentence it would sit at the same level as the three operational
registers, and the distinction between what a person said and what a system recorded is one this
whole workflow depends on. Where testimony and a register disagree, both go to stage 04 `conflicts`
and neither is marked correct.

## Retrieval tests

A source is `retrieved` only when its test passes. A failure records `unavailable` or `invalid` along
with `http_status`, `raw_bytes`, `extracted_chars` and the name of the test applied, so the judgement
can be re-checked without refetching. Extraction strips `script`, `style` and `noscript` before
measuring.

| Key | Test | Failure is |
|---|---|---|
| `ART50` | Extracted text over 10000 characters, and paragraphs numbered 1 to 4 each parse to more than 200 characters | `invalid` |
| `TIMELINE` | At least four date headings parse, and at least one entry line matches `Article 50` or `Transparency rules` | `invalid` |
| `FAQ` | Extracted text over 10000 characters and contains `Article 50` | `invalid` |
| `REGISTER` | Content type contains `text/csv`, and the header carries `system_id`, `provider_role`, `deployer_role`, `output_type`, `exposed_group`, `current_notice`, `evidence_status`, `evidence_updated_at` | `invalid` |
| `INCIDENT` | Content type contains `text/csv`, and the header carries `record_id`, `system_id`, `owner`, `status`, `evidence_state` | `invalid` |
| `CALENDAR` | Content type contains `text/csv`, and the header carries `action_id`, `system_id`, `due_date`, `status`, `approval_required` | `invalid` |
| `POLICY` | Extracted text over 500 characters | `unavailable` |
| `TRANSCRIPT` | File exists and carries headings `E1` through `E28` | `invalid` |

The timeline test is structural only. A length threshold there would add nothing the two structural
checks do not already catch, while adding a way to mark a binding source invalid by accident, and an
invalid binding source blocks the whole run.

The three header tests are how the run time column detection is actually implemented. A register that
loses a column is recorded as `invalid` rather than quietly parsed with one field missing.

## The unavailable source

The internal AI-use policy answers HTTP 200 and returns a page that carries no document text. Read on
2026-09-04 it produced 6 characters of extracted text against a 500 character threshold, so a status
code alone would have recorded it as retrieved. This is why the tests exist.

It is also the one source whose raw bytes are not stable. Two runs seconds apart returned 20047 and
20046 bytes with different `content_hash` values and an identical normalised text hash. That is the
case the second hash exists for: the page did not change, its shell did.

He confirmed the access position at E18 and gave the practice for it at E19: approach the document
owner, here leadership, and where they cannot supply the material "the affected review items have to
stay marked as pending or blocked until we get proper access".

It is not a binding source, so under the two tier policy this is a bounded partial and not a whole run
block. What it withholds is stage 04 `policy_controls`, in full: it is the document that records what
controls the school is supposed to be measuring against, per E3. Its absence is not evidence of
compliance, and the brief states that in Limitations.

## Why a stored copy is never a primary source

Copies of the three sheets exist in earlier session working directories and they still resolve. They
are reference only. README line 78 requires each invocation to read the current disclosed remote
sources, so a fetch failure is recorded and handled by the decision rules rather than papered over
with a copy that was correct yesterday.

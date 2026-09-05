---
name: regulatory-change-impact-brief
description: Run the Article 50 regulatory change impact review over the disclosed sources, writing seven audit snapshots and a draft impact register, compliance brief and action calendar for human approval.
allowed-tools: Bash, Read
compatibility: Requires network access, specifically outbound HTTPS to the seven disclosed sources listed in scripts/sources.json, three European Commission pages, three Google Sheets exports and one Notion page. No other destination is contacted, no credentials are sent, and every request is a read-only GET.
---

# Regulatory change impact brief

One command runs a fixed seven stage review of Quillhaven Academy's AI systems against EU AI Act
Article 50, and writes an audit trail plus three draft artifacts for the Compliance and Operations
Manager to take to Legal and Operations.

The pipeline is deterministic and it lives in `scripts/run_review.py`. Nothing here is decided by
reading the situation at run time: obligation limbs are a lookup table, source authority is a data
file, and every rule in this document is implemented in that script. Operating this skill means
checking the prerequisites, running the one command, reading the exit state, and handling the named
failures below. Composing any part of the register, the brief or the calendar by hand sits outside
it, which is why the frontmatter grants only `Bash` and `Read`.

Legal holds every interpretation. Operations holds activation, dates and closure. This workflow
prepares drafts and marks what is pending.

Paths that begin `scripts/` or `references/` are inside this skill package. Paths that begin
`deliverables/` are at the repository root, which is also where the command is run.

## Prerequisites

- `uv` on `PATH`. The script declares its dependencies inline, so `uv run` resolves them on first
  use and there is nothing to install by hand.
- Network reach to the seven remote sources listed in `scripts/sources.json`. Six answer; the
  internal AI-use policy is expected to deny access. The eighth entry in that file is the interview
  transcript, which is local and is never fetched.
- A working directory holding `snapshot.schema.json`, which is the repository root.

The internal AI-use policy answering with no access is a recorded state rather than an unmet
prerequisite: it withholds stage 04 `policy_controls` in full, the run continues under the bounded
partial rule, and the absence is written out as an evidence gap. Its absence is not evidence of
compliance.

## Runtime inputs

| Input | Meaning | Default |
|---|---|---|
| `--as-of <RFC 3339 timestamp>` | Stage 01 `as_of`, and the timestamp every artifact displays | Current UTC time |

Everything else is fixed, because for each of them one behaviour is correct:

- `run_id` derives from `--as-of`, so the same as-of value names the same run.
- Output paths are the tree in the repository README, written under `deliverables/`.
- Review type is the constant `change-triggered review of EU AI Act Article 50 transparency
  obligations`, which E26 point one separates from the quarterly register review.
- Sources come from `scripts/sources.json` and the remote ones are fetched live on every
  invocation. No flag substitutes a stored copy, because a stored copy may never be a primary
  source.

## The command

```bash
uv run regulatory-change-impact-brief/scripts/run_review.py
```

| Exit | Meaning |
|---|---|
| 0 | Stage 07 `publication_status` is `validated`. The audit trail conforms and formal conclusions were not blocked. A bounded partial run, which is the expected outcome while the internal policy is unreadable, still exits 0 |
| 1 | Stage 07 `publication_status` is `blocked` or `failed`, or the script could not write a conforming trail. All ten output files are written in every case |

The business outcome is read from `deliverables/snapshots/07-publication-validation.json`, never
inferred from the exit code alone.

## Outputs

| Path | What it is |
|---|---|
| `deliverables/snapshots/01-scope.json` | As-of time, review type, scope rule, audiences, approval gates |
| `deliverables/snapshots/02-source-capture.json` | Every source attempt and its retrieval result |
| `deliverables/snapshots/03-authority-and-timing.json` | Binding rules, timing, labelled guidance, authority blockers |
| `deliverables/snapshots/04-evidence-reconciliation.json` | System facts, policy controls, incidents, conflicts, evidence gaps |
| `deliverables/snapshots/05-impact-analysis.json` | Impacts, unaffected records, conflicts, unresolved items |
| `deliverables/snapshots/06-actions-and-approvals.json` | Actions, escalations, owners, approvals |
| `deliverables/snapshots/07-publication-validation.json` | Artifact paths and hashes, validation checks, publication status |
| `deliverables/impact-register.csv` | One row per impact or unresolved item, seventeen columns, listed in `references/stage-contract.md` |
| `deliverables/compliance-brief.md` | Seven sections in the order the repository README names them |
| `deliverables/action-calendar.ics` | Draft calendar, one event per proposed action, every event tentative and marked pending approval |

Each snapshot is written when its stage completes, not assembled after the artifacts.

## Stage contract

All seven snapshots share one `run_id`. Stage 01 carries `predecessor: null` and no consumed record
ids. From stage 02 onward each snapshot names its predecessor by `snapshot_id`, `path` and
`sha256`, and lists the upstream record ids it consumed and the record ids it produced.
`consumed_record_ids` names the upstream records this stage actually referenced, not every record
available to it. Per stage field detail, the id grammar and the artifact layouts are in
`references/stage-contract.md`.

| Stage | Consumes | Produces |
|---|---|---|
| 01 scope | Nothing | The run frame: as-of, review type, the scope rule, the audiences, the approval gates |
| 02 source-capture | Stage 01 | One `sourceRecord` per entry in `scripts/sources.json`, each with locator, retrieval status, content type, version metadata, content hash |
| 03 authority-and-timing | Stage 02 | Binding rules from the Article 50 text, dates from the timeline, FAQ material labelled advisory, and an authority blocker for every conclusion Legal must confirm |
| 04 evidence-reconciliation | Stages 02 and 03 | System facts from the register, policy controls, incident evidence, conflicts, evidence gaps |
| 05 impact-analysis | Stages 03 and 04 | Every system and limb pair, eight systems by five limbs, split between `impacts` and `unaffected_items` so the two together account for all forty, plus conflicts and unresolved items |
| 06 actions-and-approvals | Stage 05 | Proposed actions, approval requirements, escalations, each with an owner |
| 07 publication-validation | Stages 05 and 06 | The three artifacts, their hashes, fifteen validation checks and the publication status |

## Decision rules

1. **Two tier unavailability.** If the Article 50 binding text is unavailable, formal impact
   conclusions are blocked and the draft goes out marked unresolved. For any other unavailable
   source, a bounded partial: withhold and mark only the conclusions that source touches and
   deliver the rest. A whole run block applies only when the contaminated set cannot be determined,
   because then it is not bounded.
2. **The partial is bounded by obligation limb, not by system count.** Article 50(1) and 50(2) bind
   providers; 50(3) and 50(4) bind deployers. Deployer limb conclusions are delivered. Provider limb
   conclusions are withheld for every system pending a formal role determination.
3. **Facts stay visible, conclusions are withheld.** An observed fact goes into the register and the
   brief with its `evidence_ids`. Only the legal conclusion is withheld, as an `impactRecord` with
   `state: unresolved`.
4. **Source conflicts are recorded, never adjudicated.** Where two sources disagree, both readings
   are written into stage 04 `conflicts` with their evidence. Selecting a winner would override
   source authority, which this workflow does not do.
5. **Every unresolved item carries an owner and the evidence that would close it.** An unresolved
   item with neither is incomplete, not merely open.
6. **A correctable validation failure returns to the earliest affected stage** and reruns every
   stage downstream of it, so the lineage hashes stay intact. One rewind per run, recorded as a
   `decisions` entry in the rewritten stage. A second trigger of the same kind leaves the binding
   text recorded as invalid, which blocks the run under rule 1.

### State precedence

Each of the forty system and limb pairs takes the first outcome that matches, in this order:

1. The limb's trigger condition is not met, so the obligation does not apply: `unaffected_items`.
2. The trigger condition cannot be evaluated on register evidence: `impacts`, `unresolved`.
3. The register records `evidence_status: conflicting` for the system: `impacts`, `conflicting`.
4. The limb binds providers: `impacts`, `unresolved`, carrying the role authority blocker.
5. The register records `evidence_status` of `partial`, `stale` or `missing`: `impacts`,
   `unresolved`.
6. The register records `evidence_status: complete`: `impacts`, `supported-no-impact` where the
   register records a notice, `supported-impact` where it does not.

Layer 3 sits above layer 4 on purpose. A recorded conflict is a finding of its own and stating it
as merely unresolved would hide the most concrete evidence problem behind the role question. A pair
that reaches layer 3 still carries the role blocker when its limb binds providers.

The reasoning behind each rule, and the record of what this ordering produced on 2026-09-04, is in
`references/decision-policy.md`.

## Evidence and authority rules

1. `evidence_ids` resolve either to a source record id produced by stage 02, or to an exchange id
   `E1` to `E28` in `references/interview-transcript.md`.
2. **No stage 05 conclusion carries an `evidence_ids` pointer at an exchange.** This covers both
   arrays. Which obligation limb binds which system, and equally which limb does not apply, is legal
   interpretation derived from the Article 50 text against the register's `output_type` and
   `exposed_group`. It is ours, so every entry in `impacts` and every entry in `unaffected_items`
   carries an `authority_blocker` marking it pending Legal.
3. Stage 07 `validation_checks` take the same treatment. They rest on the repository README and on
   our own judgement, not on stakeholder testimony.
4. An `evidence_ids` pointer at E17, E20 or E27 points at a fact the interviewer read out of a file
   during the session, not at volunteered testimony. The transcript marks those quotations `H:`.
5. The E20 premise is inaccurate and is never quoted. The conclusion drawn there rests on his
   answer, and on `deployer_role` being `yes` for all eight systems, which is accurate.
6. No impact record rests on the Commission FAQ as its only evidence. The FAQ is advisory and stage
   07 checks this.

The limb mapping, its derivation and its blocker text are in `references/article-50-mapping.md`,
and the machine readable table the script reads is `scripts/article-50-limbs.json`.

## Safety boundary

The run reads the disclosed sources, writes files under `deliverables/`, and stops there.

Every output is a draft for human approval. Legal and Operations retain their stated decisions:
this workflow does not give final legal advice, activate a policy, change an approved deadline,
close an incident, submit an official response, or write to a production calendar. The draft
calendar carries only actions this run proposes; the client's own calendar entries are referenced
by id and never re-emitted as events.

Nothing leaves the machine except the source fetches themselves. Internal personal data, unredacted
staff or learner records, confidential incident details and preliminary legal interpretations stay
local, which is why the pipeline is a local script rather than a hosted service.

## Validation and completion

A run is complete when all four hold:

1. `uvx --from skills-ref agentskills validate ./regulatory-change-impact-brief` exits 0.
2. All seven snapshots validate against `snapshot.schema.json`.
3. The lineage is intact: each snapshot from 02 onward names its predecessor's real `sha256`, and
   every `evidence_ids` value resolves to a record produced upstream or to a real exchange id.
4. The register, brief and draft calendar agree with stages 06 and 07: same record ids, same states,
   same approval states, and the artifact hashes in stage 07 match the files on disk.

The fifteen checks stage 07 records, including the check that the forty system and limb pairs are
each accounted for exactly once and the check that all three artifacts read back in their own
format, are listed in `references/stage-contract.md`.

Before pushing, run the command from a clean checkout and confirm all four.

### Reproducibility

Two runs with the same `--as-of` against unchanged sources produce byte identical
`impact-register.csv`, `compliance-brief.md` and `action-calendar.ics`, because every timestamp the
artifacts display comes from `--as-of` and the retrieval clock stays in stage 02. Snapshots differ
only in `created_at`, `retrieved_at`, the predecessor hashes that cover those fields, and the
`content_hash` of any source that serves varying markup on each request. Record ids, states,
decisions and evidence pointers are identical.

Each source record carries two hashes: `content_hash` over the raw response bytes, which is the
source's identity, and a normalised text hash beside it. A difference beyond the timestamp fields
means a source changed, and comparing the two hashes says whether the change was substantive or
only markup. The internal AI-use policy is the live example: its raw bytes differ between two runs
seconds apart while its normalised text hash does not.

## Gotchas

- **`allowed-tools` governs the agent, not the script it runs.** A security scanner reports that
  this skill declares only `Bash` and `Read` while the bundled script writes files. Wrong default:
  add `Write` to settle the finding. Correct: leave the declaration alone. It exists so the agent
  cannot hand author the register, the brief or the calendar, and the script writing under
  `deliverables/` is the design. Granting `Write` would remove the one guarantee that every artifact
  came out of the command.
- **A run in a clean clone leaves the seven snapshots modified and the three artifacts unchanged.**
  Wrong default: read that as broken determinism and go hunting for the bug. Correct: this is the
  intended shape. `created_at` and `retrieved_at` record the real moment each stage was written, so
  a rerun moves them and the predecessor hashes that cover them. Every timestamp an artifact
  displays comes from `--as-of`, so the artifacts do not move. Determinism lives in the record ids,
  states, decisions and evidence pointers, and none of those change.
- **The AI-system register has no deployment or placed on market date column.** As read on
  2026-09-04 it has thirteen columns and one date column, `evidence_updated_at`. Wrong default:
  read a deployment date from it. Correct: detect columns at run time and record the absence as an
  evidence gap, because no source records placed on market dates.
- **The incident register `owner` column holds department names.** Wrong default: treat a missing
  individual as required next evidence. Correct: the department is the formal owner of record, no
  personal name exists in any of the three sheets, and the staleness caveat is carried as a
  limitation.
- **The compliance calendar `status` vocabulary is `blocked`, `open`, `planned`, `scheduled`.**
  Wrong default: write or expect `pending`. Correct: the approval state is a separate field on the
  artifact, not a calendar status value.
- **One compliance calendar row has `system_id` set to the literal `ALL`.** Wrong default: join it
  to a system and lose it silently. Correct: route any `system_id` outside the eight system ids down
  a separate path and record it as a register wide action.
- **Article 50(4) carries two distinct duties in one paragraph**, deep fake image, audio or video,
  and text published to inform the public on matters of public interest. Wrong default: treat the
  paragraph as one limb. Correct: five limbs, `50-1`, `50-2`, `50-3`, `50-4a`, `50-4b`.
- **Stored copies of the three sheets exist from earlier sessions.** Wrong default: fall back to one
  when a fetch is slow or fails. Correct: a fetch failure is recorded with its `retrieval_status`
  and handled by the decision rules.
- **The interview transcript is a local source, not a fetched one.** Wrong default: give it a URL
  and fetch it with the rest. Correct: `scripts/sources.json` marks it local, the script never
  requests it over the network, and its record says it is stakeholder testimony rather than a
  system generated record so it is not read at the same level as the three operational registers.
- **`output_type` is read from the register, never inferred from a system name.** As read on
  2026-09-04, AI-001 is `direct_interaction`, and the two systems with `output_type` `text` are
  AI-002 and AI-006.
- **Neither Commission page carries a version identifier.** Wrong default: leave `version_metadata`
  null. Correct: `retrieved_at` plus `content_hash`, recorded in `decisions` with its rationale and
  tradeoffs, together with the timeline page's own statement that it accounts for the Digital
  Omnibus amendments and marks amended entries with a double asterisk.
- **Frontmatter accepts six fields and no others**: `name`, `description`, `license`,
  `allowed-tools`, `metadata`, `compatibility`. Wrong default: add `argument-hint`. It fails
  validation.

## References

| File | Read it when |
|---|---|
| `references/stage-contract.md` | Changing what a stage records, or checking a snapshot field, an artifact column or a validation check against its contract |
| `references/decision-policy.md` | A decision rule has to change, or a reviewer asks why a conclusion was withheld |
| `references/article-50-mapping.md` | Checking how a limb was mapped to a system, or preparing the mapping for Legal |
| `references/sources.md` | Checking a source's authority, owner, retrieval test, or what its absence withholds |
| `references/interview-transcript.md` | Resolving an `E` number in any `evidence_ids` value |
| `scripts/article-50-limbs.json` | The five limb table the script reads. `article-50-mapping.md` explains it |
| `scripts/sources.json` | The source table the script reads. `sources.md` explains it |

# Stage contract

What each stage records, how records are named, and the exact layout of the three artifacts. The
skill body carries the rules; this file carries the shapes. Every field named here is written by
`scripts/run_review.py` and validated against `snapshot.schema.json`.

## Identifiers

Every identifier is derived from content or from `--as-of`. None is a sequence number, because a
sequence number changes when a source reorders its rows and that would break the reproducibility
claim.

| Identifier | Grammar | Example |
|---|---|---|
| `run_id` | `RUN-` plus `as_of` compacted to `YYYYMMDDTHHMMSSZ` | `RUN-20260904T164500Z` |
| `snapshot_id` | `<run_id>-<two digit sequence>-<stage>` | `RUN-20260904T164500Z-05-impact-analysis` |
| Source record | `SRC-<key from sources.json>` | `SRC-ART50`, `SRC-REGISTER`, `SRC-TRANSCRIPT` |
| Binding rule | `RULE-<limb>` | `RULE-50-4a` |
| Timing rule | `TIME-<date compacted>-<slug>` | `TIME-20260802-transparency-applies` |
| Guidance record | `GUID-<slug>` | `GUID-faq-marking` |
| Authority blocker | `BLK-<slug>` | `BLK-provider-role` |
| System fact | `FACT-<system_id>-<field>` | `FACT-AI-005-provider_role` |
| Incident evidence | `INC-<record_id from the incident register>` | `INC-REC-008` |
| Conflict | `CFL-<system_id>-<slug>` | `CFL-AI-003-evidence-quality` |
| Evidence gap | `GAP-<system_id or ALL>-<slug>` | `GAP-ALL-policy-controls` |
| Impact or unaffected item | `IMP-<system_id>-<limb>` | `IMP-AI-007-50-1` |
| Proposed action | `PA-<system_id or ALL>-<slug>` | `PA-ROLE-ALL` |
| Approval requirement | `APR-<proposed action id>` | `APR-PA-ROLE-ALL` |
| Escalation | `ESC-<slug>` | `ESC-ACT-002-overdue` |
| Artifact | `ART-<register or brief or calendar>` | `ART-BRIEF` |

`produced_record_ids` lists every record id this stage created in its own `state`.
`consumed_record_ids` lists only the upstream record ids this stage's records actually referenced.
Copying the whole upstream set would empty the field of information, and the field is how a reviewer
follows the document to decision path.

## Constants

Not runtime inputs and not data files. They live in `scripts/run_review.py` and are listed here so a
reader does not have to open the script.

| Constant | Value | Basis |
|---|---|---|
| `review_type` | `change-triggered review of EU AI Act Article 50 transparency obligations` | E26 point one, which separates this from the quarterly register review due 2026-10-02 |
| `audiences` | `learners`, `applicants`, `staff`, `the public` | E26 point one. Stage 04 reconciles these against the register's `exposed_group` values and records any difference as a conflict |
| `approval_gates` | `Compliance and Operations Manager reconciliation`, `Legal interpretation`, `Operations activation` | E26 point eight, in that order. Stage 06 reconciles against the calendar's `approval_required` values |
| `scope_rule` | `every AI system recorded in the AI-system register as at as_of` | Stage 01 declares the rule. The systems themselves are enumerated in stage 04, where the register has been fetched and there is evidence for them |

## Per stage state

Required keys come from `snapshot.schema.json`. This table says what goes in them.

### 01 scope

`as_of` from the input. `review_type`, `audiences`, `approval_gates` and `systems_in_scope` from the
constants above, where `systems_in_scope` holds the single scope rule string. `predecessor` is null
and `consumed_record_ids` is empty, as the schema requires for sequence 1.

### 02 source-capture

One `sourceRecord` per entry in `scripts/sources.json`, in file order. Beyond the schema's required
fields each record also carries `http_status`, `raw_bytes`, `extracted_chars`, `success_test_applied`
and `normalised_text_sha256`, so that a retrieval judgement can be re-checked without refetching.
`content_hash` covers the raw response bytes. `local_reference` holds the path for the one local
entry and is null for the remote ones.

### 03 authority-and-timing

`binding_rules`: one record per limb, carrying `fetched_paragraph_text`, the paragraph as retrieved
on this run, alongside `bundled_duty_text` from `scripts/article-50-limbs.json`. The record's
summary quotes the retrieved text, not the bundled copy, because the retrieved text is the primary
source. `bundled_duty_found_in_fetched` records whether the bundled sentence still appears verbatim
in the retrieved paragraph; a false there produces a stage 04 conflict rather than a correction,
because deciding which of the two is right is not ours. `timing_rules`: the four timeline entries that bear on Article 50, two dated 2026-08-02 and two
dated 2026-12-02, each recording whether the timeline page marked it with a double asterisk as
amended by the Digital Omnibus. `guidance_context`: FAQ material, every record labelled advisory.
`authority_blockers`: one record per determination Legal must confirm, at minimum the provider role
blocker and one blocker per limb mapping.

### 04 evidence-reconciliation

`system_facts`: one record per system per register field that later stages read. `policy_controls`:
empty, with the reason recorded, while the internal policy is unreadable. `incident_evidence`: one
record per row of the incident register. `conflicts`: source against source disagreements, including
the register against incident disagreement on evidence quality, and testimony against record
disagreements from E16 with E17 and E26 with E27. `evidence_gaps`: including the withheld policy
controls, the absent placed on market dates, and the systems whose `evidence_updated_at` predates
2026-08-02.

### 05 impact-analysis

`impacts` and `unaffected_items` together hold all forty system and limb pairs, one record each,
assigned by the state precedence in the skill body. Every record in `impacts` carries
`required_next_evidence`, named by the precedence layer it reached: layer 2 takes it from the limb
table, layer 4 is the role determination, layers 3 and 5 are complete and uncontested disclosure
evidence for the system, and layer 0, reached only when the binding text could not be read, is a
retrievable copy of the Article 50 text itself. Entries in `unaffected_items` carry none, because an
obligation that does not apply has nothing to close. `conflicts` carries the pairs that reached
precedence layer 3. `unresolved_items` carries every open question that is not itself a limb pair,
each with an owner and the evidence that would close it.

### 06 actions-and-approvals

`proposed_actions`: one record per action this run proposes. Actions are generated from state by
table: a provider role unresolved produces the single `PA-ROLE-ALL`, referenced by all seven
provider limb records, because one determination by Legal settles every one of them; an applicability
unresolved produces an evidence gathering action; a conflicting state produces a reconciliation
action; a supported impact produces a remediation action; a supported no impact produces nothing.
`approval_requirements`: one `approvalRecord` per proposed action, `status` always `pending`.
`escalations`: including any calendar action whose `due_date` precedes `as_of`.

Every proposed action record also carries `existing_calendar_action`, naming the client's own action
id where one covers the same system and subject. The presence of one never suppresses our proposed
action, because judging their action sufficient is Operations' decision.

### 07 publication-validation

`artifacts`: three `artifactRecord` entries with real `sha256` values. `validation_checks`: the
fifteen checks below. `publication_status`: `validated`, `blocked` or `failed`.

## Reason templates

Every `reason` value is a template with slots filled from the record, so the text is deterministic.

| State | Template |
|---|---|
| unaffected | `Article {limb} does not apply: the trigger condition {trigger} is not met ({field} is {value}).` |
| unresolved, applicability | `Applicability of Article {limb} cannot be determined from the disclosed sources: {undetermined_reason} Required next evidence: {required_next_evidence}` |
| conflicting | `The AI-system register records evidence_status conflicting for this system, corroborated by {incident_ids}. The conflict is recorded, not adjudicated.` |
| unresolved, provider role | `Article {limb} binds providers. The provider role is undetermined for every system pending a formal determination by Legal and the system owners.` |
| unresolved, evidence | `Article {limb} applies, but the register records evidence_status {value}, so no conclusion is established. Required next evidence: {required_next_evidence}` |
| supported-no-impact | `Article {limb} applies and the register records current_notice {value} with evidence_status complete. Timing and accessibility under Article 50(5) are not evidenced by any disclosed source.` |
| supported-impact | `Article {limb} applies and the register records current_notice {value} with evidence_status complete, so the obligation is not met.` |

## impact-register.csv

One row per `impacts` entry and per `unresolved_items` entry. The thirty `unaffected_items` do not
appear here; they are in snapshot 05 and in the brief's scope section. Seventeen columns, in this
order:

`record_id`, `system_id`, `system_name`, `obligation_limb`, `binding_party`, `applicability`,
`state`, `reason`, `evidence_references`, `evidence_ids`, `authority_blocker`, `responsible_owner`,
`required_next_evidence`, `proposed_action_id`, `existing_calendar_action`, `approval_gate`,
`approval_state`.

`evidence_references` is the human readable rendering, `evidence_ids` the raw ids. Both are present
because the file is read by people and by machines.

## compliance-brief.md

A header block carrying `run_id`, `as_of`, `publication_status` and the command that produced it,
then seven sections in the order the repository README names them: Scope, Source status, Supported
impacts, Unresolved items, Actions, Limitations, Pending Legal and Operations decisions.

Scope carries the full accounting of the forty pairs, including the list of pairs the obligations do
not reach and why. A section with nothing in it says so and gives the reason; it is never omitted.
Evidence is cited in readable form throughout, for example `AI-system register, retrieved
2026-09-04` or `stakeholder interview 2026-09-04, exchange E20`. Internal record ids do not appear.

## action-calendar.ics

`VCALENDAR` with `VERSION:2.0`, `PRODID` naming this skill and the `run_id`, `CALSCALE:GREGORIAN`,
`METHOD:PUBLISH`. One `VEVENT` per proposed action:

| Property | Value |
|---|---|
| `UID` | `<proposed action id>@<run_id>` |
| `DTSTAMP` | `as_of` |
| `DTSTART` | The proposed date where one exists, otherwise `as_of`, always `VALUE=DATE` |
| `SUMMARY` | `[DRAFT, pending <legal or operations>] <action text>` |
| `DESCRIPTION` | Related record ids, state, required next evidence, any existing calendar action id, and a closing line stating this is an unapproved draft |
| `STATUS` | `TENTATIVE` |
| `CATEGORIES` | The limb id |
| `CONTACT` | The responsible department |

No `ORGANIZER` or `ATTENDEE`, because owners are departments and not mailboxes, and inventing an
address would be fabricating a record. No `VALARM` and no `RRULE`, both of which read as writing the
client's own calendar. Lines are folded at 75 octets.

## The fifteen validation checks

Each is one record in stage 07 `validation_checks`. None cites an exchange.

1. All seven snapshots validate against `snapshot.schema.json`.
2. Every `predecessor.sha256` from stage 02 onward matches the file on disk.
3. All seven snapshots carry the same `run_id`.
4. Sequences 1 to 7 each appear exactly once.
5. `impacts` plus `unaffected_items` total forty, and each system and limb pair appears exactly once.
6. Every `evidence_ids` value resolves to a record produced upstream or to a real exchange id.
7. No entry in `impacts` or `unaffected_items` cites an exchange as the basis for a limb
   determination.
8. No impact record rests on the FAQ source id as its only evidence.
9. Every provider limb record carries the provider role authority blocker.
10. Every unresolved item carries an owner and required next evidence.
11. The register row count equals `impacts` plus `unresolved_items`, and every row's `record_id`
    exists in stage 05 or 06.
12. Every artifact `sha256` in stage 07 matches the file on disk.
13. Every proposed action in stage 06 appears as exactly one `VEVENT`.
14. Every timestamp displayed in the three artifacts equals `as_of`.
15. All three artifacts read back from disk in their own format: the register parses as CSV with the
    documented header and no row missing `record_id` or `state`, the calendar unfolds per RFC 5545
    with balanced components and every event carrying `UID`, `DTSTAMP`, `DTSTART`, `SUMMARY`,
    `STATUS`, `DESCRIPTION` and `CONTACT`, and the brief carries its seven sections in order.

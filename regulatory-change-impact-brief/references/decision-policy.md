# Decision policy

Why each decision rule in the skill body says what it says, and what the state precedence produced
when it was first run. Read this when a rule has to change, or when a reviewer asks why a conclusion
was withheld.

Quoted text is verbatim from `interview-transcript.md`. Anything not in quotation marks is our
reading, not the stakeholder's words.

## The line this whole policy defends

The workflow records what the sources say and marks what only a human may decide. It never selects a
winner between disagreeing sources, never converts an absence of evidence into evidence of
compliance, and never issues a legal conclusion in its own name. Every determination that is ours
carries an authority blocker naming the decision as pending Legal.

## Rule 1, two tier unavailability

Established with the stakeholder at E7 and applied unchanged. If the binding text is unavailable,
nothing formal can rest on anything, so formal conclusions are blocked. For any other unavailable
source the contaminated set is knowable, so the run withholds and marks the conclusions that source
touches and delivers the rest. A whole run block for a non binding source would be an over
correction, and a partial when the contaminated set is unknowable would be a false claim of
containment.

The live instance is the internal AI-use policy. He confirmed at E19 that where the document owner
cannot supply the material, "the affected review items have to stay marked as pending or blocked
until we get proper access". It withholds stage 04 `policy_controls` in full. Its absence is not
evidence of compliance, and the brief says so in Limitations.

## Rule 2, the partial is bounded by obligation limb

Article 50(1) and 50(2) bind providers. Article 50(3) and 50(4) bind deployers. The register records
`deployer_role` as `yes` for all eight systems and nothing contests that, so deployer limb work is
delivered.

Provider limb conclusions are withheld for **all eight systems**, not only for the one whose
`provider_role` is `unknown`. The register records `provider_role` as `no` for seven systems, but
that value is not a legal role determination. At E20 he described the mechanism that puts it in
doubt: a system owner marks the school as deployer, but on inspection of how the tool is used or
configured, "we might have added proprietary weights, custom fine-tuning, or branding that
potentially pushes us into provider territory under the regulation". That doubt is about the way the
column is populated, so it reaches every row of the column and not only the rows a calendar action
happens to touch.

E26 point five put the same position back to him and he did not correct it: "Until Legal and the
system owners make a formal determination, that is undetermined, not mis-recorded".

The rejected alternative was to read `provider_role: no` as evidence of no impact and mark those
seven `supported-no-impact`. That would be a conclusion drawn from an operational spreadsheet
against a binding obligation, which is the adjudication rule 4 forbids. It would also have produced a
much shorter unresolved list, which is the weaker reason to want it.

Note on citation: E20's question carried an inaccurate premise, asserting the register lists deployer
and not provider for all eight when `provider_role` is `no` for seven and `unknown` for AI-005. The
premise is never quoted. What is cited is his answer, which does not depend on it.

## Rule 3, facts stay visible and conclusions are withheld

README line 52 forbids letting a missing or conflicting record disappear downstream. Withholding a
conclusion is not the same as suppressing a fact. Every register value a withheld conclusion rests on
still appears as a `system_facts` record in stage 04 and in the `reason` column of the register row.
What is withheld is only the legal conclusion, carried as `state: unresolved` with a blocker.

This matters most where the operational urgency is real. AI-004 and AI-007 record `current_notice`
as `no` and both have live calendar actions. The run does not tell them the obligation binds them,
because that is Legal's call, and it does not tell them to stop either. It records that the notice is
absent, that a limb may reach them, and that the role question is what stands in the way.

## Rule 4, source conflicts are recorded and never adjudicated

E24 forbids overriding source authority. Where two sources disagree, both readings are written into
stage 04 `conflicts` with their evidence and neither is marked correct.

This rule decides which source can set an impact state to `conflicting`. The **register's**
`evidence_status` does; an incident record's `evidence_state` does not.

- AI-007: the register records `evidence_status: conflicting` and incident REC-008 records
  `evidence_state: conflicting`. Two sources agree that the evidence is in conflict, so nothing is
  being adjudicated by saying so. The impact state is `conflicting`.
- AI-003: the register records `complete` while incident REC-003 records `conflicting`. The sources
  disagree with each other. Letting the incident override the register would be choosing a winner.
  So the disagreement itself becomes a stage 04 `conflicts` record, and the impact state is decided
  by the register value as every other system's is.

## Rule 5, every unresolved item carries an owner and its closing evidence

His own standard, at E26 point seven: "An impact is established only when the underlying evidence is
complete and uncontested and applicability is settled. Otherwise it stays unresolved, with an owner
and the specific evidence that would close it."

That sentence is also the evidence gate in the state precedence. `complete` allows a supported state.
`partial`, `stale` and `missing` produce unresolved. `conflicting` produces conflicting.

Staleness uses the register's own `evidence_status`, which already marks AI-005 stale. The run does
not compute an age threshold of its own, because a threshold we invented would be an unlabelled
policy. Age is reported as a fact instead: AI-002 was last updated 2026-07-01 and AI-005 2026-04-15,
both before the obligations took effect on 2026-08-02. Those go to stage 04 `evidence_gaps`.

Owners are departments. At E27 he retracted the claim that the incident register holds named
individuals: "those department entries are all we have as formal owners in the records". A named
individual is therefore not required next evidence.

## Rule 6, one rewind per run

A deterministic pipeline that finds its own earlier record wrong has exactly one honest response,
which is to correct the record and rerun what depended on it. The realistic trigger is a source that
answered but did not carry what it should: the Article 50 page returns HTTP 200 and fails its parse
test, so stage 02's `retrieved` was wrong and should have been `invalid`. The run rewinds to stage
02, rewrites it, and reruns forward, recording the rewind as a `decisions` entry in the rewritten
stage.

The bound of one rewind per run exists so the pipeline cannot loop. A second trigger of the same kind
means the correction did not hold, which is a failed run and not something to retry.

## Why layer 3 sits above layer 4

A recorded conflict and an undetermined role are different findings. If the provider limb withholding
were applied first, AI-007's 50-1 would read `unresolved` for the role reason, and the conflict,
which is the most concrete evidence problem in the data and is corroborated by two sources, would
exist only in stage 04. Nobody reading the register or the brief would see it, and phase 1 decision 4
requires the misreading controls to live where the readers read.

The pair still carries the role blocker. Stating that the evidence is in conflict is not the same as
stating that the obligation binds.

## What the precedence produced on 2026-09-04

Against the register as fetched that day, forty pairs resolved as:

| Outcome | Count |
|---|---|
| `unaffected_items`, the obligation does not reach the system | 30 |
| `impacts`, `unresolved`, provider role undetermined | 6 |
| `impacts`, `conflicting`, AI-007 and Article 50(1) | 1 |
| `impacts`, `unresolved`, applicability undetermined | 3 |
| `impacts`, `supported-impact` | 0 |
| `impacts`, `supported-no-impact` | 0 |

Zero supported records is a result, not a defect. README line 52 says not to invent records to
demonstrate a state, and all four states are reachable under the precedence. Nothing in this data
reaches the two supported states because the single unresolved role question sits in front of every
provider limb, and the three deployer limb pairs that survive applicability either fail the evidence
gate or cannot be evaluated at all.

The finding this review delivers is therefore precise and small: one role determination by Legal
unlocks seven pairs, three named pieces of evidence unlock three more, and one recorded conflict
needs reconciling. That is what the brief says.

## Decisions recorded in the snapshots

These are ours and are written into the `decisions` array with rationale and tradeoffs, never
presented as the stakeholder's:

- `version_metadata` for the two Commission pages is `retrieved_at` plus `content_hash`, because
  neither page carries a version identifier.
- Stage 07 `validation_checks` rest on the repository README and on our judgement.
- The conflict recording policy in rule 4, including which source sets a `conflicting` state.
- The scope rule in stage 01, and the choice to enumerate systems in stage 04 where there is
  evidence for them.

He characterised the source authorities himself at E9: the Article 50 text is "our hard legal
authority", and of the FAQ, "it does not carry the force of law itself". Those are his words and are
cited as such.

# Compliance brief: EU AI Act Article 50 transparency obligations

- Run: `RUN-20260904T120000Z`
- As at: 2026-09-04T12:00:00Z
- Review type: change-triggered review of EU AI Act Article 50 transparency obligations
- Publication status: validated
- Produced by: `uv run regulatory-change-impact-brief/scripts/run_review.py`

This is a draft prepared for human review. Legal holds every interpretation of the obligations. Operations holds activation, dates and closure. Nothing here is a legal opinion or an approved action.

## Scope

Every ai system recorded in the ai-system register as at as_of, reviewed against the five obligation limbs of Article 50. Audiences: learners, applicants, staff, the public. Approval gates, in order: Compliance and Operations Manager reconciliation; Legal interpretation; Operations activation.

8 systems by 5 obligation limbs is 40 system and limb pairs. 30 pairs are not reached by the obligation and 10 entered the analysis.

Pairs the obligations do not reach:

- AI-001 Learner Support Chat, Article 50-2: Article 50-2 does not apply: the trigger condition output_type is one of text, synthetic_image, synthetic_audio_video is not met (direct_interaction output, exposed to learners).
- AI-001 Learner Support Chat, Article 50-3: Article 50-3 does not apply: the trigger condition output_type is classification is not met (direct_interaction output, exposed to learners).
- AI-001 Learner Support Chat, Article 50-4a: Article 50-4a does not apply: the trigger condition output_type is one of synthetic_image, synthetic_audio_video is not met (direct_interaction output, exposed to learners).
- AI-001 Learner Support Chat, Article 50-4b: Article 50-4b does not apply: the trigger condition output_type is text and exposed_group is public is not met (direct_interaction output, exposed to learners).
- AI-002 Admissions Draft Assistant, Article 50-1: Article 50-1 does not apply: the trigger condition output_type is direct_interaction is not met (text output, exposed to applicants).
- AI-002 Admissions Draft Assistant, Article 50-3: Article 50-3 does not apply: the trigger condition output_type is classification is not met (text output, exposed to applicants).
- AI-002 Admissions Draft Assistant, Article 50-4a: Article 50-4a does not apply: the trigger condition output_type is one of synthetic_image, synthetic_audio_video is not met (text output, exposed to applicants).
- AI-002 Admissions Draft Assistant, Article 50-4b: Article 50-4b does not apply: the trigger condition output_type is text and exposed_group is public is not met (text output, exposed to applicants).
- AI-003 Campaign Image Studio, Article 50-1: Article 50-1 does not apply: the trigger condition output_type is direct_interaction is not met (synthetic_image output, exposed to public).
- AI-003 Campaign Image Studio, Article 50-3: Article 50-3 does not apply: the trigger condition output_type is classification is not met (synthetic_image output, exposed to public).
- AI-003 Campaign Image Studio, Article 50-4b: Article 50-4b does not apply: the trigger condition output_type is text and exposed_group is public is not met (synthetic_image output, exposed to public).
- AI-004 Pronunciation Coach, Article 50-2: Article 50-2 does not apply: the trigger condition output_type is one of text, synthetic_image, synthetic_audio_video is not met (direct_interaction output, exposed to learners).
- AI-004 Pronunciation Coach, Article 50-3: Article 50-3 does not apply: the trigger condition output_type is classification is not met (direct_interaction output, exposed to learners).
- AI-004 Pronunciation Coach, Article 50-4a: Article 50-4a does not apply: the trigger condition output_type is one of synthetic_image, synthetic_audio_video is not met (direct_interaction output, exposed to learners).
- AI-004 Pronunciation Coach, Article 50-4b: Article 50-4b does not apply: the trigger condition output_type is text and exposed_group is public is not met (direct_interaction output, exposed to learners).
- AI-005 Remote Proctor Signal, Article 50-1: Article 50-1 does not apply: the trigger condition output_type is direct_interaction is not met (classification output, exposed to learners).
- AI-005 Remote Proctor Signal, Article 50-2: Article 50-2 does not apply: the trigger condition output_type is one of text, synthetic_image, synthetic_audio_video is not met (classification output, exposed to learners).
- AI-005 Remote Proctor Signal, Article 50-4a: Article 50-4a does not apply: the trigger condition output_type is one of synthetic_image, synthetic_audio_video is not met (classification output, exposed to learners).
- AI-005 Remote Proctor Signal, Article 50-4b: Article 50-4b does not apply: the trigger condition output_type is text and exposed_group is public is not met (classification output, exposed to learners).
- AI-006 Staff Summary Assistant, Article 50-1: Article 50-1 does not apply: the trigger condition output_type is direct_interaction is not met (text output, exposed to staff).
- AI-006 Staff Summary Assistant, Article 50-3: Article 50-3 does not apply: the trigger condition output_type is classification is not met (text output, exposed to staff).
- AI-006 Staff Summary Assistant, Article 50-4a: Article 50-4a does not apply: the trigger condition output_type is one of synthetic_image, synthetic_audio_video is not met (text output, exposed to staff).
- AI-006 Staff Summary Assistant, Article 50-4b: Article 50-4b does not apply: the trigger condition output_type is text and exposed_group is public is not met (text output, exposed to staff).
- AI-007 Website Guide Avatar, Article 50-2: Article 50-2 does not apply: the trigger condition output_type is one of text, synthetic_image, synthetic_audio_video is not met (direct_interaction output, exposed to public).
- AI-007 Website Guide Avatar, Article 50-3: Article 50-3 does not apply: the trigger condition output_type is classification is not met (direct_interaction output, exposed to public).
- AI-007 Website Guide Avatar, Article 50-4a: Article 50-4a does not apply: the trigger condition output_type is one of synthetic_image, synthetic_audio_video is not met (direct_interaction output, exposed to public).
- AI-007 Website Guide Avatar, Article 50-4b: Article 50-4b does not apply: the trigger condition output_type is text and exposed_group is public is not met (direct_interaction output, exposed to public).
- AI-008 Video Localisation Tool, Article 50-1: Article 50-1 does not apply: the trigger condition output_type is direct_interaction is not met (synthetic_audio_video output, exposed to public).
- AI-008 Video Localisation Tool, Article 50-3: Article 50-3 does not apply: the trigger condition output_type is classification is not met (synthetic_audio_video output, exposed to public).
- AI-008 Video Localisation Tool, Article 50-4b: Article 50-4b does not apply: the trigger condition output_type is text and exposed_group is public is not met (synthetic_audio_video output, exposed to public).

## Source status

| Source | Authority | Status | Read |
|---|---|---|---|
| EU AI Act Article 50 binding text, European Commission AI Act Service Desk | binding | retrieved | 2026-09-04 |
| Official EU AI Act implementation timeline, European Commission AI Act Service Desk | binding | retrieved | 2026-09-04 |
| Commission FAQ on transparency obligations under Article 50 | advisory | retrieved | 2026-09-04 |
| Quillhaven Academy AI-system register | operational-evidence | retrieved | 2026-09-04 |
| Quillhaven Academy incident and evidence register | operational-evidence | retrieved | 2026-09-04 |
| Quillhaven Academy compliance calendar | operational-evidence | retrieved | 2026-09-04 |
| Quillhaven Academy internal AI-use policy | internal-control | unavailable | 2026-09-04 |
| Stakeholder testimony recorded in the interview of 2026-09-04. This is what a person said, not a record produced by a system, and it is not read at the same level as the three operational registers. | operational-evidence | retrieved | 2026-09-04 |

Quillhaven Academy internal AI-use policy is unavailable. This withholds stage 04 policy_controls, in full. Its absence is not evidence of compliance.

## Supported impacts

No records reached this section on this run. Every applicable obligation limb is held open by the provider role determination or by missing applicability evidence, both listed under Unresolved items. No record has been invented to demonstrate a state.

## Unresolved items

### IMP-AI-001-50-1, unresolved

AI-001 Learner Support Chat, Article 50-1

Article 50-1 binds providers. The provider role is undetermined for every system pending a formal determination by Legal and the system owners.

Required next evidence: A formal provider or deployer role determination from Legal and the system owners.

Owner: Learner Operations. Evidence: AI-system register, AI-001 output_type; AI-system register, AI-001 exposed_group; Article 50-1 binding text.

### IMP-AI-002-50-2, unresolved

AI-002 Admissions Draft Assistant, Article 50-2

Article 50-2 binds providers. The provider role is undetermined for every system pending a formal determination by Legal and the system owners.

Required next evidence: A formal provider or deployer role determination from Legal and the system owners.

Owner: Admissions. Evidence: AI-system register, AI-002 output_type; AI-system register, AI-002 exposed_group; Article 50-2 binding text.

### IMP-AI-003-50-2, unresolved

AI-003 Campaign Image Studio, Article 50-2

Article 50-2 binds providers. The provider role is undetermined for every system pending a formal determination by Legal and the system owners.

Required next evidence: A formal provider or deployer role determination from Legal and the system owners.

Owner: Communications. Evidence: AI-system register, AI-003 output_type; AI-system register, AI-003 exposed_group; Article 50-2 binding text.

### IMP-AI-003-50-4a, unresolved

AI-003 Campaign Image Studio, Article 50-4a

Applicability of Article 50-4a cannot be determined from the disclosed sources: The register records a synthetic output type, which is a necessary but not a sufficient condition. Whether the content resembles existing persons, objects, places, entities or events is not recorded by any disclosed source. Required next evidence: A description of the generated content and whether it depicts real persons or events, from the system owner.

Required next evidence: A description of the generated content and whether it depicts real persons or events, from the system owner.

Owner: Communications. Evidence: AI-system register, AI-003 output_type; AI-system register, AI-003 exposed_group; Article 50-4a binding text.

### IMP-AI-004-50-1, unresolved

AI-004 Pronunciation Coach, Article 50-1

Article 50-1 binds providers. The provider role is undetermined for every system pending a formal determination by Legal and the system owners.

Required next evidence: A formal provider or deployer role determination from Legal and the system owners.

Owner: Learning Experience. Evidence: AI-system register, AI-004 output_type; AI-system register, AI-004 exposed_group; Article 50-1 binding text.

### IMP-AI-005-50-3, unresolved

AI-005 Remote Proctor Signal, Article 50-3

Applicability of Article 50-3 cannot be determined from the disclosed sources: The register records output_type classification, which is a necessary but not a sufficient condition. No disclosed source records what the classifier classifies. Required next evidence: The flagging criteria for this system, held by the system owners and outside anything the Compliance and Operations Manager can read.

Required next evidence: The flagging criteria for this system, held by the system owners and outside anything the Compliance and Operations Manager can read.

Owner: Assessment Operations. Evidence: AI-system register, AI-005 output_type; AI-system register, AI-005 exposed_group; Article 50-3 binding text.

### IMP-AI-006-50-2, unresolved

AI-006 Staff Summary Assistant, Article 50-2

Article 50-2 binds providers. The provider role is undetermined for every system pending a formal determination by Legal and the system owners.

Required next evidence: A formal provider or deployer role determination from Legal and the system owners.

Owner: People Operations. Evidence: AI-system register, AI-006 output_type; AI-system register, AI-006 exposed_group; Article 50-2 binding text.

### IMP-AI-007-50-1, conflicting

AI-007 Website Guide Avatar, Article 50-1

The AI-system register records evidence_status conflicting for this system. The conflict is recorded, not adjudicated.

Required next evidence: Complete and uncontested evidence of the disclosure practice for this system.

Owner: Marketing. Evidence: AI-system register, AI-007 output_type; AI-system register, AI-007 exposed_group; Article 50-1 binding text; AI-system register, AI-007 evidence_status; incident and evidence register, REC-008.

### IMP-AI-008-50-2, unresolved

AI-008 Video Localisation Tool, Article 50-2

Article 50-2 binds providers. The provider role is undetermined for every system pending a formal determination by Legal and the system owners.

Required next evidence: A formal provider or deployer role determination from Legal and the system owners.

Owner: Communications. Evidence: AI-system register, AI-008 output_type; AI-system register, AI-008 exposed_group; Article 50-2 binding text.

### IMP-AI-008-50-4a, unresolved

AI-008 Video Localisation Tool, Article 50-4a

Applicability of Article 50-4a cannot be determined from the disclosed sources: The register records a synthetic output type, which is a necessary but not a sufficient condition. Whether the content resembles existing persons, objects, places, entities or events is not recorded by any disclosed source. Required next evidence: A description of the generated content and whether it depicts real persons or events, from the system owner.

Required next evidence: A description of the generated content and whether it depicts real persons or events, from the system owner.

Owner: Communications. Evidence: AI-system register, AI-008 output_type; AI-system register, AI-008 exposed_group; Article 50-4a binding text.

### UNR-provider-role, unresolved



The provider or deployer role is undetermined for all eight systems, which withholds every Article 50(1) and 50(2) conclusion.

Required next evidence: Written evidence from the vendor contract or system deployment records confirming who built and placed each system into service, followed by a formal sign-off from Legal.

Owner: Legal and the system owners. Evidence: Whether Quillhaven Academy is provider or deployer is undetermined for all eight systems. Every provider limb conclusion is withheld pending a formal determinat; stakeholder interview 2026-09-04, exchange E20; stakeholder interview 2026-09-04, exchange E26.

### UNR-policy-controls, unresolved



The internal AI-use policy could not be read, so the controls the school measures itself against are unknown.

Required next evidence: The policy text or the relevant excerpts, supplied by the document owner.

Owner: Leadership. Evidence: The internal AI-use policy is unavailable, so stage 04 policy_controls is withheld in full. Its absence is not evidence of compliance.; Quillhaven Academy internal AI-use policy (unavailable, read 2026-09-04).

### UNR-placed-on-market, unresolved



No source records placed on market or deployment dates, so the Article 50(2) transitional deadline of 02 Dec 2026 cannot be applied to any system.

Required next evidence: Placed on market or deployment dates per system.

Owner: The system owners. Evidence: No disclosed source records placed on market or deployment dates, so the Article 50(2) transitional deadline cannot be applied to any system..

## Actions

Every action below is a draft proposal. None is scheduled, approved or activated.

| Action | Scope | Proposal | Owner | Approval gate | Approval state | Existing action |
|---|---|---|---|---|---|---|
| PA-ROLE-ALL | ALL | Obtain a formal provider or deployer role determination for all eight systems from Legal and the system owners. | Legal and the system owners | legal | pending | none |
| PA-AI-003-applicability-50-4a | AI-003 | Obtain the evidence that settles whether Article 50-4a applies to AI-003: A description of the generated content and whether it depicts real persons or events, from the system owner. | Communications | legal | pending | ACT-004 |
| PA-AI-005-applicability-50-3 | AI-005 | Obtain the evidence that settles whether Article 50-3 applies to AI-005: The flagging criteria for this system, held by the system owners and outside anything the Compliance and Operations Manager can read. | Assessment Operations | legal | pending | ACT-005 |
| PA-AI-007-reconcile-50-1 | AI-007 | Reconcile the conflicting disclosure evidence for AI-007 and record one agreed position. | Marketing | operations | pending | ACT-002 |
| PA-AI-008-applicability-50-4a | AI-008 | Obtain the evidence that settles whether Article 50-4a applies to AI-008: A description of the generated content and whether it depicts real persons or events, from the system owner. | Communications | legal | pending | ACT-006, ACT-007 |
| PA-ALL-policy-access | ALL | Request access to the internal AI-use policy from leadership, or the relevant excerpts. | Leadership | operations | pending | none |
| PA-ALL-placed-on-market | ALL | Record placed on market or deployment dates for each system so the Article 50(2) transitional deadline can be assessed. | The system owners | operations | pending | none |

Escalations raised by this run:

- Compliance calendar action ACT-002 for AI-007 was due 2026-09-03, before the as-of date 2026-09-04. Stated as a fact about their own record, not as a finding of non-compliance.
- AI-001 carries an open Article 50 question in this review and no compliance calendar action of its own.
- AI-006 carries an open Article 50 question in this review and no compliance calendar action of its own.
- Compliance calendar rows ACT-008 carry a system_id outside the eight system ids and are treated as register wide actions, not expanded per system.

## Limitations

- The internal AI-use policy is unavailable, so stage 04 policy_controls is withheld in full. Its absence is not evidence of compliance.
- No disclosed source records placed on market or deployment dates, so the Article 50(2) transitional deadline cannot be applied to any system.
- No disclosed source records when a notice is shown or whether it meets accessibility requirements, so Article 50(5) cannot be evidenced for any system.
- AI-002 evidence was last updated 2026-07-01, before the Article 50 obligations took effect on 2026-08-02.
- AI-005 evidence was last updated 2026-04-15, before the Article 50 obligations took effect on 2026-08-02.
- The AI-system register records evidence_status complete for AI-003, while incident REC-003 records evidence_state conflicting. The two sources disagree. Both readings are recorded and neither is marked correct.
- Testimony at E16 placed deployment dates in the AI-system register. The register has no such column. He retreated from the claim at E17. Recorded as testimony against record.
- Testimony at E26 placed named individual owners in the incident register. Its owner column holds department names only. He retracted at E27. Recorded as testimony against record.
- Every determination of which obligation limb reaches which system, including every determination that a limb does not apply, is ours and is marked pending Legal.
- The Commission FAQ is advisory and is never the sole basis for any conclusion here.

## Pending Legal and Operations decisions

Legal:

- PA-ROLE-ALL: Obtain a formal provider or deployer role determination for all eight systems from Legal and the system owners.
- PA-AI-003-applicability-50-4a: Obtain the evidence that settles whether Article 50-4a applies to AI-003: A description of the generated content and whether it depicts real persons or events, from the system owner.
- PA-AI-005-applicability-50-3: Obtain the evidence that settles whether Article 50-3 applies to AI-005: The flagging criteria for this system, held by the system owners and outside anything the Compliance and Operations Manager can read.
- PA-AI-008-applicability-50-4a: Obtain the evidence that settles whether Article 50-4a applies to AI-008: A description of the generated content and whether it depicts real persons or events, from the system owner.

Operations:

- PA-AI-007-reconcile-50-1: Reconcile the conflicting disclosure evidence for AI-007 and record one agreed position.
- PA-ALL-policy-access: Request access to the internal AI-use policy from leadership, or the relevant excerpts.
- PA-ALL-placed-on-market: Record placed on market or deployment dates for each system so the Article 50(2) transitional deadline can be assessed.

This workflow does not give final legal advice, activate a policy, change an approved deadline, close an incident, submit an official response, or write to a production calendar.

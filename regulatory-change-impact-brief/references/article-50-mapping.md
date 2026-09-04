# Article 50 mapping

How this workflow maps EU AI Act Article 50 onto Quillhaven Academy's eight AI systems. Read this
when checking how a limb reached a system, or when preparing the mapping for Legal.

**The mapping is ours.** No stakeholder supplied it and nothing in it is a transcription of their
existing plan. Every determination it produces, including every determination that an obligation does
not apply, carries an authority blocker marking it pending Legal. The machine readable form the
script reads is `scripts/article-50-limbs.json`; this file explains it and is the version to hand to
Legal.

## Why five limbs and not four

Article 50 has six numbered paragraphs. Four of them impose duties, but paragraph 4 imposes two
distinct duties with different subjects and different trigger conditions, so it is split.

| Limb | Binds | Duty, verbatim from the Article 50 text |
|---|---|---|
| `50-1` | Providers | "Providers shall ensure that AI systems intended to interact directly with natural persons are designed and developed in such a way that the natural persons concerned are informed that they are interacting with an AI system, unless this is obvious from the point of view of a natural person who is reasonably well-informed, observant and circumspect, taking into account the circumstances and the context of use." |
| `50-2` | Providers | "Providers of AI systems, including general-purpose AI systems, generating synthetic audio, image, video or text content, shall ensure that the outputs of the AI system are marked in a machine-readable format and detectable as artificially generated or manipulated." |
| `50-3` | Deployers | "Deployers of an emotion recognition system or a biometric categorisation system shall inform the natural persons exposed thereto of the operation of the system, and shall process the personal data in accordance with Regulations (EU) 2016/679 and (EU) 2018/1725 and Directive (EU) 2016/680, as applicable." |
| `50-4a` | Deployers | "Deployers of an AI system that generates or manipulates image, audio or video content constituting a deep fake, shall disclose that the content has been artificially generated or manipulated." |
| `50-4b` | Deployers | "Deployers of an AI system that generates or manipulates text which is published with the purpose of informing the public on matters of public interest shall disclose that the text has been artificially generated or manipulated." |

Paragraph 5 is not a limb. It qualifies all of paragraphs 1 to 4: "The information referred to in
paragraphs 1 to 4 shall be provided to the natural persons concerned in a clear and distinguishable
manner at the latest at the time of the first interaction or exposure. The information shall conform
to the applicable accessibility requirements." No disclosed source records when a notice is shown or
whether it meets accessibility requirements, so every `supported-no-impact` record names that as an
open evidence gap rather than claiming full compliance. Paragraph 6 is a saving provision and imposes
no duty of its own.

## Trigger conditions

Each limb is evaluated against two register fields only, `output_type` and `exposed_group`. Nothing
reads free text, because a mapping that interpreted a use case description would be hiding legal
reasoning inside a data file.

| Limb | Trigger | Outcome when the trigger matches |
|---|---|---|
| `50-1` | `output_type` is `direct_interaction` | applies |
| `50-2` | `output_type` is one of `text`, `synthetic_image`, `synthetic_audio_video` | applies |
| `50-3` | `output_type` is `classification` | undetermined |
| `50-4a` | `output_type` is one of `synthetic_image`, `synthetic_audio_video` | undetermined |
| `50-4b` | `output_type` is `text` and `exposed_group` is `public` | applies |

A trigger that does not match means the obligation does not reach that system, and the pair goes to
`unaffected_items`.

Two limbs produce `undetermined` rather than `applies` even when their trigger matches, because the
register field is a necessary condition and not a sufficient one:

- `50-3` requires an emotion recognition system or a biometric categorisation system. `classification`
  is narrower than the whole register but wider than the statutory categories, and no disclosed source
  records what a classifier classifies. AI-005 is the only system that reaches this state. The
  evidence that would close it is the flagging criteria for Remote Proctor Signal, which he placed
  with the system owners and outside anything he can read, at E26 point six.
- `50-4a` requires content constituting a deep fake, which turns on whether the output resembles
  existing persons, objects, places, entities or events. `synthetic_image` and
  `synthetic_audio_video` do not settle that. AI-003 and AI-008 reach this state.

## What this mapping cannot decide, by design

1. Whether the school is provider or deployer for any system. Withheld for all eight, see
   `decision-policy.md` rule 2.
2. Whether a classifier is an emotion recognition or biometric categorisation system.
3. Whether generated image, audio or video constitutes a deep fake.
4. Whether the `50-1` obviousness exception applies to any system.
5. Whether a notice that exists satisfies paragraph 5 on timing and accessibility.

Each of these is a legal determination. The workflow names them, attaches the evidence that would
settle them, and stops.

## The mapping applied on 2026-09-04

Eight systems by five limbs, forty pairs. Legend: `-` obligation does not apply, `R` unresolved
pending the provider role determination, `A` unresolved pending applicability evidence, `C`
conflicting.

| System | Name | `output_type` | `exposed_group` | `50-1` | `50-2` | `50-3` | `50-4a` | `50-4b` |
|---|---|---|---|---|---|---|---|---|
| AI-001 | Learner Support Chat | `direct_interaction` | learners | R | - | - | - | - |
| AI-002 | Admissions Draft Assistant | `text` | applicants | - | R | - | - | - |
| AI-003 | Campaign Image Studio | `synthetic_image` | public | - | R | - | A | - |
| AI-004 | Pronunciation Coach | `direct_interaction` | learners | R | - | - | - | - |
| AI-005 | Remote Proctor Signal | `classification` | learners | - | - | A | - | - |
| AI-006 | Staff Summary Assistant | `text` | staff | - | R | - | - | - |
| AI-007 | Website Guide Avatar | `direct_interaction` | public | C | - | - | - | - |
| AI-008 | Video Localisation Tool | `synthetic_audio_video` | public | - | R | - | A | - |

Thirty pairs unaffected, six unresolved on role, three unresolved on applicability, one conflicting.
AI-007's `50-1` is `C` rather than `R` because the register and incident REC-008 both record the
evidence as conflicting; it carries the role blocker as well.

`50-4b` matches nothing. The two systems with `output_type` `text` are exposed to applicants and to
staff, and neither publishes to inform the public on matters of public interest.

## The data file

`scripts/article-50-limbs.json` holds one object per limb with these fields:

| Field | Meaning |
|---|---|
| `limb` | `50-1`, `50-2`, `50-3`, `50-4a`, `50-4b` |
| `binding_party` | `provider` or `deployer` |
| `duty` | The verbatim paragraph text quoted above |
| `source_paragraph` | The paragraph number on the Article 50 page the text was extracted from |
| `trigger` | `{"field": ..., "op": "eq" or "in", "values": [...]}`, or `{"all_of": [ ... ]}` |
| `on_match` | `applies` or `undetermined` |
| `authority_blocker` | The blocker text attached to every record this limb produces |
| `undetermined_reason` | Present only when `on_match` is `undetermined` |
| `required_next_evidence` | The evidence that would settle an undetermined applicability |

The expression grammar is deliberately three constructs wide, `eq`, `in` and `all_of`. A richer
grammar would let legal reasoning migrate into the data file without anyone noticing, and the point
of the file is that Legal can read the whole mapping without reading the script.

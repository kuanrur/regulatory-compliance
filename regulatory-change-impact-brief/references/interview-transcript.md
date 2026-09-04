# Interview transcript, Project B, 2026-09-04

Generated from the platform export, archived alongside as
export-project-b-regulatory-compliance-20260904-0628.md. Speaker H = Heisen Chen (Kuan's
in-scenario name, typed by her through the session), M = Compliance and Operations Manager.
Exchange numbers are the pointer targets for the discovery record and for every evidence_ids
value in the snapshots.

Message text is reproduced without re-wrapping, so the bodies here are byte-identical to the
export. File links handed over during an exchange are listed under it as `files:`.

28 exchanges, 56 messages, 12:20 AM to 02:27 AM.

---

## E1
H (12:20 AM): Hi, I'm Heisen Chen. I'm building an automated version of your regulatory change impact review, so I need to understand how you do it today. Do you have a few minutes?
M (12:20 AM): Hello Heisen. I definitely have a few minutes, because chasing down these Article 50 changes manually is exhausting. Every review starts with a mess of scattered evidence, conflicting system descriptions, and manual checks across our internal registers and the official guidance. To get started on how I actually do this work, let's look at the baseline sources I have to open first. I usually start by checking the Commission FAQ to quickly scan for likely issues, then confirm what is actually binding against the official rules and timeline.

## E2
H (12:25 AM): When was the last time you did one of these reviews? Take me through that one
M (12:25 AM): Our current internal review set is dated 26 August 2026 and covers eight AI-assisted systems used across Quillhaven Academy for learners, applicants, staff, and the public. When I initiate a review like this, the very first step is establishing a dated scope covering our review type, systems, audience, and approval gates, and then opening our primary records to check what we actually know about these systems. You can take a look at the AI-system register to see how these systems are initially logged.
  files: [AI-system register](https://docs.google.com/spreadsheets/d/10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU)

## E3
H (12:27 AM): Take me through the 26 August one specifically. What did you actually do, in order?
M (12:27 AM): For the 26 August 2026 review, I started by pulling together our scope of eight systems and opening the official implementation timeline alongside the Article 50 binding text to make sure we had our authority and timing basis straight. Once I had the rules in front of me, I went through our internal AI-use policy to check our baseline requirements. You can review that policy to see what controls we are supposed to be measuring against.
  files: [Internal AI-use policy](https://app.notion.com/p/3ba0b700541e81f09998d48f3b1c2856)

## E4
H (12:28 AM): What did you do next?
M (12:28 AM): After checking our policy controls, I had to look at what has actually been happening on the ground by reviewing our incident and evidence register to catch any recent operational failures, gaps, or conflicting descriptions for those eight systems.
  files: [Incident and evidence register](https://docs.google.com/spreadsheets/d/19BYZ68OSbsa1i9OfF6MzthrdC6q6mt6IWk6ucI8u7Rk)

## E5
H (12:29 AM): What did you do next?
M (12:29 AM): Once I pulled together the system register, our policy, and the incident records, I had to cross-reference everything against our compliance calendar to map out proposed actions, deadlines, and ownership for any gaps or impacts we found. You can check the compliance calendar to see how we track those dates and ownership.
  files: [Compliance calendar](https://docs.google.com/spreadsheets/d/1xtXl_P7Yb9LaECZjjgtlyI-idoAJTAhH-1gQ4vQaCGA)

## E6
H (12:30 AM): How did that one end?
M (12:30 AM): That review ended with a draft package that highlighted a mix of supported impacts, unresolved evidence gaps, and conflicting system descriptions across our eight systems. Because we have missing evidence and stale ownership details, I cannot finalize normal formal conclusions or sign off on operational changes myself. Instead, the package sits as pending input for Legal and Operations to review. Legal owns final interpretation of the binding rules, and Operations owns policy activation and deadline changes. My manual work stops at presenting the reconciled gaps and proposed actions for human review. What would you recommend for handling these incomplete records, and how would you keep a partial result from being mistaken for a complete one?

## E7
H (12:46 AM): Two tiers. If the binding text itself is unavailable, I don't get a choice: formal conclusions are blocked and the draft goes out marked unresolved. For any other missing source, my standing policy is a bounded partial, withhold and mark the conclusions that source touches, deliver the rest. I'd only block the whole run when I can't tell which conclusions the gap contaminates, because then it isn't bounded. That's what your 26 August review already did.  On not being mistaken for complete: it has to be visible where Legal and Operations actually read, limitations and pending decisions in the brief, a state and an approval state on every register row, pending approval on every calendar event.
M (12:46 AM): That distinction makes sense for keeping things moving without hiding our blind spots. As long as those unresolved rows and pending approvals stay screamingly obvious right where the reviewers look, we avoid anyone treating a partial draft as a clean bill of health. Since you are building out how this flows, do you want to look at the official binding text and timeline sources that anchor our baseline rules?

## E8
H (12:47 AM): Yes. Could you share the links for the binding text and the implementation timeline, and the Commission FAQ you mentioned earlier?
M (12:47 AM): Here are the official sources we use to anchor our legal and timing basis. You can review the Article 50 binding text, the official implementation timeline, and the Commission FAQ for the explanatory context.
  files: [Article 50 binding text](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50)
  files: [Official implementation timeline](https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline)
  files: [Commission Article 50 FAQ](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act)

## E9
H (12:49 AM): Of those three, which ones bind us, and which are guidance?
M (12:49 AM): The Article 50 binding text is our hard legal authority, and the official implementation timeline establishes the binding dates and deadlines. The Commission FAQ is just helpful explanatory context for interpreting how those rules apply in practice, but it does not carry the force of law itself.
  files: [Article 50 binding text](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50)
  files: [Official implementation timeline](https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline)
  files: [Commission Article 50 FAQ](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act)

## E10
H (12:50 AM): For those eight systems, where are we the provider and where are we the deployer?
M (12:51 AM): Whether we act as the provider or the deployer depends entirely on the specific system facts and who built or supplied it versus who put it into operational use at Quillhaven. You can check the AI-system register to see how provider and deployer roles are logged across those eight systems.
  files: [AI-system register](https://docs.google.com/spreadsheets/d/10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU)

## E11
H (01:00 AM): The register flags AI-007 as conflicting and AI-005 as stale with provider_role unknown. When was the last time a logged value in that register turned out to be wrong, and how did you find out?
M (01:00 AM): I do not track a formal frequency or timestamp for when logged values turn out to be wrong, but I usually find out about discrepancies during these manual review cycles when I check system owner descriptions against actual operational practices or incident logs. For instance, when an owner claims a system only generates internal recommendations but our incident register shows it interacting directly with applicants, that conflict forces me to flag it as unresolved until the owner and Legal straighten it out.

## E12
H (01:02 AM): What would close one of those?
M (01:02 AM): To close out a conflicting or unknown provider role, we need concrete written evidence from the vendor contract or system deployment records confirming who built and placed the system into service, followed by a formal sign-off from Legal to update the record.

## E13
H (01:03 AM): Who owns each of those sources? Not the systems, the sources themselves
M (01:03 AM): For our internal sources, Operations and I maintain the compliance calendar and the incident register, the system owners maintain their entries in the AI-system register, and leadership owns the internal AI-use policy. For the external sources, the European Commission owns the binding text, the implementation timeline, and the FAQ.

## E14
H (01:06 AM): What dates apply to this review?
M (01:06 AM): The current review is set as of 26 August 2026, and the compliance calendar maps out our upcoming milestone dates from there. You can check the specific scheduled dates and deadlines in the compliance calendar.
  files: [Compliance calendar](https://docs.google.com/spreadsheets/d/1xtXl_P7Yb9LaECZjjgtlyI-idoAJTAhH-1gQ4vQaCGA)

## E15
H (01:15 AM): The implementation timeline gives a 2 December 2026 transitional deadline for synthetic content systems placed on the market before 2 August 2026. Campaign Image Studio and Video Localisation Tool are our two synthetic content systems. Were either of them placed on the market before 2 August 2026?
M (01:15 AM): I have to check the deployment records and the AI-system register to confirm the exact date those two systems were placed on the market, because relying on memory or assumptions here isn't enough when we're facing a hard transitional deadline.
  files: [AI-system register](https://docs.google.com/spreadsheets/d/10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU)

## E16 (claim contradicted by the file: the register has no deployment date column)
H (01:19 AM): Could you share the deployment records?
M (01:19 AM): I do not have a separate standalone deployment records document; the deployment dates and system facts we rely on are maintained directly within the AI-system register.
  files: [AI-system register](https://docs.google.com/spreadsheets/d/10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU)

## E17 (retreat from E16; deployment date becomes a named evidence gap)
H (01:21 AM): I've read the register and I don't see a placed-on-market or deployment date column. Which one holds it?
M (01:21 AM): If that specific column isn't populated or clearly labeled in the system register, it usually means the system owner hasn't provided that deployment date yet, which is one of the evidence gaps we frequently have to chase down. When those details are missing, I cross-reference our incident and evidence register to see if any past support tickets or deployment notes mention when it went live.
  files: [Incident and evidence register](https://docs.google.com/spreadsheets/d/19BYZ68OSbsa1i9OfF6MzthrdC6q6mt6IWk6ucI8u7Rk)

## E18 (a required internal source is unavailable, on record)
H (01:29 AM): I can't open the Internal AI-use policy link, it returns no access. Is there a version I can read?
M (01:29 AM): All internal links are viewer-only, so you will need to request access directly through our internal permissions workflow if your account is not provisioned. I cannot export or bypass access controls for the internal AI-use policy.

## E19 (what he does when a source is inaccessible; the business-practice basis for the partial policy)
H (01:34 AM): What do you normally do when a source you need is behind access you don't have?
M (01:34 AM): When an internal source is locked or inaccessible, I usually have to reach out directly to the owner of that document—in this case, leadership for the internal AI-use policy—to request the specific details or excerpts I need for the review. If they are unavailable or cannot provide it, the affected review items have to stay marked as pending or blocked until we get proper access.

## E20 (the role question: proprietary weights, custom fine-tuning, branding)
H (01:37 AM): The register lists us as deployer and not provider for all eight systems, but ACT-001, ACT-004 and ACT-006 in the compliance calendar are provider-side obligations under Article 50(1) and 50(2). How did that come about?
M (01:37 AM): That mismatch is exactly why these reviews are so painful to untangle. Often a system owner marks us as a deployer in the register, but when we look at how the tool is actually used or configured, we might have added proprietary weights, custom fine-tuning, or branding that potentially pushes us into provider territory under the regulation. When I spot a conflict like that between our register entries and the binding obligations, I have to flag it as an unresolved evidence gap and check our incident register to see if any past technical tickets or deployment notes clarify our true role. Then I have to escalate it to Legal and the system owners to get a formal determination before we can settle those obligations.
  files: [Incident and evidence register](https://docs.google.com/spreadsheets/d/19BYZ68OSbsa1i9OfF6MzthrdC6q6mt6IWk6ucI8u7Rk)

## E21
H (01:54 AM): How does Remote Proctor Signal decide which sessions to flag?
M (01:54 AM): I have to check the system owner's detailed technical description and documentation for Remote Proctor Signal to see what criteria or automated signals it uses to flag a session. Let's look at the entries in the AI-system register to see what the owner recorded.
  files: [AI-system register](https://docs.google.com/spreadsheets/d/10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU)

## E22
H (01:55 AM): Can I get that technical description?
M (01:55 AM): If the specific technical description for Remote Proctor Signal is missing or thin in the register, I usually have to check our incident and evidence register to see if a support ticket or vendor communication sheds light on its flagging criteria, and then ping the system owner directly to get an accurate accounting.
  files: [AI-system register](https://docs.google.com/spreadsheets/d/10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU)
  files: [Incident and evidence register](https://docs.google.com/spreadsheets/d/19BYZ68OSbsa1i9OfF6MzthrdC6q6mt6IWk6ucI8u7Rk)

## E23 (approval gates, in order)
H (01:56 AM): What approval gates does this package pass through, and in what order?
M (01:56 AM): The review package first goes through my own manual reconciliation of the sources, evidence gaps, and calendar dates to draft the impacts and proposed actions. Once the draft package is assembled, it must pass through formal review gates: Legal owns final interpretation of our obligations and risk status, while Operations owns policy activation, approved deadline changes, and incident closure before anything is finalized.
  files: [Compliance calendar](https://docs.google.com/spreadsheets/d/1xtXl_P7Yb9LaECZjjgtlyI-idoAJTAhH-1gQ4vQaCGA)

## E24 (never-automate list)
H (02:01 AM): What in this process must the automation never do on its own?
M (02:01 AM): Automation must never make legal or operational approvals on its own. It cannot establish binding interpretations, determine final system applicability, override source authority, change compliance deadlines, close incidents, or bypass the mandatory review gates owned by Legal and Operations.

## E25 (what must not leave the business)
H (02:08 AM): What information must not leave the business?
M (02:08 AM): We must not let internal personal data, unredacted staff or learner records, confidential incident details, or preliminary legal interpretations leave the business or be processed by external third-party tools without proper governance and authorization.

## E26 (say-back, itemised; eight points confirmed, point nine corrected)
H (02:21 AM): Before we finish, let me check I have this right, point by point.  One. Scope is the eight AI-assisted systems, for learners, applicants, staff and the public. This is a change-triggered review of the Article 50 obligations that took effect on 2 August 2026, not the quarterly register review scheduled for 2 October, and each run anchors to the date it actually runs, not to 26 August.  Two. The Article 50 binding text and the implementation timeline bind us. The Commission FAQ is guidance only and carries no force of law.  Three. Source ownership: you and Operations hold the compliance calendar and the incident register, the system owners hold their own entries in the AI-system register, leadership holds the internal AI-use policy, and the Commission holds the three external sources.  Four. The internal AI-use policy is not readable by me. Anything resting on policy controls stays pending or blocked until leadership supplies it, and I will not treat its absence as evidence of compliance.  Five. On role: the register records us as deployer for all eight, but configuration may have pushed us into provider territory. Until Legal and the system owners make a formal determination, that is undetermined, not mis-recorded. So no provider-side obligation under Article 50(1) or 50(2) is settled for any system, while deployer-side obligations under 50(3) and 50(4) are not in doubt and still get delivered.  Six. Two things sit with the system owners and nowhere I can read: the placed-on-market or deployment dates, since the register has no such column, and the flagging criteria for Remote Proctor Signal.  Seven. An impact is established only when the underlying evidence is complete and uncontested and applicability is settled. Otherwise it stays unresolved, with an owner and the specific evidence that would close it. On that rule, Learner Support Chat and Staff Summary Assistant look unaffected on every obligation this review has examined, and that holds regardless of how the role question resolves. The one limb I have not examined for either is whether their text output falls under the machine-readable marking obligation, because none of your sources addresses marking for the text systems.  Eight. Gates in order: your own reconciliation, then Legal for final interpretation of obligations and risk status, then Operations for policy activation, approved deadline changes and incident closure. The automation never makes those calls, never determines final applicability, never overrides source authority, never changes a deadline, never closes an incident, and never bypasses those gates.  Nine. The owner values in the register are departments, and I am treating those as the responsible owners. You mentioned stale ownership details in the 26 August review, so tell me if that is wrong.  Where is that wrong?
M (02:21 AM): Your summary is mostly spot on for how we handle the review, but on your ninth point regarding ownership, treating department names as the responsible owners is actually one of our recurring pain points. Those department-level entries in the AI-system register are often stale or generic, and in practice, we usually have to track down the specific named individual owner or system custodian listed in the incident register or talk to Operations to find out who currently owns the risk before any proposed action can move forward.
Note: the correction landed on point nine only, the one point about his own operational practice.
Points one to eight, which are legal structure and classification, drew a single "mostly spot on".
Point five was pre-registered in say-back-prediction.md as the one most likely to be corrected, and
it was not. Per that pre-registration the say-back therefore does not support the "undetermined, not
mis-recorded" framing, which continues to rest on his own words in E20 alone.

## E27 (the E26 claim tested against the incident register, and retracted)
H (02:26 AM): I've read all ten records in the incident register. Its owner column holds the same seven department names as the AI-system register, and there are no personal names in any field. Where would the named individual owner actually come from?
M (02:26 AM): That is a very fair catch. Since neither register holds personal names and only lists those seven department names, those department entries are all we have as formal owners in the records. When I talk about tracking down a specific person, it is usually an informal game of chasing down whoever is currently sitting in that department's lead role or handling the system support desk when an issue actually pops up, rather than finding a formal individual name written down in the spreadsheets.
  files: [Incident and evidence register](https://docs.google.com/spreadsheets/d/19BYZ68OSbsa1i9OfF6MzthrdC6q6mt6IWk6ucI8u7Rk)
  files: [AI-system register](https://docs.google.com/spreadsheets/d/10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU)
Note: second instance of a claim about where a field lives being contradicted by the file. E16 put
deployment dates in the AI-system register, which has no such column. E26 put named individual owners
in the incident register, whose owner column holds the same seven department names as the AI-system
register. Retracted here: the department entries are all there is as formal owners of record, and
finding a person is informal. A named individual owner is therefore NOT required next evidence,
because no formal one exists to obtain.

## E28 (closing question, exact SOME wording)
H (02:27 AM): Is there something else you want to address today?
M (02:27 AM): We have covered a lot of ground today, from tracking down those department-level owners to locking down our review gates and boundaries. The main thing left is for you to pull together the draft package keeping all those evidence gaps and unresolved items clearly visible so we can take them to Legal and Operations when you are ready.


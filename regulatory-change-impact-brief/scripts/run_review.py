# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.21", "rfc3339-validator>=0.1.4"]
# ///
"""Article 50 regulatory change impact review.

One deterministic pass over the disclosed sources. Writes seven stage snapshots as each stage
completes, then the impact register, the compliance brief and the draft action calendar.

The rules this script implements are documented in ../SKILL.md and ../references/. Nothing here
decides anything by reading the situation: obligation limbs come from article-50-limbs.json,
source authority and retrieval tests come from sources.json.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parent
SCRIPT_DIR = Path(__file__).resolve().parent
DELIVERABLES = REPO_ROOT / "deliverables"
SNAPSHOTS = DELIVERABLES / "snapshots"

REVIEW_TYPE = "change-triggered review of EU AI Act Article 50 transparency obligations"
AUDIENCES = ["learners", "applicants", "staff", "the public"]
APPROVAL_GATES = [
    "Compliance and Operations Manager reconciliation",
    "Legal interpretation",
    "Operations activation",
]
SCOPE_RULE = "every AI system recorded in the AI-system register as at as_of"
SCOPE_RECORD_ID = "SCOPE-FRAME"
OBLIGATION_EFFECTIVE = "2026-08-02"

MAX_RUN_ATTEMPTS = 2  # one pass, plus at most one rewind. Decision rule 6.
FETCH_ATTEMPTS = 3
FETCH_BACKOFF_SECONDS = 2
FETCH_TIMEOUT_SECONDS = 60
USER_AGENT = "regulatory-change-impact-brief/1.0 (read-only compliance review)"

STAGES = [
    (1, "scope", "01-scope.json"),
    (2, "source-capture", "02-source-capture.json"),
    (3, "authority-and-timing", "03-authority-and-timing.json"),
    (4, "evidence-reconciliation", "04-evidence-reconciliation.json"),
    (5, "impact-analysis", "05-impact-analysis.json"),
    (6, "actions-and-approvals", "06-actions-and-approvals.json"),
    (7, "publication-validation", "07-publication-validation.json"),
]


# --------------------------------------------------------------------------- helpers


def sha256_of(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_text(raw: bytes) -> str:
    body = raw.decode("utf-8", errors="replace")
    body = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", body)))


def extract_lines(raw: bytes) -> list[str]:
    """Tag boundaries become line breaks, so a page's heading structure survives extraction."""
    body = raw.decode("utf-8", errors="replace")
    body = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body)
    body = html.unescape(re.sub(r"<[^>]+>", "\n", body))
    return [norm(line) for line in body.split("\n") if norm(line)]


def rec(record_id: str, summary: str, evidence_ids: list[str], **extra) -> dict:
    out = {"id": record_id, "summary": summary, "evidence_ids": list(evidence_ids)}
    out.update(extra)
    return out


def decision(record_id: str, summary: str, evidence_ids: list[str], rationale: str,
             tradeoffs: list[str]) -> dict:
    return rec(record_id, summary, evidence_ids, rationale=rationale, tradeoffs=list(tradeoffs))


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


# --------------------------------------------------------------------------- parsers


def parse_article50_paragraphs(text: str) -> dict[int, str]:
    start = text.find("Providers shall ensure")
    if start < 0:
        return {}
    segment = text[start - 40:start + 12000]
    marks = [(m.start(), int(m.group(1))) for m in re.finditer(r"(?<=[.\s])(\d)\.\s{1,4}(?=[A-Z])", segment)]
    marks = [(pos, num) for pos, num in marks if 1 <= num <= 6]
    out: dict[int, str] = {}
    for index, (pos, num) in enumerate(marks):
        end = marks[index + 1][0] if index + 1 < len(marks) else pos + 1600
        if num not in out:
            out[num] = norm(segment[pos:end])
    if 1 not in out:
        out[1] = norm(segment[40:marks[0][0]]) if marks else ""
    return {n: t for n, t in out.items() if t}


MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
DATE_HEADING = re.compile(r"^(\d{2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})$")


def heading_to_iso(label: str) -> str:
    match = DATE_HEADING.fullmatch(label)
    return f"{match.group(3)}-{MONTHS[match.group(2)]:02d}-{match.group(1)}" if match else ""


def parse_timeline(lines: list[str]) -> list[tuple[str, list[str]]]:
    """A date heading is a line that is only a date. Dates inside a sentence are not headings."""
    out: list[tuple[str, list[str]]] = []
    current: tuple[str, list[str]] | None = None
    for line in lines:
        if DATE_HEADING.fullmatch(line):
            current = (line, [])
            out.append(current)
        elif current is not None:
            current[1].append(line)
    return out


def parse_csv(raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig", errors="replace")))
    rows = [dict(r) for r in reader]
    return list(reader.fieldnames or []), rows


def parse_transcript_exchanges(text: str) -> set[str]:
    return {m.group(1) for m in re.finditer(r"(?m)^## (E\d+)\b", text)}


# --------------------------------------------------------------------------- retrieval


def fetch_remote(url: str) -> dict:
    last_error = ""
    for attempt in range(1, FETCH_ATTEMPTS + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
                body = response.read()
                return {
                    "ok": True,
                    "status": response.status,
                    "content_type": response.headers.get("Content-Type", ""),
                    "body": body,
                    "attempts": attempt,
                    "error": None,
                }
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            return {"ok": False, "status": exc.code, "content_type": "", "body": b"",
                    "attempts": attempt, "error": last_error}
        except Exception as exc:  # transport failure, worth retrying
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < FETCH_ATTEMPTS:
                time.sleep(FETCH_BACKOFF_SECONDS)
    return {"ok": False, "status": None, "content_type": "", "body": b"",
            "attempts": FETCH_ATTEMPTS, "error": last_error}


def apply_success_test(source: dict, fetched: dict) -> tuple[bool, str, dict]:
    """Return (passed, test_applied, parsed_payload)."""
    test = source.get("success_test", {})
    applied: list[str] = []
    payload: dict = {}
    body = fetched["body"]

    if not fetched["ok"]:
        return False, "transport", payload

    if "content_type_contains" in test:
        applied.append("content_type_contains")
        if test["content_type_contains"] not in (fetched["content_type"] or ""):
            return False, "+".join(applied), payload

    if source["content_kind"] == "csv":
        headers, rows = parse_csv(body)
        payload = {"headers": headers, "rows": rows}
        if "required_columns" in test:
            applied.append("required_columns")
            missing = [c for c in test["required_columns"] if c not in headers]
            if missing:
                payload["missing_columns"] = missing
                return False, "+".join(applied), payload
        return True, "+".join(applied), payload

    text = extract_text(body) if source["content_kind"] == "html" else norm(
        body.decode("utf-8", errors="replace"))
    payload["text"] = text
    payload["raw_text"] = body.decode("utf-8", errors="replace")
    if source["content_kind"] == "html":
        payload["lines"] = extract_lines(body)

    if "min_extracted_chars" in test:
        applied.append("min_extracted_chars")
        if len(text) < test["min_extracted_chars"]:
            return False, "+".join(applied), payload

    for needle in test.get("must_contain", []):
        applied.append("must_contain")
        if needle not in text:
            return False, "+".join(applied), payload

    parser = test.get("must_parse")
    if parser == "article50_paragraphs":
        applied.append("article50_paragraphs")
        paragraphs = parse_article50_paragraphs(text)
        payload["paragraphs"] = paragraphs
        if not all(len(paragraphs.get(n, "")) > 200 for n in (1, 2, 3, 4)):
            return False, "+".join(applied), payload
    elif parser == "timeline_headings":
        applied.append("timeline_headings")
        headings = parse_timeline(payload.get("lines", []))
        payload["timeline"] = headings
        flat = " ".join(e for _, entries in headings for e in entries)
        if len(headings) < 4 or not re.search(r"Article 50|transparency rules", flat, re.I):
            return False, "+".join(applied), payload
    elif parser == "transcript_exchanges":
        applied.append("transcript_exchanges")
        exchanges = parse_transcript_exchanges(payload["raw_text"])
        payload["exchanges"] = exchanges
        if not {f"E{n}" for n in range(1, 29)} <= exchanges:
            return False, "+".join(applied), payload

    return True, "+".join(applied) or "none", payload


def capture_sources(sources: list[dict], as_of: str, force_invalid: set[str]) -> tuple[list[dict], dict]:
    records: list[dict] = []
    payloads: dict[str, dict] = {}
    for source in sources:
        key = source["key"]
        if source["transport"] == "local":
            path = SKILL_DIR / source["locator"]
            if path.exists():
                body = path.read_bytes()
                fetched = {"ok": True, "status": None, "content_type": "text/markdown",
                           "body": body, "attempts": 1, "error": None}
            else:
                fetched = {"ok": False, "status": None, "content_type": "", "body": b"",
                           "attempts": 1, "error": "file not found"}
        else:
            fetched = fetch_remote(source["locator"])

        passed, applied, payload = apply_success_test(source, fetched)
        if key in force_invalid:
            passed, applied = False, applied + "+stage03-recheck"

        status = "retrieved" if passed else source["failure_status"]
        text = payload.get("text") or (
            norm(fetched["body"].decode("utf-8", errors="replace")) if fetched["body"] else "")
        version_metadata = {
            "identifier_on_page": None,
            "recorded_as": "retrieved_at plus content_hash",
            "note": "This page carries no version identifier, so identity is recorded as the "
                    "retrieval time and the content hash. Our decision, not the stakeholder's.",
        } if source["content_kind"] == "html" and source["authority"] == "binding" else None

        records.append(rec(
            f"SRC-{key}",
            source["summary"],
            [] if not source["disclosed_at"] else list(source["disclosed_at"]),
            source_role=source["source_role"],
            authority=source["authority"],
            locator=source["locator"],
            retrieved_at=as_of if source["transport"] == "local" else utc_now(),
            retrieval_status=status,
            content_type=fetched["content_type"] or source["content_kind"],
            version_metadata=version_metadata,
            content_hash=sha256_of(fetched["body"]) if fetched["body"] else None,
            local_reference=source["locator"] if source["transport"] == "local" else None,
            owner=source["owner"],
            transport=source["transport"],
            http_status=fetched["status"],
            raw_bytes=len(fetched["body"]),
            extracted_chars=len(text),
            fetch_attempts=fetched["attempts"],
            fetch_error=fetched["error"],
            success_test_applied=applied,
            normalised_text_sha256=sha256_of(text.encode("utf-8")) if text else None,
            withholds_on_failure=source["withholds_on_failure"],
        ))
        payloads[key] = {"payload": payload, "status": status, "fetched": fetched}
    return records, payloads


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- snapshot io


class Trail:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self.previous: dict | None = None
        self.written: list[dict] = []

    def write(self, sequence: int, stage: str, filename: str, status: str, state: dict,
              consumed: list[str], produced: list[str], decisions: list[dict],
              unresolved: list[dict]) -> dict:
        snapshot = {
            "schema_version": "regulatory-compliance-stage-snapshot/2",
            "snapshot_id": f"{self.run_id}-{sequence:02d}-{stage}",
            "run_id": self.run_id,
            "stage": stage,
            "sequence": sequence,
            "created_at": utc_now(),
            "status": status,
            "predecessor": None if self.previous is None else {
                "snapshot_id": self.previous["snapshot_id"],
                "path": self.previous["path"],
                "sha256": self.previous["sha256"],
            },
            "consumed_record_ids": dedupe(consumed),
            "produced_record_ids": dedupe(produced),
            "state": state,
            "unresolved": unresolved,
            "decisions": decisions,
        }
        path = SNAPSHOTS / filename
        payload = (json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        path.write_bytes(payload)
        self.previous = {
            "snapshot_id": snapshot["snapshot_id"],
            "path": f"deliverables/snapshots/{filename}",
            "sha256": sha256_of(payload),
        }
        self.written.append(snapshot)
        return snapshot

    def reset(self) -> None:
        self.previous = None
        self.written = []


def dedupe(values: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for value in values:
        if value:
            seen[value] = None
    return list(seen)


# --------------------------------------------------------------------------- limb logic


def trigger_matches(trigger: dict, row: dict[str, str]) -> bool:
    if "all_of" in trigger:
        return all(trigger_matches(t, row) for t in trigger["all_of"])
    value = row.get(trigger["field"], "")
    if trigger["op"] == "eq":
        return value == trigger["value"]
    if trigger["op"] == "in":
        return value in trigger["values"]
    raise ValueError(f"unsupported trigger operator: {trigger['op']}")


def trigger_summary(trigger: dict) -> str:
    if "all_of" in trigger:
        return " and ".join(trigger_summary(t) for t in trigger["all_of"])
    if trigger["op"] == "eq":
        return f"{trigger['field']} is {trigger['value']}"
    return f"{trigger['field']} is one of {', '.join(trigger['values'])}"


NOTICE_PRESENT = {"yes", "visible_label"}


def classify(limb: dict, row: dict[str, str], binding_available: bool) -> dict:
    """Apply the six layer state precedence documented in SKILL.md."""
    limb_id = limb["limb"]
    evidence_status = row.get("evidence_status", "")
    notice = row.get("current_notice", "")

    if not trigger_matches(limb["trigger"], row):
        return {
            "array": "unaffected_items",
            "state": None,
            "applicability": "does-not-apply",
            "layer": 1,
            "reason": (f"Article {limb_id} does not apply: the trigger condition "
                       f"{trigger_summary(limb['trigger'])} is not met "
                       f"({row.get('output_type', '')} output, exposed to "
                       f"{row.get('exposed_group', '')})."),
        }

    if not binding_available:
        return {
            "array": "impacts", "state": "unresolved", "applicability": "undetermined", "layer": 0,
            "reason": ("The Article 50 binding text could not be retrieved on this run, so no "
                       "formal conclusion is drawn for any limb."),
        }

    if limb["on_match"] == "undetermined":
        return {
            "array": "impacts", "state": "unresolved", "applicability": "undetermined", "layer": 2,
            "reason": (f"Applicability of Article {limb_id} cannot be determined from the disclosed "
                       f"sources: {limb['undetermined_reason']} Required next evidence: "
                       f"{limb['required_next_evidence']}"),
        }

    if evidence_status == "conflicting":
        return {
            "array": "impacts", "state": "conflicting", "applicability": "applies", "layer": 3,
            "reason": ("The AI-system register records evidence_status conflicting for this system. "
                       "The conflict is recorded, not adjudicated."),
        }

    if limb["binding_party"] == "provider":
        return {
            "array": "impacts", "state": "unresolved", "applicability": "applies", "layer": 4,
            "reason": (f"Article {limb_id} binds providers. The provider role is undetermined for "
                       f"every system pending a formal determination by Legal and the system "
                       f"owners."),
        }

    if evidence_status in {"partial", "stale", "missing"}:
        return {
            "array": "impacts", "state": "unresolved", "applicability": "applies", "layer": 5,
            "reason": (f"Article {limb_id} applies, but the register records evidence_status "
                       f"{evidence_status}, so no conclusion is established. Required next "
                       f"evidence: complete and uncontested evidence of the disclosure practice "
                       f"for this system."),
        }

    if notice in NOTICE_PRESENT:
        return {
            "array": "impacts", "state": "supported-no-impact", "applicability": "applies",
            "layer": 6,
            "reason": (f"Article {limb_id} applies and the register records current_notice "
                       f"{notice} with evidence_status complete. Timing and accessibility under "
                       f"Article 50(5) are not evidenced by any disclosed source."),
        }

    return {
        "array": "impacts", "state": "supported-impact", "applicability": "applies", "layer": 6,
        "reason": (f"Article {limb_id} applies and the register records current_notice {notice} "
                   f"with evidence_status complete, so the obligation is not met."),
    }


# --------------------------------------------------------------------------- stage builders


def build_stage_03(payloads: dict, limbs: list[dict], as_of_date: str) -> tuple[dict, list[dict], list[str], list[str]]:
    art = payloads["ART50"]
    timeline = payloads["TIMELINE"]
    faq = payloads["FAQ"]
    binding_available = art["status"] == "retrieved"
    paragraphs = art["payload"].get("paragraphs", {})

    binding_rules = []
    for limb in limbs:
        text = paragraphs.get(limb["source_paragraph"], "")
        binding_rules.append(rec(
            f"RULE-{limb['limb']}",
            f"Article {limb['limb']} binds {limb['binding_party']}s: {limb['duty']}",
            ["SRC-ART50"],
            binding_party=limb["binding_party"],
            source_paragraph=limb["source_paragraph"],
            paragraph_text_retrieved=bool(text),
            trigger=trigger_summary(limb["trigger"]),
            on_match=limb["on_match"],
        ))

    timing_rules = []
    transitional_ids: list[str] = []
    for date_label, entries in timeline["payload"].get("timeline", []):
        for entry in entries:
            if not re.search(r"Article 50|transparency rules", entry, re.I):
                continue
            amended = "**" in entry
            iso_date = heading_to_iso(date_label)
            transitional = bool(re.search(r"50\(2\)", entry)
                                and re.search(r"transition", entry, re.I))
            if transitional:
                applicable_now = False
                reasons = [
                    "No disclosed source records placed on market or deployment dates, so no "
                    "system can be shown to fall inside the transitional population.",
                    "The provider role is undetermined for all eight systems, and this deadline "
                    "binds providers.",
                ]
            elif iso_date and iso_date <= as_of_date:
                applicable_now, reasons = True, []
            else:
                applicable_now = False
                reasons = ["The date has not been reached as at the review as-of date."]
            record_id = f"TIME-{date_label.replace(' ', '')}-{slugify(entry)[:40]}"
            if transitional:
                transitional_ids.append(record_id)
            timing_rules.append(rec(
                record_id,
                f"{date_label}: {norm(entry)}",
                ["SRC-TIMELINE"],
                date=date_label,
                iso_date=iso_date,
                amended_by_digital_omnibus=amended,
                applicable_now=applicable_now,
                not_applicable_reasons=reasons,
                note=("Marked with a double asterisk on the timeline page, meaning it was amended by "
                      "the Digital Omnibus on AI." if amended else None),
            ))
    if not timing_rules:
        timing_rules.append(rec(
            "TIME-NONE", "No Article 50 timing entry could be read from the implementation timeline.",
            ["SRC-TIMELINE"]))

    guidance_context = [rec(
        "GUID-faq-article-50",
        "Commission FAQ on transparency obligations under Article 50. Advisory only, and it does "
        "not carry the force of law itself.",
        ["SRC-FAQ", "E9"],
        label="advisory",
        may_be_sole_basis=False,
        retrieved=faq["status"] == "retrieved",
    )]

    blockers = [rec(
        "BLK-provider-role",
        "Whether Quillhaven Academy is provider or deployer is undetermined for all eight systems. "
        "Every provider limb conclusion is withheld pending a formal determination.",
        ["SRC-REGISTER", "E20", "E26"],
        owner="Legal and the system owners",
    )]
    for limb in limbs:
        blockers.append(rec(
            f"BLK-{limb['limb']}",
            limb["authority_blocker"],
            ["SRC-ART50", f"RULE-{limb['limb']}"],
            owner="Legal",
        ))

    state = {
        "binding_rules": binding_rules,
        "timing_rules": timing_rules,
        "guidance_context": guidance_context,
        "authority_blockers": blockers,
    }
    decisions = []
    if transitional_ids:
        decisions.append(decision(
            "DEC-record-inapplicable-timing",
            "The Article 50(2) transitional deadline of 02 Dec 2026 is recorded in timing_rules and "
            "marked as not applicable to any system on this run, with both reasons.",
            ["SRC-TIMELINE", "BLK-provider-role"] + transitional_ids,
            "The deadline cannot be applied today because no source records placed on market dates "
            "and the provider role is undetermined. Recording it anyway means that the moment Legal "
            "settles the role the rule is already in the trail, and a reviewer can see that this "
            "run knew the deadline exists rather than having missed it.",
            ["timing_rules carries a rule that applies to nothing on this run, which reads as "
             "clutter until the role question is settled.",
             "A reader could mistake a recorded rule for an active obligation, so the record "
             "carries applicable_now false and names both reasons."]))
    produced = [r["id"] for group in state.values() for r in group]
    consumed = ["SRC-ART50", "SRC-TIMELINE", "SRC-FAQ"]
    return state, decisions, consumed, produced


def build_stage_04(payloads: dict, as_of_date: str) -> tuple[dict, list[str], list[str], dict]:
    register_rows = payloads["REGISTER"]["payload"].get("rows", [])
    incident_rows = payloads["INCIDENT"]["payload"].get("rows", [])
    calendar_rows = payloads["CALENDAR"]["payload"].get("rows", [])
    policy_status = payloads["POLICY"]["status"]

    tracked = ["output_type", "exposed_group", "provider_role", "deployer_role",
               "current_notice", "evidence_status", "evidence_updated_at"]
    system_facts = []
    for row in register_rows:
        for field in tracked:
            system_facts.append(rec(
                f"FACT-{row['system_id']}-{field}",
                f"{row['system_id']} {row.get('system_name', '')}: {field} is "
                f"{row.get(field, '') or 'empty'}.",
                ["SRC-REGISTER"],
                system_id=row["system_id"], field=field, value=row.get(field, ""),
            ))

    policy_controls = []
    incident_evidence = [rec(
        f"INC-{row['record_id']}",
        f"{row['record_id']} on {row['system_id']}, {row.get('record_type', '')} reported "
        f"{row.get('reported_at', '')}, status {row.get('status', '')}, evidence state "
        f"{row.get('evidence_state', '')}.",
        ["SRC-INCIDENT"],
        system_id=row["system_id"], owner=row.get("owner", ""),
        status=row.get("status", ""), evidence_state=row.get("evidence_state", ""),
    ) for row in incident_rows]

    register_status = {row["system_id"]: row.get("evidence_status", "") for row in register_rows}
    conflicts = []
    for row in incident_rows:
        system = row["system_id"]
        if row.get("evidence_state") == "conflicting" and register_status.get(system) != "conflicting":
            conflicts.append(rec(
                f"CFL-{system}-evidence-quality",
                f"The AI-system register records evidence_status "
                f"{register_status.get(system, 'unknown')} for {system}, while incident "
                f"{row['record_id']} records evidence_state conflicting. The two sources disagree. "
                f"Both readings are recorded and neither is marked correct.",
                ["SRC-REGISTER", "SRC-INCIDENT", f"FACT-{system}-evidence_status",
                 f"INC-{row['record_id']}"],
                owner=row.get("owner", ""),
            ))
    conflicts.append(rec(
        "CFL-ALL-deployment-dates",
        "Testimony at E16 placed deployment dates in the AI-system register. The register has no "
        "such column. He retreated from the claim at E17. Recorded as testimony against record.",
        ["SRC-REGISTER", "E16", "E17"],
        owner="The system owners",
    ))
    conflicts.append(rec(
        "CFL-ALL-owner-names",
        "Testimony at E26 placed named individual owners in the incident register. Its owner column "
        "holds department names only. He retracted at E27. Recorded as testimony against record.",
        ["SRC-INCIDENT", "E26", "E27"],
        owner="Operations",
    ))
    register_audiences = sorted({row.get("exposed_group", "") for row in register_rows} - {""})
    declared = {a.replace("the ", "") for a in AUDIENCES}
    if set(register_audiences) != declared:
        conflicts.append(rec(
            "CFL-ALL-audiences",
            f"Stage 01 declared audiences {sorted(declared)} while the register records "
            f"exposed_group values {register_audiences}.",
            ["SRC-REGISTER"], owner="The Compliance and Operations Manager"))

    evidence_gaps = [rec(
        "GAP-ALL-policy-controls",
        f"The internal AI-use policy is {policy_status}, so stage 04 policy_controls is withheld in "
        f"full. Its absence is not evidence of compliance.",
        ["SRC-POLICY", "E3", "E19"], owner="Leadership"),
        rec("GAP-ALL-placed-on-market",
            "No disclosed source records placed on market or deployment dates, so the Article 50(2) "
            "transitional deadline cannot be applied to any system.",
            ["SRC-REGISTER", "E17"], owner="The system owners"),
        rec("GAP-ALL-notice-timing",
            "No disclosed source records when a notice is shown or whether it meets accessibility "
            "requirements, so Article 50(5) cannot be evidenced for any system.",
            ["SRC-REGISTER", "SRC-ART50"], owner="The system owners")]
    for row in register_rows:
        updated = row.get("evidence_updated_at", "")
        if updated and updated < OBLIGATION_EFFECTIVE:
            evidence_gaps.append(rec(
                f"GAP-{row['system_id']}-evidence-predates-obligation",
                f"{row['system_id']} evidence was last updated {updated}, before the Article 50 "
                f"obligations took effect on {OBLIGATION_EFFECTIVE}.",
                ["SRC-REGISTER", f"FACT-{row['system_id']}-evidence_updated_at"],
                owner=row.get("owner", "")))

    state = {
        "system_facts": system_facts,
        "policy_controls": policy_controls,
        "incident_evidence": incident_evidence,
        "conflicts": conflicts,
        "evidence_gaps": evidence_gaps,
    }
    produced = [r["id"] for group in state.values() for r in group]
    consumed = ["SRC-REGISTER", "SRC-INCIDENT", "SRC-CALENDAR", "SRC-POLICY", "SRC-TRANSCRIPT"]
    context = {"register_rows": register_rows, "incident_rows": incident_rows,
               "calendar_rows": calendar_rows, "conflicts": conflicts,
               "incident_evidence": incident_evidence}
    return state, consumed, produced, context


def build_stage_05(limbs: list[dict], context: dict, binding_available: bool) -> tuple[dict, list[str], list[str]]:
    impacts, unaffected, pair_conflicts = [], [], []
    consumed: list[str] = []
    for row in context["register_rows"]:
        system = row["system_id"]
        for limb in limbs:
            verdict = classify(limb, row, binding_available)
            limb_id = limb["limb"]
            evidence = [f"FACT-{system}-output_type", f"FACT-{system}-exposed_group",
                        f"RULE-{limb_id}"]
            if verdict["state"] in {"conflicting", "supported-no-impact", "supported-impact"} or \
                    verdict["layer"] == 5:
                evidence.append(f"FACT-{system}-evidence_status")
            if verdict["state"] == "conflicting":
                evidence.extend([r["id"] for r in context["incident_evidence"]
                                 if r.get("system_id") == system
                                 and r.get("evidence_state") == "conflicting"])
            if verdict["state"] in {"supported-no-impact", "supported-impact"}:
                evidence.append(f"FACT-{system}-current_notice")
            consumed.extend(evidence)
            blocker = limb["authority_blocker"]
            if limb["binding_party"] == "provider":
                blocker += " The provider role is undetermined for every system."
            record = rec(
                f"IMP-{system}-{limb_id}",
                f"{system} {row.get('system_name', '')} against Article {limb_id}.",
                evidence,
                system_id=system, system_name=row.get("system_name", ""),
                obligation_limb=limb_id, binding_party=limb["binding_party"],
                applicability=verdict["applicability"], reason=verdict["reason"],
                authority_blocker=blocker, owner=row.get("owner", ""),
                precedence_layer=verdict["layer"],
                required_next_evidence=limb["required_next_evidence"] if verdict["layer"] == 2 else (
                    "A formal provider or deployer role determination from Legal and the system "
                    "owners." if verdict["layer"] == 4 else (
                        "Complete and uncontested evidence of the disclosure practice for this "
                        "system." if verdict["layer"] in (3, 5) else None)),
            )
            if verdict["array"] == "impacts":
                record["state"] = verdict["state"]
                impacts.append(record)
                if verdict["state"] == "conflicting":
                    pair_conflicts.append(rec(
                        f"CFL-{system}-{limb_id}",
                        f"{system} against Article {limb_id} is recorded as conflicting because the "
                        f"register records evidence_status conflicting. Not adjudicated.",
                        evidence, owner=row.get("owner", "")))
            else:
                unaffected.append(record)

    unresolved_items = [
        rec("UNR-provider-role",
            "The provider or deployer role is undetermined for all eight systems, which withholds "
            "every Article 50(1) and 50(2) conclusion.",
            ["BLK-provider-role", "E20", "E26"],
            owner="Legal and the system owners",
            required_next_evidence="Written evidence from the vendor contract or system deployment "
                                   "records confirming who built and placed each system into "
                                   "service, followed by a formal sign-off from Legal."),
        rec("UNR-policy-controls",
            "The internal AI-use policy could not be read, so the controls the school measures "
            "itself against are unknown.",
            ["GAP-ALL-policy-controls", "SRC-POLICY"],
            owner="Leadership",
            required_next_evidence="The policy text or the relevant excerpts, supplied by the "
                                   "document owner."),
        rec("UNR-placed-on-market",
            "No source records placed on market or deployment dates, so the Article 50(2) "
            "transitional deadline of 02 Dec 2026 cannot be applied to any system.",
            ["GAP-ALL-placed-on-market"],
            owner="The system owners",
            required_next_evidence="Placed on market or deployment dates per system."),
    ]
    consumed.extend(["BLK-provider-role", "GAP-ALL-policy-controls", "GAP-ALL-placed-on-market"])
    state = {
        "impacts": impacts,
        "unaffected_items": unaffected,
        "conflicts": pair_conflicts,
        "unresolved_items": unresolved_items,
    }
    produced = [r["id"] for group in state.values() for r in group]
    return state, dedupe(consumed), produced


def build_stage_06(stage05: dict, context: dict, as_of_date: str) -> tuple[dict, list[str], list[str], dict]:
    calendar_rows = context["calendar_rows"]
    system_ids = {row["system_id"] for row in context["register_rows"]}
    by_system: dict[str, list[str]] = {}
    register_wide: list[str] = []
    for row in calendar_rows:
        target = row.get("system_id", "")
        if target in system_ids:
            by_system.setdefault(target, []).append(row["action_id"])
        else:
            register_wide.append(row["action_id"])

    actions: list[dict] = []
    consumed: list[str] = []
    action_for_record: dict[str, str] = {}

    provider_records = [i for i in stage05["impacts"] if i["binding_party"] == "provider"]
    if provider_records:
        action_id = "PA-ROLE-ALL"
        actions.append(rec(
            action_id,
            "Obtain a formal provider or deployer role determination for all eight systems from "
            "Legal and the system owners.",
            ["UNR-provider-role"] + [r["id"] for r in provider_records],
            system_id="ALL", approval_gate="legal", owner="Legal and the system owners",
            existing_calendar_action="",
            note="One determination settles every provider limb record, so this run proposes one "
                 "action rather than one per record.",
            proposed_date=as_of_date, date_agreed=False))
        consumed.extend(["UNR-provider-role"] + [r["id"] for r in provider_records])
        for record in provider_records:
            action_for_record[record["id"]] = action_id

    for record in stage05["impacts"]:
        layer, system, limb = record["precedence_layer"], record["system_id"], record["obligation_limb"]
        if layer == 4:
            # Settled by the single role determination above, not by an action of its own.
            continue
        if layer == 2:
            action_id = f"PA-{system}-applicability-{limb}"
            summary = (f"Obtain the evidence that settles whether Article {limb} applies to "
                       f"{system}: {record['required_next_evidence']}")
            gate = "legal"
        elif layer == 3:
            action_id = f"PA-{system}-reconcile-{limb}"
            summary = (f"Reconcile the conflicting disclosure evidence for {system} and record one "
                       f"agreed position.")
            gate = "operations"
        elif layer == 5:
            action_id = f"PA-{system}-evidence-{limb}"
            summary = (f"Refresh the disclosure evidence for {system} until it is complete and "
                       f"uncontested.")
            gate = "operations"
        elif record.get("state") == "supported-impact":
            action_id = f"PA-{system}-remediate-{limb}"
            summary = f"Add and verify the Article {limb} disclosure for {system}."
            gate = "operations"
        else:
            continue
        actions.append(rec(action_id, summary, [record["id"]],
                           system_id=system, approval_gate=gate, owner=record["owner"],
                           existing_calendar_action=", ".join(by_system.get(system, [])),
                           proposed_date=as_of_date, date_agreed=False))
        consumed.append(record["id"])
        action_for_record[record["id"]] = action_id

    for item, action_id, summary, gate, owner in [
        ("UNR-policy-controls", "PA-ALL-policy-access",
         "Request access to the internal AI-use policy from leadership, or the relevant excerpts.",
         "operations", "Leadership"),
        ("UNR-placed-on-market", "PA-ALL-placed-on-market",
         "Record placed on market or deployment dates for each system so the Article 50(2) "
         "transitional deadline can be assessed.", "operations", "The system owners"),
    ]:
        actions.append(rec(action_id, summary, [item], system_id="ALL", approval_gate=gate,
                           owner=owner, existing_calendar_action="",
                           proposed_date=as_of_date, date_agreed=False))
        consumed.append(item)
        action_for_record[item] = action_id
    action_for_record["UNR-provider-role"] = "PA-ROLE-ALL" if provider_records else ""

    approvals = [rec(f"APR-{a['id']}",
                     f"{a['approval_gate'].capitalize()} approval required for {a['id']}.",
                     [a["id"]], status="pending", approval_gate=a["approval_gate"])
                 for a in actions]

    escalations = []
    for row in calendar_rows:
        due = row.get("due_date", "")
        if due and due < as_of_date:
            escalations.append(rec(
                f"ESC-{row['action_id']}-overdue",
                f"Compliance calendar action {row['action_id']} for {row.get('system_id', '')} was "
                f"due {due}, before the as-of date {as_of_date}. Stated as a fact about their own "
                f"record, not as a finding of non-compliance.",
                ["SRC-CALENDAR"], owner=row.get("owner", ""), due_date=due))
    impacted_systems = {r["system_id"] for r in stage05["impacts"]}
    for system in sorted(impacted_systems):
        if not by_system.get(system):
            escalations.append(rec(
                f"ESC-{system}-no-calendar-action",
                f"{system} carries an open Article 50 question in this review and no compliance "
                f"calendar action of its own.",
                ["SRC-CALENDAR"] + [r["id"] for r in stage05["impacts"] if r["system_id"] == system],
                owner="Operations"))
    if register_wide:
        escalations.append(rec(
            "ESC-register-wide-actions",
            f"Compliance calendar rows {', '.join(register_wide)} carry a system_id outside the "
            f"eight system ids and are treated as register wide actions, not expanded per system.",
            ["SRC-CALENDAR"], owner="Operations"))

    consumed.append("SRC-CALENDAR")
    state = {"proposed_actions": actions, "approval_requirements": approvals,
             "escalations": escalations}
    produced = [r["id"] for group in state.values() for r in group]
    return state, dedupe(consumed), produced, action_for_record


# --------------------------------------------------------------------------- artifacts


def readable(record_id: str, index: dict[str, dict], as_of_date: str) -> str:
    if re.fullmatch(r"E\d+", record_id):
        return f"stakeholder interview 2026-09-04, exchange {record_id}"
    record = index.get(record_id)
    if record_id.startswith("SRC-") and record:
        return f"{record['summary']} ({record['retrieval_status']}, read {as_of_date})"
    if record_id.startswith("FACT-") and record:
        return f"AI-system register, {record['system_id']} {record['field']}"
    if record_id.startswith("RULE-"):
        return f"Article {record_id[5:]} binding text"
    if record_id.startswith("INC-"):
        return f"incident and evidence register, {record_id[4:]}"
    if record:
        return norm(record["summary"])[:160]
    return record_id


CSV_COLUMNS = ["record_id", "system_id", "system_name", "obligation_limb", "binding_party",
               "applicability", "state", "reason", "evidence_references", "evidence_ids",
               "authority_blocker", "responsible_owner", "required_next_evidence",
               "proposed_action_id", "existing_calendar_action", "approval_gate", "approval_state"]


def write_register(stage05: dict, stage06: dict, context: dict, index: dict, as_of_date: str,
                   action_for_record: dict) -> bytes:
    system_ids = {row["system_id"] for row in context["register_rows"]}
    by_system: dict[str, list[str]] = {}
    for row in context["calendar_rows"]:
        if row.get("system_id") in system_ids:
            by_system.setdefault(row["system_id"], []).append(row["action_id"])
    gate_for_action = {a["id"]: a["approval_gate"] for a in stage06["proposed_actions"]}

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for record in stage05["impacts"]:
        action = action_for_record.get(record["id"], "")
        writer.writerow({
            "record_id": record["id"], "system_id": record["system_id"],
            "system_name": record["system_name"], "obligation_limb": record["obligation_limb"],
            "binding_party": record["binding_party"], "applicability": record["applicability"],
            "state": record["state"], "reason": record["reason"],
            "evidence_references": "; ".join(readable(e, index, as_of_date)
                                             for e in record["evidence_ids"]),
            "evidence_ids": " ".join(record["evidence_ids"]),
            "authority_blocker": record["authority_blocker"],
            "responsible_owner": record["owner"],
            "required_next_evidence": record["required_next_evidence"] or "",
            "proposed_action_id": action,
            "existing_calendar_action": ", ".join(by_system.get(record["system_id"], [])),
            "approval_gate": gate_for_action.get(action, ""),
            "approval_state": "pending" if action else "not-required",
        })
    for record in stage05["unresolved_items"]:
        action = action_for_record.get(record["id"], "")
        writer.writerow({
            "record_id": record["id"], "system_id": "ALL", "system_name": "",
            "obligation_limb": "", "binding_party": "", "applicability": "",
            "state": "unresolved", "reason": record["summary"],
            "evidence_references": "; ".join(readable(e, index, as_of_date)
                                             for e in record["evidence_ids"]),
            "evidence_ids": " ".join(record["evidence_ids"]),
            "authority_blocker": "Pending Legal.", "responsible_owner": record["owner"],
            "required_next_evidence": record["required_next_evidence"],
            "proposed_action_id": action, "existing_calendar_action": "",
            "approval_gate": gate_for_action.get(action, ""),
            "approval_state": "pending" if action else "not-required",
        })
    payload = buffer.getvalue().encode("utf-8")
    (DELIVERABLES / "impact-register.csv").write_bytes(payload)
    return payload


def write_brief(run_id: str, as_of: str, as_of_date: str, publication_status: str,
                sources: list[dict], stage03: dict, stage04: dict, stage05: dict, stage06: dict,
                index: dict) -> bytes:
    lines: list[str] = []
    add = lines.append
    add("# Compliance brief: EU AI Act Article 50 transparency obligations")
    add("")
    add(f"- Run: `{run_id}`")
    add(f"- As at: {as_of}")
    add(f"- Review type: {REVIEW_TYPE}")
    add(f"- Publication status: {publication_status}")
    add("- Produced by: `uv run regulatory-change-impact-brief/scripts/run_review.py`")
    add("")
    add("This is a draft prepared for human review. Legal holds every interpretation of the "
        "obligations. Operations holds activation, dates and closure. Nothing here is a legal "
        "opinion or an approved action.")
    add("")

    add("## Scope")
    add("")
    add(f"{SCOPE_RULE.capitalize()}, reviewed against the five obligation limbs of Article 50. "
        f"Audiences: {', '.join(AUDIENCES)}. Approval gates, in order: "
        f"{'; '.join(APPROVAL_GATES)}.")
    add("")
    systems = sorted({r["system_id"] for r in stage05["impacts"] + stage05["unaffected_items"]})
    total = len(stage05["impacts"]) + len(stage05["unaffected_items"])
    add(f"{len(systems)} systems by 5 obligation limbs is {total} system and limb pairs. "
        f"{len(stage05['unaffected_items'])} pairs are not reached by the obligation and "
        f"{len(stage05['impacts'])} entered the analysis.")
    add("")
    add("Pairs the obligations do not reach:")
    add("")
    for record in stage05["unaffected_items"]:
        add(f"- {record['system_id']} {record['system_name']}, Article "
            f"{record['obligation_limb']}: {record['reason']}")
    add("")

    add("## Source status")
    add("")
    add("| Source | Authority | Status | Read |")
    add("|---|---|---|---|")
    for source in sources:
        add(f"| {source['summary']} | {source['authority']} | {source['retrieval_status']} | "
            f"{as_of_date} |")
    add("")
    unavailable = [s for s in sources if s["retrieval_status"] != "retrieved"]
    if unavailable:
        for source in unavailable:
            add(f"{source['summary']} is {source['retrieval_status']}. This withholds "
                f"{source['withholds_on_failure']}. Its absence is not evidence of compliance.")
        add("")

    for title, states in [("Supported impacts", {"supported-impact", "supported-no-impact"}),
                          ("Unresolved items", {"unresolved", "conflicting"})]:
        add(f"## {title}")
        add("")
        selected = [r for r in stage05["impacts"] if r.get("state") in states]
        if title == "Unresolved items":
            selected = selected + stage05["unresolved_items"]
        if not selected:
            add("No records reached this section on this run. Every applicable obligation limb is "
                "held open by the provider role determination or by missing applicability "
                "evidence, both listed under Unresolved items. No record has been invented to "
                "demonstrate a state.")
            add("")
            continue
        for record in selected:
            label = record.get("state", "unresolved")
            head = (f"{record['system_id']} {record.get('system_name', '')}, Article "
                    f"{record['obligation_limb']}" if record.get("obligation_limb")
                    else record["summary"])
            add(f"### {record['id']}, {label}")
            add("")
            add(head if record.get("obligation_limb") else "")
            add("")
            add(record.get("reason", record["summary"]))
            add("")
            if record.get("required_next_evidence"):
                add(f"Required next evidence: {record['required_next_evidence']}")
                add("")
            add(f"Owner: {record.get('owner', 'not recorded')}. Evidence: "
                f"{'; '.join(readable(e, index, as_of_date) for e in record['evidence_ids'])}.")
            add("")

    add("## Actions")
    add("")
    add("Every action below is a draft proposal. None is scheduled, approved or activated.")
    add("")
    add("| Action | Scope | Proposal | Owner | Approval gate | Approval state | Existing action |")
    add("|---|---|---|---|---|---|---|")
    for action in stage06["proposed_actions"]:
        add(f"| {action['id']} | {action['system_id']} | {action['summary']} | {action['owner']} | "
            f"{action['approval_gate']} | pending | {action['existing_calendar_action'] or 'none'} |")
    add("")
    if stage06["escalations"]:
        add("Escalations raised by this run:")
        add("")
        for item in stage06["escalations"]:
            add(f"- {item['summary']}")
        add("")

    add("## Limitations")
    add("")
    for gap in stage04["evidence_gaps"]:
        add(f"- {gap['summary']}")
    for conflict in stage04["conflicts"]:
        add(f"- {conflict['summary']}")
    add("- Every determination of which obligation limb reaches which system, including every "
        "determination that a limb does not apply, is ours and is marked pending Legal.")
    add("- The Commission FAQ is advisory and is never the sole basis for any conclusion here.")
    add("")

    add("## Pending Legal and Operations decisions")
    add("")
    add("Legal:")
    add("")
    for action in stage06["proposed_actions"]:
        if action["approval_gate"] == "legal":
            add(f"- {action['id']}: {action['summary']}")
    add("")
    add("Operations:")
    add("")
    for action in stage06["proposed_actions"]:
        if action["approval_gate"] == "operations":
            add(f"- {action['id']}: {action['summary']}")
    add("")
    add("This workflow does not give final legal advice, activate a policy, change an approved "
        "deadline, close an incident, submit an official response, or write to a production "
        "calendar.")
    add("")

    payload = ("\n".join(lines).rstrip("\n") + "\n").encode("utf-8")
    (DELIVERABLES / "compliance-brief.md").write_bytes(payload)
    return payload


def ics_escape(text: str) -> str:
    return (text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\n", "\\n"))


def ics_fold(line: str) -> list[str]:
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return [line]
    out, chunk = [], b""
    for character in line:
        encoded = character.encode("utf-8")
        limit = 75 if not out else 74
        if len(chunk) + len(encoded) > limit:
            out.append(chunk.decode("utf-8"))
            chunk = b""
        chunk += encoded
    if chunk:
        out.append(chunk.decode("utf-8"))
    return [out[0]] + [" " + part for part in out[1:]]


def write_calendar(run_id: str, as_of: str, as_of_date: str, stage06: dict) -> bytes:
    stamp = as_of.replace("-", "").replace(":", "")
    date_value = as_of_date.replace("-", "")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             f"PRODID:-//regulatory-change-impact-brief//{run_id}//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    for action in stage06["proposed_actions"]:
        description = (
            f"Draft proposal from run {run_id}. Related records: "
            f"{', '.join(action['evidence_ids'])}. Owner: {action['owner']}. "
            f"Approval gate: {action['approval_gate']}, approval state pending. "
            f"Existing compliance calendar action: "
            f"{action['existing_calendar_action'] or 'none'}. "
            f"No date has been agreed; this event carries the review as-of date so the proposal is "
            f"visible. This is an unapproved draft and is not an entry in the production calendar.")
        summary_text = f"[DRAFT, pending {action['approval_gate']}] {action['summary']}"
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{action['id']}@{run_id}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{date_value}",
            f"SUMMARY:{ics_escape(summary_text)}",
            f"DESCRIPTION:{ics_escape(description)}",
            "STATUS:TENTATIVE",
            f"CATEGORIES:{ics_escape('Article 50 draft action')}",
            f"CONTACT:{ics_escape(action['owner'])}",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    folded: list[str] = []
    for line in lines:
        folded.extend(ics_fold(line))
    payload = ("\r\n".join(folded) + "\r\n").encode("utf-8")
    (DELIVERABLES / "action-calendar.ics").write_bytes(payload)
    return payload


# --------------------------------------------------------------------------- validation


def check(check_id: str, summary: str, passed: bool, detail: str = "") -> dict:
    return rec(check_id, summary, [], passed=passed, detail=detail)


def run_checks(schema: dict, trail: Trail, produced_ids: set[str], exchanges: set[str],
               stage05: dict, stage06: dict, limbs: list[dict], context: dict,
               register_bytes: bytes, brief_bytes: bytes, ics_bytes: bytes,
               as_of: str, as_of_date: str) -> list[dict]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    checks: list[dict] = []

    invalid = [f"{s['snapshot_id']}: {e.message}"
               for s in trail.written for e in validator.iter_errors(s)]
    checks.append(check("CHK-01",
                        "Snapshots 01 to 06 validate against snapshot.schema.json during the run. "
                        "Snapshot 07 is validated immediately after it is written and a failure "
                        "there exits 1.",
                        not invalid, "; ".join(invalid[:3])))

    lineage_bad = []
    for snapshot in trail.written[1:]:
        path = REPO_ROOT / snapshot["predecessor"]["path"]
        actual = sha256_of(path.read_bytes()) if path.exists() else "missing"
        if actual != snapshot["predecessor"]["sha256"]:
            lineage_bad.append(snapshot["snapshot_id"])
    checks.append(check("CHK-02", "Every predecessor sha256 from stage 02 onward matches the file "
                        "on disk.", not lineage_bad, ", ".join(lineage_bad)))

    run_ids = {s["run_id"] for s in trail.written}
    checks.append(check("CHK-03", "All snapshots carry the same run_id.", len(run_ids) == 1,
                        ", ".join(sorted(run_ids))))

    sequences = sorted(s["sequence"] for s in trail.written)
    checks.append(check("CHK-04", "Sequences 1 to 6 each appear exactly once during the run, and 7 "
                        "is written last.", sequences == [1, 2, 3, 4, 5, 6], str(sequences)))

    pairs = [(r["system_id"], r["obligation_limb"])
             for r in stage05["impacts"] + stage05["unaffected_items"]]
    expected = len({row["system_id"] for row in context["register_rows"]}) * len(limbs)
    checks.append(check("CHK-05",
                        f"impacts plus unaffected_items total {expected}, and each system and limb "
                        f"pair appears exactly once.",
                        len(pairs) == expected and len(set(pairs)) == expected,
                        f"{len(pairs)} pairs, {len(set(pairs))} distinct"))

    dangling = []
    for snapshot in trail.written:
        for group in snapshot["state"].values():
            if not isinstance(group, list):
                continue
            for record in group:
                if not isinstance(record, dict):
                    continue
                for evidence in record.get("evidence_ids", []):
                    if evidence not in produced_ids and evidence not in exchanges:
                        dangling.append(f"{record['id']} -> {evidence}")
    checks.append(check("CHK-06", "Every evidence_ids value resolves to a record produced upstream "
                        "or to a real exchange id.", not dangling, "; ".join(sorted(set(dangling))[:5])))

    cited = [r["id"] for r in stage05["impacts"] + stage05["unaffected_items"]
             if any(re.fullmatch(r"E\d+", e) for e in r["evidence_ids"])]
    checks.append(check("CHK-07", "No entry in impacts or unaffected_items cites an exchange as the "
                        "basis for a limb determination.", not cited, ", ".join(cited[:5])))

    faq_only = [r["id"] for r in stage05["impacts"]
                if "SRC-FAQ" in r["evidence_ids"] and len(r["evidence_ids"]) == 1]
    checks.append(check("CHK-08", "No impact record rests on the Commission FAQ as its only "
                        "evidence.", not faq_only, ", ".join(faq_only)))

    missing_blocker = [r["id"] for r in stage05["impacts"]
                       if r["binding_party"] == "provider"
                       and "provider role is undetermined" not in r["authority_blocker"]]
    checks.append(check("CHK-09", "Every provider limb record carries the provider role authority "
                        "blocker.", not missing_blocker, ", ".join(missing_blocker)))

    incomplete = [r["id"] for r in stage05["unresolved_items"]
                  if not r.get("owner") or not r.get("required_next_evidence")]
    incomplete += [r["id"] for r in stage05["impacts"]
                   if r.get("state") in {"unresolved", "conflicting"}
                   and (not r.get("owner") or not r.get("required_next_evidence"))]
    checks.append(check("CHK-10", "Every unresolved or conflicting item carries an owner and the "
                        "evidence that would close it.", not incomplete, ", ".join(incomplete[:5])))

    rows = list(csv.DictReader(io.StringIO(register_bytes.decode("utf-8"))))
    expected_rows = len(stage05["impacts"]) + len(stage05["unresolved_items"])
    known = {r["id"] for r in stage05["impacts"] + stage05["unresolved_items"]}
    unknown_rows = [r["record_id"] for r in rows if r["record_id"] not in known]
    checks.append(check("CHK-11", "The register row count equals impacts plus unresolved_items, and "
                        "every row record_id exists in stage 05 or 06.",
                        len(rows) == expected_rows and not unknown_rows,
                        f"{len(rows)} rows, expected {expected_rows}; unknown {unknown_rows[:3]}"))

    on_disk = {
        "impact-register.csv": sha256_of(register_bytes),
        "compliance-brief.md": sha256_of(brief_bytes),
        "action-calendar.ics": sha256_of(ics_bytes),
    }
    mismatch = [name for name, digest in on_disk.items()
                if not (DELIVERABLES / name).exists()
                or sha256_of((DELIVERABLES / name).read_bytes()) != digest]
    checks.append(check("CHK-12", "Every artifact sha256 recorded in stage 07 matches the file on "
                        "disk.", not mismatch, ", ".join(mismatch)))

    uids = re.findall(r"(?m)^UID:(\S+)@", ics_bytes.decode("utf-8"))
    action_ids = [a["id"] for a in stage06["proposed_actions"]]
    checks.append(check("CHK-13", "Every proposed action in stage 06 appears as exactly one VEVENT.",
                        sorted(uids) == sorted(action_ids),
                        f"{len(uids)} events, {len(action_ids)} actions"))

    stamps = set()
    for blob in (register_bytes, brief_bytes, ics_bytes):
        stamps.update(re.findall(r"\d{4}-\d{2}-\d{2}T[\d:]+Z", blob.decode("utf-8")))
    ics_stamps = set(re.findall(r"(?m)^DTSTAMP:(\S+)", ics_bytes.decode("utf-8")))
    compact = as_of.replace("-", "").replace(":", "")
    checks.append(check("CHK-14", "Every run timestamp displayed in the three artifacts equals "
                        "as_of. Dates that come from the sources are data and are not run "
                        "timestamps.",
                        stamps <= {as_of} and ics_stamps <= {compact},
                        f"{sorted(stamps)} {sorted(ics_stamps)}"))
    return checks


# --------------------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", dest="as_of", default=None,
                        help="RFC 3339 timestamp the review anchors to. Defaults to now, UTC.")
    args = parser.parse_args()

    as_of = args.as_of or utc_now()
    try:
        parsed = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    except ValueError:
        print(f"--as-of is not an RFC 3339 timestamp: {as_of}", file=sys.stderr)
        return 1
    as_of = parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    as_of_date = as_of[:10]
    run_id = "RUN-" + as_of.replace("-", "").replace(":", "")

    schema = json.loads((REPO_ROOT / "snapshot.schema.json").read_text(encoding="utf-8"))
    sources = json.loads((SCRIPT_DIR / "sources.json").read_text(encoding="utf-8"))["sources"]
    limbs = json.loads((SCRIPT_DIR / "article-50-limbs.json").read_text(encoding="utf-8"))["limbs"]
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)

    trail = Trail(run_id)
    force_invalid: set[str] = set()

    for attempt in range(MAX_RUN_ATTEMPTS):
        rewind_available = attempt + 1 < MAX_RUN_ATTEMPTS
        trail.reset()
        produced_ids: set[str] = set()

        state01 = {"as_of": as_of, "review_type": REVIEW_TYPE,
                   "systems_in_scope": [SCOPE_RULE], "audiences": AUDIENCES,
                   "approval_gates": APPROVAL_GATES}
        trail.write(1, "scope", "01-scope.json", "complete", state01, [], [SCOPE_RECORD_ID],
                    [decision("DEC-scope-rule",
                              "Stage 01 declares the scope as a rule and does not enumerate the "
                              "systems.", [],
                              "The systems live in the AI-system register, which is fetched in "
                              "stage 02. Enumerating them here would mean carrying a copied list "
                              "that says nothing about the register as it is today.",
                              ["A reviewer does not see the eight system ids until stage 04.",
                               "The scope rule is stable while the register changes."])], [])
        produced_ids.add(SCOPE_RECORD_ID)

        source_records, payloads = capture_sources(sources, as_of, force_invalid)
        produced_ids.update(r["id"] for r in source_records)
        binding_available = payloads["ART50"]["status"] == "retrieved"
        not_retrieved = [r for r in source_records if r["retrieval_status"] != "retrieved"]
        decisions02 = [decision(
            "DEC-version-metadata",
            "version_metadata for the two Commission pages is retrieved_at plus content_hash.",
            ["SRC-ART50", "SRC-TIMELINE"],
            "Neither page carries a version identifier, so identity has to be recorded some other "
            "way. This is our decision; the scenario states the stakeholder does not design the "
            "automation.",
            ["Identity is only as good as the retrieval time and the hash.",
             "A cosmetic markup change moves content_hash, which is why a normalised text hash is "
             "recorded beside it."])]
        if force_invalid:
            decisions02.append(decision(
                "DEC-rewind",
                f"Stage 03 rechecked {', '.join(sorted(force_invalid))} and disagreed with stage "
                f"02, so stage 02 was rewritten and every downstream stage rerun.",
                ["SRC-ART50"],
                "A validation failure returns to the earliest affected stage so the lineage stays "
                "intact rather than carrying a record known to be wrong.",
                ["The trail on disk is the corrected one, and the rewind itself is recorded here.",
                 "One rewind per run is allowed; a second of the same kind is a failed run."]))
        status02 = "complete" if not not_retrieved else ("blocked" if not binding_available else "partial")
        trail.write(2, "source-capture", "02-source-capture.json", status02,
                    {"sources": source_records}, [SCOPE_RECORD_ID],
                    [r["id"] for r in source_records], decisions02,
                    [rec(f"UNRES-{r['id']}", f"{r['summary']} is {r['retrieval_status']}. This "
                         f"withholds {r['withholds_on_failure']}.", [r["id"]])
                     for r in not_retrieved])

        state03, decisions03, consumed03, produced03 = build_stage_03(payloads, limbs, as_of_date)
        paragraphs = payloads["ART50"]["payload"].get("paragraphs", {})
        recheck_failed = binding_available and not all(
            len(paragraphs.get(n, "")) > 200 for n in (1, 2, 3, 4))
        if recheck_failed and rewind_available:
            force_invalid = {"ART50"}
            continue
        produced_ids.update(produced03)
        trail.write(3, "authority-and-timing", "03-authority-and-timing.json",
                    "complete" if binding_available else "blocked", state03, consumed03, produced03,
                    decisions03, [r for r in state03["authority_blockers"]])

        state04, consumed04, produced04, context = build_stage_04(payloads, as_of_date)
        produced_ids.update(produced04)
        trail.write(4, "evidence-reconciliation", "04-evidence-reconciliation.json", "partial",
                    state04, consumed04, produced04,
                    [decision("DEC-conflict-policy",
                              "Source conflicts are recorded and never adjudicated. The register's "
                              "evidence_status sets a conflicting impact state; an incident "
                              "record's evidence_state does not.",
                              ["SRC-REGISTER", "SRC-INCIDENT", "E24"],
                              "Where two sources agree that evidence is in conflict, saying so "
                              "adjudicates nothing. Where they disagree with each other, letting "
                              "one override the other would be choosing a winner, so the "
                              "disagreement itself is the record.",
                              ["A conflicting incident on a system whose register entry reads "
                               "complete does not change that system's impact state.",
                               "The disagreement is visible in stage 04 instead."])],
                    state04["evidence_gaps"])

        state05, consumed05, produced05 = build_stage_05(limbs, context, binding_available)
        produced_ids.update(produced05)
        open_pairs = [r for r in state05["impacts"]
                      if r.get("state") in {"unresolved", "conflicting"}]
        trail.write(5, "impact-analysis", "05-impact-analysis.json",
                    "blocked" if not binding_available else ("partial" if open_pairs else "complete"),
                    state05, consumed05, produced05,
                    [decision("DEC-provider-role-withheld",
                              "Provider limb conclusions are withheld for all eight systems.",
                              ["BLK-provider-role", "E20", "E26"],
                              "The register's provider_role column is maintained by system owners "
                              "and the mechanism that puts it in doubt, described at E20, reaches "
                              "the whole column rather than particular rows. A value of no in an "
                              "operational record is not a legal role determination.",
                              ["Seven pairs that might otherwise read supported-no-impact stay "
                               "unresolved.",
                               "One determination by Legal settles all of them at once."]),
                     decision("DEC-state-precedence",
                              "A recorded conflict is assigned before the provider limb "
                              "withholding.",
                              ["CFL-ALL-deployment-dates"],
                              "Reporting a corroborated evidence conflict as merely unresolved "
                              "would leave the most concrete evidence problem visible only in "
                              "stage 04, where neither Legal nor Operations reads.",
                              ["A conflicting record still carries the role blocker, so nothing "
                               "about the role question is lost."])],
                    state05["unresolved_items"])

        state06, consumed06, produced06, action_for_record = build_stage_06(state05, context, as_of_date)
        produced_ids.update(produced06)
        trail.write(6, "actions-and-approvals", "06-actions-and-approvals.json", "partial",
                    state06, consumed06, produced06,
                    [decision("DEC-action-no-suppression",
                              "An existing compliance calendar action is cross referenced and never "
                              "suppresses a proposed action.",
                              ["SRC-CALENDAR"],
                              "Judging their existing action sufficient would be an Operations "
                              "decision. Cross referencing shows the overlap and leaves the call "
                              "with them.",
                              ["Some proposed actions will look like duplicates of calendar rows.",
                               "The register row names the existing action so the overlap is "
                               "visible."])],
                    state06["approval_requirements"])

        index = {r["id"]: r for r in source_records}
        for group in (state03, state04, state05, state06):
            for records in group.values():
                if isinstance(records, list):
                    index.update({r["id"]: r for r in records})

        register_bytes = write_register(state05, state06, context, index, as_of_date,
                                        action_for_record)
        ics_bytes = write_calendar(run_id, as_of, as_of_date, state06)
        exchanges = payloads["TRANSCRIPT"]["payload"].get("exchanges", set())
        checks = run_checks(schema, trail, produced_ids, exchanges, state05, state06, limbs,
                            context, register_bytes, b"", ics_bytes, as_of, as_of_date)
        provisional_failed = [c["id"] for c in checks if not c["passed"] and c["id"] != "CHK-12"]
        publication_status = ("blocked" if not binding_available
                              else ("failed" if provisional_failed else "validated"))
        brief_bytes = write_brief(run_id, as_of, as_of_date, publication_status, source_records,
                                  state03, state04, state05, state06, index)
        checks = run_checks(schema, trail, produced_ids, exchanges, state05, state06, limbs,
                            context, register_bytes, brief_bytes, ics_bytes, as_of, as_of_date)
        failed = [c["id"] for c in checks if not c["passed"]]
        publication_status = ("blocked" if not binding_available
                              else ("failed" if failed else "validated"))

        artifacts = [
            {"id": "ART-REGISTER", "path": "deliverables/impact-register.csv",
             "sha256": sha256_of(register_bytes), "validation_status": "valid"},
            {"id": "ART-BRIEF", "path": "deliverables/compliance-brief.md",
             "sha256": sha256_of(brief_bytes), "validation_status": "valid"},
            {"id": "ART-CALENDAR", "path": "deliverables/action-calendar.ics",
             "sha256": sha256_of(ics_bytes), "validation_status": "valid"},
        ]
        state07 = {"artifacts": artifacts, "validation_checks": checks,
                   "publication_status": publication_status}
        trail.write(7, "publication-validation", "07-publication-validation.json",
                    "complete" if publication_status == "validated" else
                    ("blocked" if publication_status == "blocked" else "failed"),
                    state07,
                    [r["id"] for r in state05["impacts"]] + [a["id"] for a in state06["proposed_actions"]],
                    [a["id"] for a in artifacts] + [c["id"] for c in checks],
                    [decision("DEC-validation-basis",
                              "The validation checks rest on the repository README and on our own "
                              "judgement, not on stakeholder testimony.", [],
                              "Nobody at the client specified how the audit trail should be "
                              "checked, so presenting these as theirs would misattribute them.",
                              ["The checks are ours to defend."])],
                    [c for c in checks if not c["passed"]])
        break

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    final_errors = []
    for _, stage, filename in STAGES:
        snapshot = json.loads((SNAPSHOTS / filename).read_text(encoding="utf-8"))
        final_errors += [f"{filename}: {e.message}" for e in validator.iter_errors(snapshot)]

    print(f"run_id            : {run_id}")
    print(f"as_of             : {as_of}")
    print(f"publication_status: {publication_status}")
    print(f"checks            : {sum(1 for c in checks if c['passed'])}/{len(checks)} passed")
    if failed:
        print(f"failed checks     : {', '.join(failed)}")
    for source in source_records:
        if source["retrieval_status"] != "retrieved":
            print(f"source            : {source['id']} is {source['retrieval_status']}")
    if final_errors:
        print("schema errors     : " + "; ".join(final_errors[:5]), file=sys.stderr)
        return 1
    return 0 if publication_status == "validated" else 1


if __name__ == "__main__":
    sys.exit(main())

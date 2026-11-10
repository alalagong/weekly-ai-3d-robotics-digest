"""Validate a SLAM weekly report and its ledger, presentation, and discovery manifest."""

import argparse
from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from lxml import html
from PIL import Image

INCLUDED = {"deep_read", "supplemental", "revision_tracking"}
DISPOSITIONS = INCLUDED | {"excluded", "unresolved"}
WINDOWS = {
    "new": lambda start, end, v1, updated, version: start < v1 <= updated <= end,
    "revised": lambda start, end, v1, updated, version: v1 <= start < updated <= end and version > 1,
    "historical_backfill": lambda start, end, v1, updated, version: v1 <= updated <= start and version == 1,
    "historical_revision_backfill": lambda start, end, v1, updated, version: v1 <= updated <= start and version > 1,
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse(path):
    return html.fromstring(path.read_text(encoding="utf-8-sig"))


def validate(ledger_path, browser_path):
    folder = ledger_path.parent
    root = folder.parent
    prefix = ledger_path.name.removesuffix("_paper-ledger.json")
    ledger = read(ledger_path)
    manifest = read(folder / f"{prefix}_search-manifest.json")
    presentation = read(folder / f"{prefix}_presentation.json")
    history = read(folder / "paper-history.json")["papers"]
    report_path = root / ledger["report_path"]
    report = parse(report_path)
    index = parse(folder / "index.html")
    papers = ledger["papers"]
    candidates = {r["id"] for r in papers}
    counts = Counter(r["disposition"] for r in papers)
    included = [r for r in papers if r["disposition"] in INCLUDED]
    tracking = [r for r in included if r["disposition"] != "deep_read"]
    tracked = {r["id"]: r for r in tracking}
    notes = {r["id"]: r for r in presentation["papers"]}
    anchors = report.xpath("//*[@id]/@id")
    start = stamp(ledger["coverage_start_exclusive"])
    end = stamp(ledger["coverage_end_inclusive"])
    expected_anchors = {r["report_anchor"] for r in included}
    tracked_anchors = {r["report_anchor"] for r in tracking}
    categories = Counter(r["category"] for r in notes.values())
    groups = report.xpath('//details[@class="tracking-group"]')
    browser = read(browser_path) if browser_path else {"status": "not-run"}
    checks = {}

    checks["nine_sections_and_header"] = len(report.xpath("//main/section")) == 9 and len(report.xpath('//header//div[@class="tile"]')) == 4
    checks["no_placeholders"] = not re.search(r"\{\{[A-Z0-9_]+\}\}", report_path.read_text(encoding="utf-8"))
    checks["candidate_closure"] = len(candidates) == len(papers) == ledger["stats"]["candidates"] and set(counts) <= DISPOSITIONS and dict(counts) == ledger["stats"]["dispositions"]
    checks["window_count_closure"] = dict(Counter(r["window_class"] for r in included)) == ledger["stats"]["included_windows"]
    checks["locked_versions_and_window"] = all(
        isinstance(r.get("version"), int) and r["history_verified"] and r["evidence_source"].endswith(f'v{r["version"]}')
        and WINDOWS[r["window_class"]](start, end, stamp(r["v1_utc"]), stamp(r["updated_utc"]), r["version"])
        for r in included
    )
    checks["decision_evidence"] = all(
        (r.get("owner") and (r.get("abstract_read") or r["evidence_level"] == "reused_abstract"))
        if r["disposition"] in INCLUDED else bool(r.get("reason")) for r in papers
    )
    checks["history_dedupe"] = all(
        not (r.get("prior_same_version") and r["prior_same_version"].get("report_path") != ledger["report_path"])
        and (history.get(r["id"], {}).get("versions", {}).get(f'v{r["version"]}', {}).get("report_path") in {None, ledger["report_path"]})
        for r in included
    )
    checks["unique_paper_anchors"] = len(anchors) == len(set(anchors)) and {a for a in anchors if a.startswith("paper-")} == expected_anchors
    checks["presentation_closure"] = set(notes) == set(tracked) and len(notes) == len(presentation["papers"]) and all(
        r["version"] == tracked[ident]["version"] and 40 <= len(r["takeaway"]) <= 100
        and (not r["priority"] or r["priority_reason"]) for ident, r in notes.items()
    )
    rendered = report.xpath('//details[@class="tracking-paper"]')
    checks["tracking_details_and_categories"] = (
        {r.get("id") for r in rendered} == tracked_anchors and len(rendered) == len(tracking)
        and all(len(r.xpath("./summary")) == 1 and len(r.xpath(".//dt")) >= 6 and r.get("hidden") is None and r.get("open") is None for r in rendered)
        and {g.get("data-category"):len(g.xpath('./details[@class="tracking-paper"]')) for g in groups} == dict(categories)
    )
    invalid_links = []
    images = set()
    external_documents = {}
    for url in report.xpath("//@href|//@src"):
        parts = urlsplit(url)
        if parts.scheme or parts.netloc:
            continue
        target = (folder / unquote(parts.path)).resolve() if parts.path else report_path.resolve()
        if not target.is_file():
            invalid_links.append(url)
        elif parts.fragment and target.suffix == ".html":
            target_anchors = anchors if target == report_path.resolve() else external_documents.get(target)
            if target_anchors is None:
                target_anchors = set(parse(target).xpath("//*[@id]/@id"))
                external_documents[target] = target_anchors
            if unquote(parts.fragment) not in target_anchors:
                invalid_links.append(url)
        if target.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            images.add(target)
    checks["local_links_and_index"] = not invalid_links and index.xpath('count(//article/a[@href=$url])', url="./"+report_path.name) == 1
    figures = [r["figure_evidence"] for r in included if r["disposition"] == "deep_read" and "figure_evidence" in r]
    checks["confirmed_images"] = len(images) == len(figures) and {sha256(p.read_bytes()).hexdigest() for p in images if p.is_file()} == {
        r["sha256"] for r in figures if r["caption_confirmed"] and r["visual_confirmed"]
    }
    for image in images:
        if image.is_file():
            with Image.open(image) as decoded:
                decoded.verify()
    primary = manifest["query_sources"]["primary"]
    independent = manifest["query_sources"]["independent_classifications"]
    checks["primary_pagination"] = bool(primary) and all(
        q["exhausted"] and q["total"] == q["fetched"] == sum(p["returned"] for p in q["pages"])
        for q in primary
    )
    review = manifest["independent_review"]
    seen_review = {r["id"] for r in papers if "independent-review" in r.get("query_hits", [])}
    checks["independent_closure"] = bool(independent) and all(r["status"] == "exhausted" and r["advertised_total"] == r["retrieved"] == sum(p["retrieved"] for p in r["pages"]) for r in independent) and (
        len(seen_review) == review["count"] and not (seen_review & set(ledger["stats"]["unresolved_ids"]))
        and review["status"] == "passed"
    )
    checks["unresolved_queue"] = set(ledger["stats"]["unresolved_ids"]) == {r["id"] for r in papers if r["disposition"] == "unresolved"}
    checks["coverage_ready"] = ledger["coverage_status"] == "complete_with_known_limits" and not ledger["stats"]["unresolved_ids"]
    result = dict(run_at=ledger["run_at"], validated_at=datetime.now().astimezone().isoformat(), checks=checks,
                  passed=all(checks.values()), failures=[k for k,v in checks.items() if not v],
                  invalid_local_links=invalid_links, stats=ledger["stats"], browser_checks=browser)
    out = folder / f"{prefix}_validation.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"passed":result["passed"],"failures":result["failures"],"invalid_links":invalid_links[:12],
                      "checks":len(checks),"browser":browser.get("status")}, ensure_ascii=False))
    return result["passed"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--browser-results", type=Path)
    args = parser.parse_args()
    raise SystemExit(0 if validate(args.ledger.resolve(), args.browser_results) else 1)

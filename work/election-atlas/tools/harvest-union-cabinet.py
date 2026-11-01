#!/usr/bin/env python3
"""Harvest the Union Council of Ministers "as sworn in" and "as it stands".

Writes data/cabinet/union/2014.json and adds the sworn-in roster to
data/cabinet/union/2024.json. Each file carries both tenses:

    "swornIn", "allocated":  oath and portfolio-allocation dates
    "members":      [members] as sworn in
    "asOf":         the date the as-it-stands roster describes
    "as_it_stands": [members] as it stands on asOf

Sources (President's Secretariat and the Prime Minister's Office):
  - 2014 sworn in: "President Allocates Portfolios to Cabinet Ministers and
    Ministers of State", Rashtrapati Bhavan, 27.05.2014 (presidentofindia.gov.in).
  - 2014 as it stands (end of the 16th Lok Sabha): the full re-allocation of
    03.09.2017, then every later change. Releases from July 2017 on are on
    President Kovind's archive site, ramnathkovind.nic.in. Each change below is
    a structured transcription of one release and carries that release's own
    sentence verbatim; the harvester stops if the sentence is not in the fetched
    release, or if a change names a minister or portfolio the roster does not hold.
  - 2024 sworn in: the press communique of 10.06.2024 (presidentofindia.gov.in).
  - 2024 as it stands: the roster fetch-cabinet.py and join-sansad.py write to
    `members` of data/cabinet/union/2024.json (run them first), which is checked name-for-name and portfolio-for-portfolio against PM India's
    current "Portfolios of the Union Council of Ministers" before it is stamped.

Party, state and constituency come from the Sansad Lok Sabha directory, only
where a minister's name matches a member exactly; Rajya Sabha ministers and
non-matches carry none of the three rather than a guessed one.

Usage (from work/election-atlas/):
    python3 tools/harvest-union-cabinet.py
    python3 tools/harvest-union-cabinet.py --cache /tmp/harvest --dry-run
"""
import argparse
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest_common import DATA, DEFAULT_CACHE, SourceShapeError, fetch, source_block, write_json  # noqa: E402
from validate_records import require_valid  # noqa: E402

PRES = "https://www.presidentofindia.gov.in/"
RNK = "https://ramnathkovind.nic.in/"
SWORN_2014 = PRES + "pranab-mukherjee/press_releases/president-allocates-portfolios-cabinet-ministers-and-ministers"
FULL_2017 = RNK + "pr030917_2.html"
END_2014 = RNK + "pr240519.html"
SWORN_2024 = PRES + "press_releases/press-communique-18"
SANSAD_LS = "https://sansad.in/api_ls/member?loksabha={}&lang=en"

# Changes after the 03.09.2017 full re-allocation, to the end of the 16th Lok
# Sabha. Found by reading every release on ramnathkovind.nic.in from September
# 2017 to May 2019 that says "as advised by the Prime Minister".
# ops: remove (leaves the council), add (portfolio item), drop (portfolio item,
# matched as a substring), replace (portfolio item -> new text).
CHANGES_2014 = [
    {"date": "2018-03-09", "url": RNK + "pr090318.html",
     "sentence": "has accepted the resignation of the following Ministers from the Union Council of Ministers",
     "ops": [("remove", "ASHOK GAJAPATHI RAJU PUSAPATI"), ("remove", "Y.S. CHOWDARY"),
             ("add", "NARENDRA MODI", "Ministry of Civil Aviation")]},
    {"date": "2018-03-10", "url": RNK + "pr100318.html",
     "sentence": "Shri Suresh Prabhu, Cabinet Minister shall be assigned the charge of the Ministry of Civil Aviation",
     "ops": [("drop", "NARENDRA MODI", "Ministry of Civil Aviation"),
             ("add", "SURESH PRABHU", "Minister of Civil Aviation")]},
    {"date": "2018-05-14", "url": RNK + "pr140518.html",
     "sentence": "the portfolios of Minister of Finance and Minister of Corporate Affairs held by him, be temporarily assigned to Shri Piyush Goyal",
     "ops": [("drop", "ARUN JAITLEY", "Minister of Finance"), ("drop", "ARUN JAITLEY", "Minister of Corporate Affairs"),
             ("add", "PIYUSH GOYAL", "Minister of Finance"), ("add", "PIYUSH GOYAL", "Minister of Corporate Affairs")]},
    {"date": "2018-05-14", "url": RNK + "pr140518.html",
     "sentence": "Col. Rajyavardhan Singh Rathore be assigned the independent charge as Minister of State in the Ministry of Information and Broadcasting, in place of Smt. Smriti Zubin Irani",
     "ops": [("drop", "SMRITI ZUBIN IRANI", "Minister of Information and Broadcasting"),
             ("replace", "RAJYAVARDHAN SINGH RATHORE", "Minister of State in the Ministry of Information and Broadcasting",
              "Minister of State (Independent Charge) of the Ministry of Information and Broadcasting")]},
    {"date": "2018-05-14", "url": RNK + "pr140518.html",
     "sentence": "Shri S.S. Ahluwalia, Minister of State be relieved of the charge of Ministry of Drinking Water & Sanitation and assigned the portfolio of Minister of State in the Ministry of Electronics & Information Technology",
     "ops": [("drop", "S.S. AHLUWALIA", "Drinking Water"),
             ("add", "S.S. AHLUWALIA", "Minister of State in the Ministry of Electronics & Information Technology")]},
    {"date": "2018-05-14", "url": RNK + "pr140518.html",
     "sentence": "Shri Alphons Kannanthanam, Minister of State be relieved of the charge of Minister of State in the Ministry of Electronics & Information Technology",
     "ops": [("drop", "ALPHONS KANNANTHANAM", "Electronics")]},
    {"date": "2018-08-23", "url": RNK + "pr230818.html",
     "sentence": "has directed to assign the portfolios of the Minister of Finance and Minister of Corporate Affairs to Shri Arun Jaitley",
     "ops": [("drop", "PIYUSH GOYAL", "Minister of Finance"), ("drop", "PIYUSH GOYAL", "Minister of Corporate Affairs"),
             ("add", "ARUN JAITLEY", "Minister of Finance"), ("add", "ARUN JAITLEY", "Minister of Corporate Affairs")]},
    {"date": "2018-10-17", "url": RNK + "pr171018.html",
     "sentence": "has accepted the resignation of Shri M.J. Akbar from the Union Council of Ministers",
     "ops": [("remove", "M.J. AKBAR")]},
    {"date": "2018-11-13", "url": RNK + "pr131118_1.html",
     "sentence": "Shri D. V. Sadananda Gowda, Cabinet Minister, be assigned the charge of the Ministry of Chemicals & Fertilizers",
     # The release reassigns both of Shri Ananth Kumar's ministries; the Sansad
     # 16th Lok Sabha directory records him as "Died" (checked in main()).
     "ops": [("remove", "ANANTH KUMAR"),
             ("add", "D.V. SADANANDA GOWDA", "Ministry of Chemicals & Fertilizers"),
             ("add", "NARENDRA SINGH TOMAR", "Ministry of Parliamentary Affairs")]},
    {"date": "2018-12-11", "url": RNK + "pr111218.html",
     "sentence": "has accepted the resignation of Shri Upendra Kushwaha from the Union Council of Ministers",
     "ops": [("remove", "UPENDRA KUSHWAHA")]},
    {"date": "2019-01-23", "url": RNK + "pr230119_2.html",
     "sentence": "the portfolios of Minister of Finance and Minister of Corporate Affairs held by him, be temporarily assigned to Shri Piyush Goyal",
     "ops": [("drop", "ARUN JAITLEY", "Minister of Finance"), ("drop", "ARUN JAITLEY", "Minister of Corporate Affairs"),
             ("add", "PIYUSH GOYAL", "Minister of Finance"), ("add", "PIYUSH GOYAL", "Minister of Corporate Affairs")]},
    {"date": "2019-02-15", "url": RNK + "pr150219.html",
     "sentence": "has directed to assign the portfolios of the Minister of Finance and Minister of Corporate Affairs to Shri Arun Jaitley",
     "ops": [("drop", "PIYUSH GOYAL", "Minister of Finance"), ("drop", "PIYUSH GOYAL", "Minister of Corporate Affairs"),
             ("add", "ARUN JAITLEY", "Minister of Finance"), ("add", "ARUN JAITLEY", "Minister of Corporate Affairs")]},
]
END_2014_SENTENCE = "tendered his resignation along with the Council of Ministers"

TITLE = r"(?:Shri|Smt\.?|Sushri|Kumari|Dr\.?|General|Gen\.|Col\.|Prof\.|Sadhvi|Sant)"
NAME_LINE = re.compile(rf"^(?:{TITLE}\s*\S|Rao\s+\S)")
SECTIONS = [
    (re.compile(r"^CABINET MINISTERS$", re.I), "cabinet"),
    (re.compile(r"^MINISTERS? OF STATE \(INDEPENDENT CHARGE\)$", re.I), "mos-ic"),
    (re.compile(r"^MINISTERS? OF STATE$", re.I), "mos"),
]


# ── reading an allocation release ────────────────────────────────────────────
def page_text_blocks(page: str, where: str):
    """The release body as text blocks, one per paragraph, table cell or line break."""
    start = page.find("Rashtrapati Bhavan")
    if start < 0:
        raise SourceShapeError(f"{where}: no 'Rashtrapati Bhavan' dateline")
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", page[start:], flags=re.S | re.I)
    body = re.sub(r"<(br|/p|/td|/tr|/li|/div|/h\d)[^>]*>", "\n", body, flags=re.I)
    body = html.unescape(re.sub(r"<[^>]+>", " ", body)).replace(" ", " ")
    return [" ".join(line.split()) for line in body.split("\n") if line.strip()]


def plain(page: str) -> str:
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S | re.I)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).replace(" ", " ").split())


def name_key(name: str) -> str:
    """'Shri D. V. Sadananda Gowda' -> 'D.V. SADANANDA GOWDA' (title dropped, initials closed up)."""
    n = re.sub(rf"^{TITLE}\s*", "", name.strip(), flags=re.I)
    n = re.sub(r"\.\s+(?=[A-Z]\.)", ".", n.upper())
    return " ".join(n.split()).rstrip(".")


def join_portfolio(lines):
    """Portfolio lines -> one '; '-separated string (the page splits on ';').

    The 2014 release puts one ministry per line with no separators; later ones
    separate items with ';' and wrap long items across lines."""
    if not any(";" in ln or ln.rstrip().endswith(",") for ln in lines):
        items = lines
    else:
        items = re.split(r";", " ".join(lines))
    out = []
    for it in items:
        it = re.sub(r"\band(?=Minister)", "and ", it)
        it = re.sub(r"^\s*and\s+", "", it.strip()).strip(" .;")
        if it:
            out.append(it)
    return "; ".join(out)


def parse_allocation(page: str, where: str):
    """A full allocation release -> [{name, rank, portfolio}], PM first."""
    blocks = page_text_blocks(page, where)
    first_section = next((i for i, b in enumerate(blocks) if any(rx.match(b) for rx, _ in SECTIONS)), None)
    if first_section is None:
        raise SourceShapeError(f"{where}: no CABINET MINISTERS heading")
    pm = [b for b in blocks[:first_section] if NAME_LINE.match(b)]
    if len(pm) != 1:
        raise SourceShapeError(f"{where}: expected one Prime Minister name before the first heading, found {pm}")
    members = [{"name": name_key(pm[0]), "rank": "pm", "portfolio": "Prime Minister"}]
    section, expect, cur = None, 1, None
    for b in blocks[first_section:]:
        hit = next((rank for rx, rank in SECTIONS if rx.match(b)), None)
        if hit:
            section, expect, cur = hit, 1, None
            continue
        if re.match(r"^This release issued|^\(.*\)\s*Press Secretary|^For immediate release", b, re.I):
            break
        serial = re.fullmatch(r"(\d+)\.", b)
        if serial:
            if int(serial.group(1)) != expect:
                raise SourceShapeError(f"{where}: serial {serial.group(1)} in {section}, expected {expect}")
            expect += 1
            cur = {"name": None, "rank": section, "lines": []}
            members.append(cur)
            continue
        if cur is None:
            continue
        if cur["name"] is None:
            if not NAME_LINE.match(b):
                raise SourceShapeError(f"{where}: {section} #{expect - 1} does not start with a name: {b!r}")
            cur["name"] = name_key(b)
        else:
            cur["lines"].append(b)
    for m in members[1:]:
        lines = m.pop("lines")
        if not lines:
            raise SourceShapeError(f"{where}: {m['name']} has no portfolio")
        m["portfolio"] = join_portfolio(lines)
        if m["rank"] == "mos" and "Independent Charge" in m["portfolio"]:
            m["rank"] = "mos-ic"
    return members


# ── applying changes ─────────────────────────────────────────────────────────
def apply_changes(members, changes, pages, where):
    roster = {m["name"]: dict(m) for m in members}
    log = []
    for ch in changes:
        if " ".join(ch["sentence"].split()) not in plain(pages[ch["url"]]):
            raise SourceShapeError(f"{ch['url']}: the transcribed sentence is not in the release: {ch['sentence'][:80]}")
        for op in ch["ops"]:
            kind, name = op[0], op[1]
            if name not in roster:
                raise SourceShapeError(f"{where} {ch['date']}: {name} is not on the roster for {kind}")
            items = [p for p in roster[name]["portfolio"].split("; ") if p]
            if kind == "remove":
                del roster[name]
            elif kind == "add":
                items.append(op[2])
            elif kind == "drop":
                keep = [p for p in items if op[2] not in p]
                if len(keep) != len(items) - 1:
                    raise SourceShapeError(f"{where} {ch['date']}: {name} holds {len(items) - len(keep)} items matching {op[2]!r}")
                items = keep
            elif kind == "replace":
                if op[2] not in items:
                    raise SourceShapeError(f"{where} {ch['date']}: {name} does not hold {op[2]!r}")
                items = [op[3] if p == op[2] else p for p in items]
                if "Independent Charge" in op[3] and roster[name]["rank"] == "mos":
                    roster[name]["rank"] = "mos-ic"
            if kind != "remove":
                roster[name]["portfolio"] = "; ".join(items)
        log.append({"date": ch["date"], "sentence": ch["sentence"],
                    "ops": [list(op) for op in ch["ops"]], "url": ch["url"]})
    return list(roster.values()), log


# ── Sansad join ──────────────────────────────────────────────────────────────
def sansad_directory(term_no, cache):
    got = fetch(SANSAD_LS.format(term_no), cache)
    doc = json.loads(got["bytes"])
    recs = doc.get("membersDtoList") if isinstance(doc, dict) else doc
    if not recs:
        raise SourceShapeError(f"{got['url']}: no membersDtoList")
    return got, recs


def enrich(members, recs, regions):
    """Party / state / constituency from exact name matches in the Lok Sabha directory."""
    spec = importlib.util.spec_from_file_location("join_sansad", Path(__file__).parent / "join-sansad.py")
    js = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(js)
    by_name = {}
    for r in recs:
        nm = r.get("mpFirstLastName") or f"{r.get('firstName', '')} {r.get('lastName', '')}"
        by_name.setdefault(js.no_space(nm), []).append(r)
    state_code = {js.norm_state(s): r["code"] for r in regions for s in [r["name"], *r.get("sourceNames", [])]}
    for m in members:
        hits = by_name.get(js.no_space(m["name"]), [])
        if len(hits) == 1:
            r = hits[0]
            m["party"] = js.PARTY_MAP.get(r.get("partySname"), r.get("partySname"))
            m["state"] = state_code.get(js.norm_state(r.get("stateName")))
            m["constituency"] = r.get("constName")
            m["mpsno"] = r.get("mpsno")
    return members


# ── main ─────────────────────────────────────────────────────────────────────
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Harvest the Union Council of Ministers, sworn in and as it stands.")
    ap.add_argument("--cache", default=str(DEFAULT_CACHE))
    ap.add_argument("--out", default=str(DATA / "cabinet" / "union"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    cache = args.cache
    regions = json.loads((DATA / "regions.json").read_text())["regions"]
    outputs = {}

    # 2014
    sworn_got = fetch(SWORN_2014, cache)
    sworn = parse_allocation(sworn_got["bytes"].decode("utf-8", "replace"), "2014 sworn in")
    if len(sworn) - 1 != 45:  # the Prime Minister plus 45 ministers (23 + 10 + 12)
        raise SourceShapeError(f"2014 sworn-in roster has {len(sworn) - 1} ministers besides the PM, the release lists 45")
    full_got = fetch(FULL_2017, cache)
    full = parse_allocation(full_got["bytes"].decode("utf-8", "replace"), "2017 re-allocation")
    change_pages, sources = {}, [source_block("president-secretariat", sworn_got),
                                 source_block("president-secretariat", full_got)]
    for ch in CHANGES_2014:
        if ch["url"] not in change_pages:
            got = fetch(ch["url"], cache)
            change_pages[ch["url"]] = got["bytes"].decode("utf-8", "replace")
            sources.append(source_block("president-secretariat", got))
    end_got = fetch(END_2014, cache)
    if END_2014_SENTENCE not in plain(end_got["bytes"].decode("utf-8", "replace")):
        raise SourceShapeError(f"{END_2014}: does not record the council's resignation")
    sources.append(source_block("president-secretariat", end_got))
    dir_got, recs16 = sansad_directory(16, cache)
    if not any(r.get("mpFirstLastName") == "Ananth Kumar" and r.get("status") == "Died" for r in recs16):
        raise SourceShapeError("Sansad 16th Lok Sabha directory does not record Ananth Kumar as Died")
    sources.append(source_block("sansad", dir_got))
    stands, log = apply_changes(full, CHANGES_2014, change_pages, "2014")
    src_of = {s["url"]: i for i, s in enumerate(sources)}
    for entry in log:
        entry["src"] = src_of[entry.pop("url")]
    enrich(sworn, recs16, regions)
    enrich(stands, recs16, regions)
    doc14 = {
        "schema": 2, "scope": "union", "cycle": 2014, "term": "16th Lok Sabha", "swornIn": "2014-05-26",
        "provenance": "published", "source": sources[0], "sources": sources,
        "note": ("Union Council of Ministers from President's Secretariat releases. `members` is the "
                 "council as sworn in, the allocation of 27.05.2014 (oath 26.05.2014). `as_it_stands` is the council at the end of "
                 "the 16th Lok Sabha (`asOf`): the full re-allocation of 03.09.2017 with every later change applied "
                 "(`changes`, each with its release's own sentence). Reshuffles between 2014 and 2017 are "
                 "contained in the 2017 re-allocation and are not itemised. Party, state and constituency "
                 "come from exact name matches in the Sansad 16th Lok Sabha directory."),
        "allocated": "2014-05-27", "fetchedAt": sworn_got["fetched_at"][:10],
        "members": sworn,
        "asOf": "2019-05-24",
        "as_it_stands": stands,
        "changes": log,
    }
    outputs[Path(args.out) / "2014.json"] = doc14
    print(f"2014: sworn in {len(sworn)}, as it stands {len(stands)} after {len(log)} changes")

    # 2024
    path24 = DATA / "cabinet" / "union" / "2024.json"
    doc24 = json.loads(path24.read_text())
    sworn24_got = fetch(SWORN_2024, cache)
    sworn24 = parse_allocation(sworn24_got["bytes"].decode("utf-8", "replace"), "2024 sworn in")
    if len(sworn24) - 1 != 71:  # the Prime Minister plus 71 ministers
        raise SourceShapeError(f"2024 sworn-in roster has {len(sworn24) - 1} ministers besides the PM, the communique lists 71")
    spec = importlib.util.spec_from_file_location("fetch_cabinet", Path(__file__).parent / "fetch-cabinet.py")
    fc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fc)
    pmi_got = fetch(fc.PMINDIA_PORTFOLIOS, cache)
    pmi_page = pmi_got["bytes"].decode("utf-8", "replace")
    current = ([fc.parse_pm(pmi_page)] if fc.parse_pm(pmi_page) else []) + fc.parse_portfolios(pmi_page)
    have = {(m["name"], m["rank"], m["portfolio"]) for m in doc24["members"]}
    now = {(m["name"], m["rank"], m["portfolio"]) for m in current}
    if have != now:
        raise SourceShapeError(f"2024 roster differs from PM India today ({len(now - have)} new, {len(have - now)} gone); "
                               "refresh it with fetch-cabinet.py and join-sansad.py first")
    dir18_got, recs18 = sansad_directory(18, cache)
    enrich(sworn24, recs18, regions)
    photo_of = {m["name"]: m["photo"] for m in doc24["members"] if m.get("photo")}
    for m in sworn24:  # same official name, same person: reuse the portrait already held
        if m["name"] in photo_of:
            m["photo"] = photo_of[m["name"]]
    sources24 = [source_block("pmindia", pmi_got), source_block("president-secretariat", sworn24_got),
                 source_block("sansad", dir18_got)]
    doc24.pop("_communiques", None)
    doc24.pop("_note", None)
    out24 = {
        "schema": 2, "scope": "union", "cycle": 2024, "term": doc24["term"], "swornIn": doc24["swornIn"],
        "fetchedAt": pmi_got["fetched_at"][:10], "provenance": "published",
        "source": sources24[0], "sources": sources24,
        "note": ("Union Council of Ministers. `as_it_stands` is PM India's current portfolio list on "
                 "`asOf`, joined to the Sansad directory for party, state, constituency and photo. "
                 "`members` is the council as sworn in: the President's press communique of 10.06.2024 "
                 "(oath 09.06.2024)."),
        "allocated": "2024-06-10",
        "members": sworn24,
        "asOf": pmi_got["fetched_at"][:10],
        "as_it_stands": doc24["members"],
        "changes": doc24.get("changes", []),
    }
    outputs[Path(args.out) / "2024.json"] = out24
    print(f"2024: sworn in {len(sworn24)}, as it stands {len(doc24['members'])} (matches PM India)")

    require_valid(outputs, cache)
    if not args.dry_run:
        for p, d in outputs.items():
            write_json(p, d)
        print(f"wrote {len(outputs)} files under {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

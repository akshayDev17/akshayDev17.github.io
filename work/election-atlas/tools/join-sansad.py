#!/usr/bin/env python3
"""Join the fetched Union Council of Ministers to the Sansad member directory.

Fills in, from the official Parliament of India member directory (.gov.in):
  - party (mapped to the atlas party code),
  - state (mapped to the atlas region code),
  - constituency (Lok Sabha only; Rajya Sabha members have none),
  - photo (downloaded + credited).

Sources:
  - Lok Sabha:  https://sansad.in/api_ls/member            (all members, one call)
  - Rajya Sabha: https://sansad.in/api_rs/member/in-council-of-ministers

Usage:
  python3 tools/join-sansad.py --cycle 2024 \
      --in  _research/cabinet-fetched/2024.json \
      --out _research/cabinet-fetched/2024.enriched.json
"""
import argparse
import json
import re
import subprocess
import sys
import difflib
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

LS_URL = "https://sansad.in/api_ls/member?lang=en"
RS_URL = "https://sansad.in/api_rs/member/in-council-of-ministers?lang=en"

# Manual aliases: cabinet name (normalised) -> Sansad name (normalised).
# These are the few where the two official sources genuinely disagree on
# spelling, initials, or word order, and no generic rule recovers them.
ALIASES = {
    "C R PATIL": "CHANDRAKANT RAGHUNATH PATIL",
    "KRISHAN PAL": "KRISHAN PAL GURJAR",
    "PANKAJ CHAUDHARY": "PANKAJ CHOUDHARY",
    "BHUPATHI RAJU SRINIVASA VARMA": "SRINIVASA VARMA BHUPATHIRAJU",
}

# Sansad party code -> atlas party code. Unmapped codes stay as-is and render
# grey (the atlas fallback) until they are added to parties.json.
PARTY_MAP = {
    "BJP": "BJP", "INC": "INC", "SP": "SP", "BSP": "BSP", "AITC": "AITC",
    "CPM": "CPM", "CPI(M)": "CPM", "CPI": "CPI", "DMK": "DMK",
    "AIADMK": "AIADMK", "YSRCP": "YSRCP", "TDP": "TDP", "BRS": "BRS",
    "JD(U)": "JDU", "JDU": "JDU", "RJD": "RJD", "SHS": "SHS", "SS": "SHS",
    "NCP": "NCP", "AAP": "AAP", "BJD": "BJD", "IND": "IND", "Ind.": "IND",
    "JD(S)": "JDS", "HAM (S)": "HAMS", "LJSP(RV)": "LJSP", "RLD": "RLD",
    "RPI (ATWL)": "RPIA", "Apna Dal (S)": "ADS",
}


def fetch_json(url):
    r = subprocess.run(["curl", "-sSL", "-m", "60", "-A", UA, url],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed for {url}: {r.stderr.decode('utf-8', 'replace')[:200]}")
    return json.loads(r.stdout.decode("utf-8", "replace"))


def norm(name):
    n = (name or "").upper()
    n = re.sub(r"\b(?:SHRI|SMT\.?|DR\.?|KUMARI|PROF\.?|COL\.?|SADHVI|SUSHRI)\s*", "", n)
    n = re.sub(r"\s+ALIAS\s+.*$", "", n)          # "Rajiv Ranjan Singh alias …"
    n = n.replace(".", "")                        # "H. D." -> "H D"
    n = re.sub(r"[^A-Z ]", "", n)
    return re.sub(r"\s+", " ", n).strip()


def no_space(name):
    return norm(name).replace(" ", "")


def norm_state(name):
    """Fold the few state-name spellings Sansad uses that regions.json doesn't."""
    s = (name or "").strip().upper()
    s = s.replace(" AND ", " & ")        # "Jammu and Kashmir" -> "Jammu & Kashmir"
    s = s.replace("NCT OF DELHI", "DELHI")
    return s


def build_lookup():
    """Return {norm_name: record} and {no_space_name: record} plus a record list."""
    records = []
    ls = fetch_json(LS_URL)
    for m in ls.get("membersDtoList", []):
        if m.get("status") != "Sitting":
            continue
        name = m.get("mpFirstLastName") or f"{m.get('firstName','')} {m.get('lastName','')}"
        records.append({"house": "ls", "name": norm(name),
                        "party": m.get("partySname"), "state": m.get("stateName"),
                        "const": m.get("constName"), "photo": m.get("imageUrl"),
                        "id": m.get("mpsno")})
    rs = fetch_json(RS_URL)
    for m in rs.get("records", []):
        name = f"{m.get('firstName','')} {m.get('lastName','')}"
        records.append({"house": "rs", "name": norm(name),
                        "party": m.get("partyCode"), "state": m.get("stateName"),
                        "const": None, "photo": m.get("imageUrl"),
                        "id": m.get("mpCode")})
    by_norm, by_nospace = {}, {}
    for r in records:
        by_norm.setdefault(r["name"], r)
        by_nospace.setdefault(no_space(r["name"]), r)
    return records, by_norm, by_nospace


def match_member(cab_name, records, by_norm, by_nospace):
    key = norm(cab_name)
    # 1. exact
    if key in by_norm:
        return by_norm[key]
    # 2. exact ignoring spaces
    if no_space(key) in by_nospace:
        return by_nospace[no_space(key)]
    # 3. manual alias
    if key in ALIASES:
        t = norm(ALIASES[key])
        if t in by_norm:
            return by_norm[t]
        if no_space(t) in by_nospace:
            return by_nospace[no_space(t)]
    # 4. last-name anchored, best similarity
    last = key.split()[-1] if key.split() else ""
    subs = [r for r in records if r["name"].split() and r["name"].split()[-1] == last]
    if len(subs) == 1:
        return subs[0]
    if subs:
        return max(subs, key=lambda r: difflib.SequenceMatcher(None, key, r["name"]).ratio())
    # 5. global best similarity
    return max(records, key=lambda r: difflib.SequenceMatcher(None, key, r["name"]).ratio())


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", type=int, default=2024)
    ap.add_argument("--in", dest="inp", default=None,
                    help="cabinet JSON from fetch-cabinet.py")
    ap.add_argument("--out", default=None)
    ap.add_argument("--photo-dir", default=None,
                    help="where to write portraits (default: data/photos/cabinet/<cycle>)")
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.inp:
        doc = json.load(open(args.inp, encoding="utf-8"))
    else:
        # re-fetch the cabinet on the fly
        sys.path.insert(0, str(Path(__file__).parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "fetch_cabinet", Path(__file__).parent / "fetch-cabinet.py")
        fetch_cabinet = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fetch_cabinet)
        members = fetch_cabinet.parse_portfolios(fetch_cabinet.fetch(fetch_cabinet.PMINDIA_PORTFOLIOS))
        pm = fetch_cabinet.parse_pm(fetch_cabinet.fetch(fetch_cabinet.PMINDIA_PORTFOLIOS))
        if pm:
            members.insert(0, pm)
        doc = {"members": members}

    records, by_norm, by_nospace = build_lookup()
    regions = json.load(open(Path(__file__).parent.parent / "data" / "regions.json", encoding="utf-8"))
    state_to_code = {}
    for r in regions["regions"]:
        for s in r.get("sourceNames", []):
            state_to_code[norm_state(s)] = r["code"]

    photo_dir = args.photo_dir or f"data/photos/cabinet/{args.cycle}"
    credits = {}
    unmatched = []
    for m in doc["members"]:
        rec = match_member(m["name"], records, by_norm, by_nospace)
        m["party"] = PARTY_MAP.get(rec["party"], rec["party"])
        m["state"] = state_to_code.get(norm_state(rec["state"]))
        m["constituency"] = rec["const"]
        m["_match"] = rec["name"]
        if rec["photo"] and not args.no_download:
            ext = ".jpg"
            fname = f"{rec['house']}-{rec['id']}{ext}"
            path = Path(photo_dir) / fname
            path.parent.mkdir(parents=True, exist_ok=True)
            r = subprocess.run(["curl", "-sSL", "-m", "40", "-A", UA,
                                rec["photo"], "-o", str(path)], capture_output=True)
            if r.returncode == 0 and path.stat().st_size > 2000:
                m["photo"] = f"{args.cycle}/{fname}"
                credits[fname] = {"url": rec["photo"],
                                  "authority": "Parliament of India (Sansad)"}
            else:
                m["photo"] = None
                path.unlink(missing_ok=True)
        else:
            m["photo"] = None
        if rec["house"] == "rs" and not m.get("constituency"):
            pass  # RS members have no Lok Sabha constituency

    doc["_join"] = {"source": "Parliament of India (Sansad) member directory",
                    "matched": sum(1 for m in doc["members"] if m.get("party")),
                    "total": len(doc["members"])}
    # drop the internal match field for the final file? keep it for audit.
    out = args.out or f"data/cabinet/union/{args.cycle}.json"
    if args.dry_run:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return
    json.dump(doc, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    if credits:
        json.dump(credits, open(Path(photo_dir) / "credits.json", "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
    print(f"enriched {len(doc['members'])} members -> {out}")
    print(f"photos: {len(credits)} written to {photo_dir}")


if __name__ == "__main__":
    main()

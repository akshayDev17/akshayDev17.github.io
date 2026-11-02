#!/usr/bin/env python3
"""Sworn-in ministers get the Sansad id and party the as-it-stands roster holds,
even when the communique spells their name differently, and never a guessed one.

    python3 tools/test_harvest_union_cabinet.py
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("harvest_union_cabinet", HERE / "harvest-union-cabinet.py")
huc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(huc)

UNION = HERE.parent / "data" / "cabinet" / "union"


def ids(m):
    return {k: m[k] for k in ("mpsno", "house") if k in m}


def party(m):
    return m.get("party")


class CopySansadIds(unittest.TestCase):
    def setUp(self):
        self.prior = json.loads((UNION / "2024.json").read_text(encoding="utf-8"))["members"]

    def test_communique_spellings_meet_the_roster(self):
        sworn = [{"name": "JADHAV PRATAPRAO GANPATRAO"}, {"name": "B.L. VERMA"},
                 {"name": "RAVNEET SINGH"}, {"name": "GEORGE KURIAN"}, {"name": "AMIT SHAH"}]
        log = huc.copy_sansad_ids(sworn, self.prior, [])
        by = {m["name"]: ids(m) for m in sworn}
        self.assertEqual(by["JADHAV PRATAPRAO GANPATRAO"], {"mpsno": 4373})
        self.assertEqual(by["B.L. VERMA"], {"house": "rs"})
        self.assertEqual(by["AMIT SHAH"], {"mpsno": 5021})
        self.assertEqual(by["RAVNEET SINGH"], {})
        self.assertEqual(by["GEORGE KURIAN"], {})
        parties = {m["name"]: party(m) for m in sworn}
        self.assertEqual(parties["JADHAV PRATAPRAO GANPATRAO"], "SHS")
        self.assertEqual(parties["B.L. VERMA"], "BJP")
        self.assertEqual(parties["AMIT SHAH"], "BJP")
        self.assertIsNone(parties["RAVNEET SINGH"])
        self.assertIsNone(parties["GEORGE KURIAN"])
        self.assertEqual({(n, m) for n, m, _ in log},
                         {("JADHAV PRATAPRAO GANPATRAO", "PRATAPRAO JADHAV"), ("B.L. VERMA", "B. L. VERMA")})

    def test_directory_fills_a_name_the_roster_lacks(self):
        sworn = [{"name": "GEORGE KURIAN"}]
        directory = huc.directory_entries([{"mpFirstLastName": "Kurian George", "mpsno": 9999,
                                            "partySname": "BJP", "constName": "Somewhere"}], [])
        huc.copy_sansad_ids(sworn, self.prior, directory)
        self.assertEqual(ids(sworn[0]), {"mpsno": 9999})
        self.assertEqual((party(sworn[0]), sworn[0]["constituency"]), ("BJP", "Somewhere"))

    def test_an_ambiguous_match_copies_nothing(self):
        sworn = [{"name": "RAVNEET SINGH"}]
        directory = huc.directory_entries([{"mpFirstLastName": "Ravneet Singh Bittu", "mpsno": 1},
                                           {"mpFirstLastName": "Ravneet Singh Sidhu", "mpsno": 2}], [])
        self.assertEqual(huc.copy_sansad_ids(sworn, self.prior, directory), [])
        self.assertEqual(ids(sworn[0]), {})
        self.assertIsNone(party(sworn[0]))

    def test_a_party_already_held_is_kept(self):
        sworn = [{"name": "AMIT SHAH", "party": "XYZ"}]
        huc.copy_sansad_ids(sworn, self.prior, [])
        self.assertEqual((party(sworn[0]), sworn[0]["mpsno"]), ("XYZ", 5021))

    def test_an_id_already_held_is_not_given_twice(self):
        sworn = [{"name": "PRATAPRAO JADHAV"}, {"name": "JADHAV PRATAPRAO GANPATRAO"}]
        huc.copy_sansad_ids(sworn, self.prior, [])
        self.assertEqual([ids(m) for m in sworn], [{"mpsno": 4373}, {}])

    def test_committed_sworn_in_roster_carries_the_backfilled_ids(self):
        members = {m["name"]: m for m in
                   json.loads((UNION / "2024-sworn-in.json").read_text(encoding="utf-8"))["members"]}
        self.assertEqual(ids(members["JADHAV PRATAPRAO GANPATRAO"]), {"mpsno": 4373})
        self.assertEqual(ids(members["B.L. VERMA"]), {"house": "rs"})
        self.assertEqual(party(members["JADHAV PRATAPRAO GANPATRAO"]), "SHS")
        self.assertEqual(party(members["B.L. VERMA"]), "BJP")
        self.assertEqual(sorted(n for n, m in members.items() if not party(m)), ["GEORGE KURIAN", "RAVNEET SINGH"])


def directory_first_last(name):
    """'Jadhav, Shri Prataprao Ganpatrao' -> 'Shri Prataprao Ganpatrao Jadhav'."""
    last, _, first = name.partition(", ")
    return f"{first} {last}" if first else last


def same_person(minister, directory_name):
    """An exact or ALIASES match (join-sansad), or the harvester's normalised-name match."""
    fl = directory_first_last(directory_name)
    key = huc.js.norm(minister)
    if huc.js.no_space(fl) in {huc.js.no_space(key), huc.js.no_space(huc.js.ALIASES.get(key, key))}:
        return True
    a, b = huc.name_tokens(minister), huc.name_tokens(fl)
    return len(a & b) >= 2 and (a <= b or b <= a)


class RosterLinksPointAtTheMinister(unittest.TestCase):
    """Every Lok Sabha member number on a 2024 roster is that minister's own seat
    in data/members/ls/2024.json, with the same state and constituency."""

    def setUp(self):
        seats = json.loads((HERE.parent / "data" / "members" / "ls" / "2024.json").read_text(encoding="utf-8"))
        self.by_mpsno = {m["mpsno"]: m for m in seats["members"].values()}
        regions = json.loads((HERE.parent / "data" / "regions.json").read_text(encoding="utf-8"))["regions"]
        self.state_code = {huc.js.norm_state(n): r["code"] for r in regions for n in [r["name"], *r.get("sourceNames", [])]}

    def audit(self, roster):
        members = json.loads((UNION / roster).read_text(encoding="utf-8"))["members"]
        for m in members:
            if "mpsno" not in m:
                continue
            with self.subTest(roster=roster, minister=m["name"]):
                seat = self.by_mpsno.get(m["mpsno"])
                self.assertIsNotNone(seat, f"mpsno {m['mpsno']} is no 2024 Lok Sabha member")
                self.assertTrue(same_person(m["name"], seat["name"]), f"mpsno {m['mpsno']} is {seat['name']}")
                self.assertEqual(m.get("state"), self.state_code.get(huc.js.norm_state(seat["state"])))
                self.assertEqual(m.get("constituency"), seat["seat"])
        return sorted(m["name"] for m in members if not (m.get("mpsno") or m.get("house")))

    def test_as_it_stands_roster(self):
        self.assertEqual(self.audit("2024.json"), ["L. MURUGAN"])

    def test_sworn_in_roster(self):
        self.assertEqual(self.audit("2024-sworn-in.json"), ["GEORGE KURIAN", "L. MURUGAN", "RAVNEET SINGH"])

    def test_the_audit_rejects_another_members_number(self):
        self.assertFalse(same_person("BHUPATHI RAJU SRINIVASA VARMA", self.by_mpsno[5711]["name"]))
        self.assertTrue(same_person("BHUPATHI RAJU SRINIVASA VARMA", self.by_mpsno[5745]["name"]))


class JoinSansadMatch(unittest.TestCase):
    """join-sansad joins a minister only by exact name or ALIASES, never by likeness."""

    @staticmethod
    def lookup(*names):
        recs = [{"name": huc.js.norm(n), "id": i} for i, n in enumerate(names, 1)]
        return {r["name"]: r for r in recs}, {huc.js.no_space(r["name"]): r for r in recs}

    def test_a_near_name_is_not_joined(self):
        by_norm, by_nospace = self.lookup("Kota Srinivasa Poojary", "Ramdas Athawale Kumar")
        self.assertIsNone(huc.js.match_member("BHUPATHI RAJU SRINIVASA VARMA", by_norm, by_nospace))
        self.assertIsNone(huc.js.match_member("RAMDAS ATHAWALE", by_norm, by_nospace))

    def test_exact_and_alias_names_are_joined(self):
        by_norm, by_nospace = self.lookup("Kota Srinivasa Poojary", "Srinivasa Varma B J P Varma Bhupathiraju", "Rajnath Singh")
        self.assertEqual(huc.js.match_member("BHUPATHI RAJU SRINIVASA VARMA", by_norm, by_nospace)["id"], 2)
        self.assertEqual(huc.js.match_member("RAJ NATH SINGH", by_norm, by_nospace)["id"], 3)


if __name__ == "__main__":
    unittest.main()

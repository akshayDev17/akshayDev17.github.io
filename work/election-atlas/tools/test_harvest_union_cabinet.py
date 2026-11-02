#!/usr/bin/env python3
"""Sworn-in ministers get the Sansad id the as-it-stands roster holds, even when
the communique spells their name differently, and never a guessed one.

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
        self.assertEqual({(n, m) for n, m, _ in log},
                         {("JADHAV PRATAPRAO GANPATRAO", "PRATAPRAO JADHAV"), ("B.L. VERMA", "B. L. VERMA")})

    def test_directory_fills_a_name_the_roster_lacks(self):
        sworn = [{"name": "GEORGE KURIAN"}]
        huc.copy_sansad_ids(sworn, self.prior, [{"mpFirstLastName": "Kurian George", "mpsno": 9999}])
        self.assertEqual(ids(sworn[0]), {"mpsno": 9999})

    def test_an_ambiguous_match_copies_nothing(self):
        sworn = [{"name": "RAVNEET SINGH"}]
        directory = [{"mpFirstLastName": "Ravneet Singh Bittu", "mpsno": 1},
                     {"mpFirstLastName": "Ravneet Singh Sidhu", "mpsno": 2}]
        self.assertEqual(huc.copy_sansad_ids(sworn, self.prior, directory), [])
        self.assertEqual(ids(sworn[0]), {})

    def test_an_id_already_held_is_not_given_twice(self):
        sworn = [{"name": "PRATAPRAO JADHAV"}, {"name": "JADHAV PRATAPRAO GANPATRAO"}]
        huc.copy_sansad_ids(sworn, self.prior, [])
        self.assertEqual([ids(m) for m in sworn], [{"mpsno": 4373}, {}])

    def test_committed_sworn_in_roster_carries_the_backfilled_ids(self):
        members = {m["name"]: m for m in
                   json.loads((UNION / "2024-sworn-in.json").read_text(encoding="utf-8"))["members"]}
        self.assertEqual(ids(members["JADHAV PRATAPRAO GANPATRAO"]), {"mpsno": 4373})
        self.assertEqual(ids(members["B.L. VERMA"]), {"house": "rs"})


if __name__ == "__main__":
    unittest.main()

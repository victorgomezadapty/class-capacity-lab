import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import analysis as A  # noqa: E402
import build_sessions as B  # noqa: E402


class TestFunctions(unittest.TestCase):
    def test_weighted_auc_perfect_and_chance(self):
        self.assertAlmostEqual(A.weighted_auc(np.array([0.1, 0.9]), np.array([0, 5]), np.array([5, 0])), 1.0)
        self.assertAlmostEqual(A.weighted_auc(np.array([0.5, 0.5]), np.array([3, 1]), np.array([1, 3])), 0.5)

    def test_cramers_v_independent_is_zero(self):
        t = pd.DataFrame({"g": ["a", "b"], "full": [10, 20], "sessions": [100, 200]})
        self.assertAlmostEqual(A.cramers_v(t, "g"), 0.0)

    def test_family_rules(self):
        self.assertEqual(B.family("Pilates MesD"), "Pilates")
        self.assertEqual(B.family("Gimnasia acuática"), "Aquatic fitness")
        self.assertEqual(B.family("Natación acondicionamiento"), "Swimming")
        self.assertEqual(B.family("Pádel acondicionamiento"), "Racket conditioning")
        self.assertEqual(B.family("Cubo Gym Cross Training/Funcional"), "Cross training and functional")
        self.assertEqual(B.slot(9), "Morning"); self.assertEqual(B.slot(19), "Evening")


class TestOutputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = pd.read_csv(ROOT / "data" / "processed" / "madrid_class_slots.csv.gz")
        cls.r = json.loads((ROOT / "data" / "processed" / "results.json").read_text())

    def test_slot_table_consistency(self):
        t = self.t
        self.assertTrue((t["booked"] <= t["places"]).all())
        self.assertTrue((t["full"] <= t["sessions"]).all())
        self.assertTrue((t["places"] >= 5 * t["sessions"]).all())
        self.assertEqual(int(t["sessions"].sum()), self.r["overall"]["sessions"])
        self.assertEqual(sorted(t["season"].unique()), A.SEASONS)

    def test_kaggle_file_matches(self):
        k = pd.read_csv(ROOT / "delivery" / "kaggle" / "dataset" / "madrid_class_slots.csv.gz")
        pd.testing.assert_frame_equal(k, self.t)

    def test_quality_log_adds_up(self):
        q = json.loads((ROOT / "data" / "processed" / "data_quality.json").read_text())
        self.assertEqual(q["directed_rows"] - sum(q["dropped"].values()), q["analysed_sessions"])
        self.assertEqual(q["analysed_sessions"], self.r["overall"]["sessions"])


class TestSite(unittest.TestCase):
    def test_pages_built_and_clean(self):
        for name in ["index.html", "dashboard.html", "evidence.html"]:
            html = (ROOT / "site" / name).read_text(encoding="utf-8")
            self.assertNotIn("{{", html, name)
            self.assertNotRegex(html, "[\u2013\u2014]", name)
            self.assertIn("CC BY 4.0", html, name)
            self.assertIn("datos.madrid.es/dataset/300076", html, name)

    def test_links_to_local_files_exist(self):
        for name in ["index.html", "dashboard.html", "evidence.html"]:
            html = (ROOT / "site" / name).read_text(encoding="utf-8")
            for ref in re.findall(r'(?:href|src)="([^"#?]+)', html):
                if ":" in ref or ref.startswith("//"):
                    continue
                self.assertTrue((ROOT / "site" / ref).exists(), f"{name}: {ref}")


if __name__ == "__main__":
    unittest.main()

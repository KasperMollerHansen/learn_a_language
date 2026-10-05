import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WordbankExpansionTests(unittest.TestCase):
    def test_wordbank_has_many_entries(self) -> None:
        bank = json.loads((ROOT / "wordbank.json").read_text(encoding="utf-8"))
        self.assertGreater(len(bank["words"]), 250)
        self.assertTrue(all(len(level["wordIds"]) == 30 for level in bank["levels"]))


if __name__ == "__main__":
    unittest.main()

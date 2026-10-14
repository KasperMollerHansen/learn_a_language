import unittest

from wordbank import load_wordbank


class WordbankExpansionTests(unittest.TestCase):
    def test_wordbank_has_many_entries(self) -> None:
        bank = load_wordbank()
        self.assertGreater(len(bank["words"]), 250)
        self.assertTrue(all(len(level["wordIds"]) == 30 for level in bank["levels"]))


if __name__ == "__main__":
    unittest.main()

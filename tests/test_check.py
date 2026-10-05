import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ready.check import Check  # noqa: E402


class CheckTest(unittest.TestCase):
    def test_join_then_ready(self):
        book = Check(4, 10000)
        book.join("a", 0)
        self.assertTrue(book.set_ready("r1", "a"))

    def test_unknown_player_cannot_ready(self):
        self.assertFalse(Check(4, 10000).set_ready("r1", "ghost"))

    def test_confirm_without_missing(self):
        book = Check(4, 10000)
        book.join("a", 0)
        book.set_ready("r1", "a")
        self.assertTrue(book.confirm("a", 0)[0])


if __name__ == "__main__":
    unittest.main()

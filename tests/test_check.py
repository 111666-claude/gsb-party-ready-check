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

    def test_join_respects_cap(self):
        book = Check(2, 10000)
        self.assertTrue(book.join("a", 0))
        self.assertTrue(book.join("b", 0))
        self.assertFalse(book.join("c", 0))

    def test_bypass_only_once(self):
        book = Check(4, 10000)
        book.join("lead", 0)
        book.join("x", 0)
        book.set_ready("r1", "lead")
        self.assertTrue(book.confirm("lead", 0)[0])
        book.join("y", 0)
        self.assertFalse(book.confirm("lead", 0)[0])

    def test_bypass_exempts_first_missing_by_name(self):
        book = Check(4, 10000)
        for name in ("lead", "bob", "amy"):
            book.join(name, 0)
        book.set_ready("r1", "lead")
        ok, missing = book.confirm("lead", 0)
        self.assertFalse(ok)
        self.assertEqual(missing, ["bob"])

    def test_timeout_kicks_unready_member(self):
        book = Check(4, 1000)
        book.join("slow", 0)
        book.join("fast", 0)
        book.set_ready("r1", "fast")
        ok, missing = book.confirm("fast", 5000)
        self.assertTrue(ok)
        self.assertEqual(missing, [])
        self.assertEqual(book.kicked, ["slow"])
        self.assertNotIn("slow", book.members)

    def test_duplicate_req_id_rejected(self):
        book = Check(4, 10000)
        book.join("a", 0)
        self.assertTrue(book.set_ready("r1", "a"))
        book.ready.discard("a")
        self.assertFalse(book.set_ready("r1", "a"))

    def test_dump_load_round_trip(self):
        book = Check(4, 10000)
        book.join("lead", 0)
        book.join("afk", 0)
        book.set_ready("r1", "lead")
        book.confirm("lead", 0)
        restored = Check(4, 10000)
        restored.load(book.dump())
        self.assertEqual(restored.members, book.members)
        self.assertEqual(restored.ready, book.ready)
        self.assertEqual(restored.bypass_used, book.bypass_used)
        self.assertEqual(restored.seen, book.seen)


if __name__ == "__main__":
    unittest.main()

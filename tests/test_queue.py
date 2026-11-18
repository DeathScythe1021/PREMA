"""scripts/queue.py 的測試。執行：python3 -m unittest discover tests"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import queue_lib as q  # noqa: E402


DESC = """In this video...

🕰️ Timestamps For This Video:
0:00 Intro
0:30 Rubber Hose Design
1:15 Romantasy
2:40 Risograph & Risoprint
11:10 Regencycore
12:00 How To Search For Styles
1:02:03 Long Video Style

📱 Follow Kittl On Social:
0:99 not a timestamp line in social section
"""


def sample():
    return {
        "videos": [{"id": "AAA", "title": "20 More Design Styles", "published": "2026-02-13"}],
        "candidates": [
            {"name_en": "Romantasy", "video": "AAA", "t": "1:15", "status": "pending"},
            {"name_en": "Chinoiserie", "video": "AAA", "t": "1:50", "status": "pending"},
            {"name_en": "Trinket Design", "video": "AAA", "t": "10:50", "status": "done", "style_id": "trinket"},
            {"name_en": "Kidcore", "video": "AAA", "t": "11:40", "status": "skipped", "note": "x"},
            {"name_en": "Cottagecore", "video": "AAA", "t": "6:30", "status": "pending"},
        ],
    }


class TestSlug(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(q.slug("Risograph & Risoprint"), "risograph-and-risoprint")
        self.assertEqual(q.slug("  Neo Fruitger "), "neo-fruitger")
        self.assertEqual(q.slug("Y2K Retro"), "y2k-retro")
        self.assertEqual(q.slug("3x3 Grid"), "3x3-grid")

    def test_strips_design_suffix(self):
        self.assertEqual(q.style_key("Rubber Hose Design"), "rubber-hose")
        self.assertEqual(q.style_key("Swiss Punk Design"), "swiss-punk")
        self.assertEqual(q.style_key("Wabi Sabi Style"), "wabi-sabi")
        self.assertEqual(q.style_key("Glassmorphism"), "glassmorphism")


class TestTimestamps(unittest.TestCase):
    def test_parses_chapter_block_only(self):
        got = q.parse_timestamps(DESC)
        names = [n for _, n in got]
        self.assertEqual(names, ["Rubber Hose Design", "Romantasy", "Risograph & Risoprint",
                                 "Regencycore", "Long Video Style"])
        self.assertEqual(got[0][0], "0:30")
        self.assertEqual(got[-1][0], "1:02:03")

    def test_no_chapters(self):
        self.assertEqual(q.parse_timestamps("no chapters here"), [])

    def test_is_style_video(self):
        self.assertTrue(q.is_style_video("20 More Design Styles You've Been Searching For"))
        self.assertTrue(q.is_style_video("10 Design Names You've Been Searching For But Can't Find"))
        self.assertTrue(q.is_style_video("The 2027 Design Style Trends You Need To Know"))
        self.assertFalse(q.is_style_video("How To Use Kittl With Claude and ChatGPT (Full Demo)"))
        self.assertFalse(q.is_style_video("Best Selling Print On Demand Products"))


class TestQueueOps(unittest.TestCase):
    def test_next_returns_pending_in_order(self):
        d = sample()
        self.assertEqual([c["name_en"] for c in q.next_pending(d, 2)], ["Romantasy", "Chinoiserie"])
        self.assertEqual(len(q.next_pending(d, 10)), 3)

    def test_mark_done(self):
        d = sample()
        q.mark(d, "romantasy", "done", style_id="romantasy")
        c = q.find(d, "Romantasy")
        self.assertEqual(c["status"], "done")
        self.assertEqual(c["style_id"], "romantasy")

    def test_mark_done_requires_style_id(self):
        with self.assertRaises(ValueError):
            q.mark(sample(), "Romantasy", "done")

    def test_mark_unknown(self):
        with self.assertRaises(KeyError):
            q.mark(sample(), "Nope", "skipped")

    def test_mark_bad_status(self):
        with self.assertRaises(ValueError):
            q.mark(sample(), "Romantasy", "finished")

    def test_add_candidates_dedupes(self):
        d = sample()
        added = q.add_candidates(d, "BBB", [("0:10", "Romantasy"), ("0:20", "Trinket"),
                                            ("0:30", "Vaporwave"), ("0:40", "Intro"),
                                            ("0:50", "Final Thoughts"), ("1:00", "Swiss Punk Design")],
                                 existing_keys={"swiss-punk"})
        self.assertEqual([c["name_en"] for c in added], ["Vaporwave"])
        self.assertEqual(q.find(d, "Vaporwave")["status"], "pending")
        self.assertEqual(q.find(d, "Vaporwave")["video"], "BBB")


class TestCheck(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(q.check(sample(), style_ids={"trinket"}), [])

    def test_done_without_style_file(self):
        errs = q.check(sample(), style_ids=set())
        self.assertEqual(len(errs), 1)
        self.assertIn("trinket", errs[0])

    def test_duplicate_candidate(self):
        d = sample()
        d["candidates"].append({"name_en": "Romantasy Style", "video": "AAA", "t": "9:99", "status": "pending"})
        self.assertTrue(any("重複" in e for e in q.check(d, style_ids={"trinket"})))

    def test_unknown_video(self):
        d = sample()
        d["candidates"][0]["video"] = "ZZZ"
        self.assertTrue(any("ZZZ" in e for e in q.check(d, style_ids={"trinket"})))

    def test_style_exists_but_still_pending(self):
        errs = q.check(sample(), style_ids={"trinket", "cottagecore"})
        self.assertTrue(any("Cottagecore" in e for e in errs))


if __name__ == "__main__":
    unittest.main()

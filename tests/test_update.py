import unittest
from scripts.update import build_stats


class CollaborationViewTests(unittest.TestCase):
    def test_collaboration_views_are_separate_without_double_counting_total(self):
        entries = [
            {"artist": "Act A", "key": "act a", "id": "AAAAAAAAAAA", "songs": 1, "collab": False},
            {"artist": "Act A", "key": "act a", "id": "BBBBBBBBBBB", "songs": 0, "collab": True},
            {"artist": "Act B", "key": "act b", "id": "CCCCCCCCCCC", "songs": 1, "collab": False},
        ]
        found = {
            "AAAAAAAAAAA": {"id": "AAAAAAAAAAA", "title": "Solo", "views": 100},
            "BBBBBBBBBBB": {"id": "BBBBBBBBBBB", "title": "Collab", "views": 50},
            "CCCCCCCCCCC": {"id": "CCCCCCCCCCC", "title": "Other", "views": 50},
        }
        config = {
            "event": "MAMA 2026",
            "day": "Day 1",
            "day1_start_kst": "2026-11-20T18:00:00+09:00",
        }

        stats = build_stats(entries, found, config)
        acts = {act["artist"]: act for act in stats["acts"]}

        self.assertEqual(stats["total_views"], 200)
        self.assertEqual(stats["total_collaboration_views"], 50)
        self.assertEqual(acts["Act A"]["views"], 150)
        self.assertEqual(acts["Act A"]["collab_views"], 50)
        self.assertEqual(acts["Act B"]["views"], 50)
        self.assertEqual(acts["Act B"]["collab_views"], 0)
        self.assertEqual(sum(act["views"] for act in stats["acts"]), 200)


if __name__ == "__main__":
    unittest.main()

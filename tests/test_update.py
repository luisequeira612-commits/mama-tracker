import unittest
from scripts.update import build_stats, load_videos, percentage_tenths



class ReferenceInventoryTests(unittest.TestCase):
    def test_inventory_matches_reference_video_and_act_counts(self):
        entries = load_videos()
        self.assertEqual(len(entries), 69)
        self.assertEqual(len({entry["id"] for entry in entries}), 69)
        self.assertEqual(len({entry["key"] for entry in entries}), 26)

    def test_taeyang_shared_stage_is_credited_to_bigbang(self):
        entries = load_videos()
        shared = next(entry for entry in entries if entry["id"] == "FGBnglnOBsE")
        self.assertEqual(shared["artist"], "BIGBANG")
        self.assertFalse(shared["collab"])

class PercentageRoundingTests(unittest.TestCase):
    def test_rounded_act_percentages_sum_to_exactly_100_percent(self):
        views = [
            3276144, 1727374, 1679461, 1539092, 1282683, 1175802,
            870796, 801314, 560389, 336703, 306134, 217357, 85684, 49987,
        ]
        shares = percentage_tenths(views, sum(views))
        self.assertEqual(sum(shares), 1000)
        self.assertEqual(shares[0], 235)

    def test_collaboration_percentages_also_sum_to_exactly_100_percent(self):
        views = [1766268, 585287, 541842, 126975, 201979, 509030, 85524, 206760]
        shares = percentage_tenths(views, sum(views))
        self.assertEqual(sum(shares), 1000)

    def test_zero_total_returns_zero_shares(self):
        self.assertEqual(percentage_tenths([10, 20], 0), [0, 0])


class ArtistViewsGrowthTests(unittest.TestCase):
    def test_growth_is_aggregated_by_artist_and_normalized_to_one_hour(self):
        from datetime import datetime, timezone, timedelta
        from scripts.update import calculate_artist_growth
        now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
        history = {"snapshots": [{
            "captured_at": (now - timedelta(minutes=50)).isoformat().replace("+00:00", "Z"),
            "views": {"AAAAAAAAAAA": 1000, "BBBBBBBBBBB": 500, "CCCCCCCCCCC": 200},
        }]}
        entries = [
            {"id": "AAAAAAAAAAA", "artist": "Act A", "key": "act a"},
            {"id": "BBBBBBBBBBB", "artist": "Act A", "key": "act a"},
            {"id": "CCCCCCCCCCC", "artist": "Act B", "key": "act b"},
        ]
        found = {
            "AAAAAAAAAAA": {"views": 1500},
            "BBBBBBBBBBB": {"views": 750},
            "CCCCCCCCCCC": {"views": 250},
        }
        growth = calculate_artist_growth(history, entries, found, now)
        self.assertEqual(growth, {"act a": 900, "act b": 60})

    def test_growth_waits_for_a_valid_baseline(self):
        from datetime import datetime, timezone, timedelta
        from scripts.update import calculate_artist_growth
        now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
        history = {"snapshots": [{
            "captured_at": (now - timedelta(minutes=30)).isoformat().replace("+00:00", "Z"),
            "views": {"AAAAAAAAAAA": 100},
        }]}
        growth = calculate_artist_growth(
            history,
            [{"id": "AAAAAAAAAAA", "artist": "Act", "key": "act"}],
            {"AAAAAAAAAAA": {"views": 200}},
            now,
        )
        self.assertIsNone(growth)


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
        self.assertNotIn("hours_since_start_text", stats)
        self.assertRegex(stats["updated_kst_text"], r"^\d{1,2} [A-Z][a-z]{2} at \d{2}:\d{2} KST$")


if __name__ == "__main__":
    unittest.main()

from datetime import date, timedelta
from unittest.mock import patch
from django.test import SimpleTestCase, RequestFactory
from quit_smoking_webapp.helpers import (
    calculate_ranking_score,
    assign_places,
    is_htmx,
    get_ranking_week_range,
    AVG_POINTS_CEILING,
    CONSISTENCY_DAYS_CAP,
)


class CalculateRankingScoreTest(SimpleTestCase):
    def test_zero_days_returns_zeros(self):
        score, ratio = calculate_ranking_score(0, 0, 0)
        self.assertEqual(score, 0.0)
        self.assertEqual(ratio, 0.0)

    def test_all_smoke_free_no_cigarettes(self):
        score, ratio = calculate_ranking_score(0.0, 7, 7)
        self.assertEqual(ratio, 100.0)
        expected = round(60 + 30 + (7 / CONSISTENCY_DAYS_CAP * 10), 2)
        self.assertAlmostEqual(score, expected, places=2)

    def test_no_smoke_free_days_gives_zero_ratio(self):
        _, ratio = calculate_ranking_score(0.0, 0, 7)
        self.assertEqual(ratio, 0.0)

    def test_avg_above_ceiling_clamped_to_zero_points(self):
        score, _ = calculate_ranking_score(25.0, 0, 7)
        expected = round(0 + 0 + (7 / CONSISTENCY_DAYS_CAP * 10), 2)
        self.assertAlmostEqual(score, expected, places=2)

    def test_consistency_capped_at_30_days(self):
        score_30, _ = calculate_ranking_score(0.0, 30, 30)
        score_60, _ = calculate_ranking_score(0.0, 60, 60)
        self.assertEqual(score_30, score_60)

    def test_partial_smoke_free_ratio(self):
        _, ratio = calculate_ranking_score(0.0, 5, 10)
        self.assertEqual(ratio, 50.0)


class AssignPlacesTest(SimpleTestCase):
    def _entry(self, score, smoke_free_ratio, avg_daily, eligible=True):
        return {
            "score": score,
            "smoke_free_ratio": smoke_free_ratio,
            "avg_daily_cigarettes": avg_daily,
            "eligible": eligible,
            "place": None,
        }

    def test_unique_scores_get_sequential_places(self):
        ranking = [
            self._entry(90, 100, 0),
            self._entry(80, 80, 2),
            self._entry(70, 60, 5),
        ]
        result = assign_places(ranking)
        self.assertEqual(result[0]["place"], 1)
        self.assertEqual(result[1]["place"], 2)
        self.assertEqual(result[2]["place"], 3)

    def test_tied_scores_share_place_with_skip(self):
        ranking = [
            self._entry(90, 100, 0),
            self._entry(90, 100, 0),
            self._entry(80, 80, 2),
        ]
        result = assign_places(ranking)
        self.assertEqual(result[0]["place"], 1)
        self.assertEqual(result[1]["place"], 1)
        self.assertEqual(result[2]["place"], 3)

    def test_ineligible_entry_gets_no_place(self):
        ranking = [self._entry(90, 100, 0, eligible=False)]
        result = assign_places(ranking)
        self.assertIsNone(result[0]["place"])

    def test_empty_ranking_returns_empty(self):
        self.assertEqual(assign_places([]), [])


class IsHtmxTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_htmx_header_true_returns_true(self):
        request = self.factory.get("/", HTTP_HX_REQUEST="true")
        self.assertTrue(is_htmx(request))

    def test_no_htmx_header_returns_false(self):
        request = self.factory.get("/")
        self.assertFalse(is_htmx(request))

    def test_htmx_header_false_string_returns_false(self):
        request = self.factory.get("/", HTTP_HX_REQUEST="false")
        self.assertFalse(is_htmx(request))


class GetRankingWeekRangeTest(SimpleTestCase):
    @patch("quit_smoking_webapp.helpers.timezone.localdate")
    def test_monday_returns_previous_full_week(self, mock_date):
        mock_date.return_value = date(2026, 4, 20)  
        week_start, week_end = get_ranking_week_range()
        self.assertEqual(week_end, date(2026, 4, 19))   
        self.assertEqual(week_start, date(2026, 4, 13))  

    @patch("quit_smoking_webapp.helpers.timezone.localdate")
    def test_sunday_returns_current_week(self, mock_date):
        mock_date.return_value = date(2026, 4, 19)  
        week_start, week_end = get_ranking_week_range()
        self.assertEqual(week_end, date(2026, 4, 19))
        self.assertEqual(week_start, date(2026, 4, 13))

    @patch("quit_smoking_webapp.helpers.timezone.localdate")
    def test_week_range_is_always_6_day_span(self, mock_date):
        for offset in range(7):
            mock_date.return_value = date(2026, 4, 13) + timedelta(days=offset)
            week_start, week_end = get_ranking_week_range()
            self.assertEqual((week_end - week_start).days, 6)

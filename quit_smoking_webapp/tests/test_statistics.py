from decimal import Decimal
from datetime import datetime, time
from django.test import SimpleTestCase, TestCase
from django.contrib.auth.models import User
from quit_smoking_webapp.models import (
    UserProfile,
    CravingLevel,
    DailyLog,
    DailyLogEmotion,
    DailyLogSituation,
    Emotion,
    Situation,
)
from quit_smoking_webapp.statistics_helpers import (
    craving_label_from_avg,
    get_consumption_stats,
    get_emotion_stats,
    get_trigger_stats,
)


class CravingLabelFromAvgTest(SimpleTestCase):
    def test_none_returns_dash(self):
        self.assertEqual(craving_label_from_avg(None), "-")

    def test_zero_returns_dash(self):
        self.assertEqual(craving_label_from_avg(0), "-")

    def test_2_5_or_above_returns_high(self):
        self.assertEqual(craving_label_from_avg(2.5), "High")
        self.assertEqual(craving_label_from_avg(3.0), "High")

    def test_between_1_5_and_2_5_returns_medium(self):
        self.assertEqual(craving_label_from_avg(1.5), "Medium")
        self.assertEqual(craving_label_from_avg(2.4), "Medium")

    def test_below_1_5_returns_low(self):
        self.assertEqual(craving_label_from_avg(1.0), "Low")
        self.assertEqual(craving_label_from_avg(1.49), "Low")


class GetConsumptionStatsNoLogsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("statsuser", password="pass")

    def test_no_logs_returns_default_values(self):
        stats = get_consumption_stats(self.user)
        self.assertEqual(stats["total_cigarettes"], 0)
        self.assertEqual(stats["avg_per_day"], 0)
        self.assertEqual(stats["cigarettes_today"], "-")
        self.assertEqual(stats["first_cigarette_today"], "-")
        self.assertEqual(stats["craving_today"], "-")
        self.assertFalse(stats["has_today_log"])

    def test_no_logs_returns_empty_chart_data(self):
        stats = get_consumption_stats(self.user)
        import json
        self.assertEqual(json.loads(stats["consumption_labels_json"]), [])
        self.assertEqual(json.loads(stats["consumption_values_json"]), [])

    def test_no_logs_streak_is_zero(self):
        stats = get_consumption_stats(self.user)
        summary = {card["title"]: card["value"] for card in stats["summary_cards"]}
        self.assertEqual(summary["Current Streak"], "0")
        self.assertEqual(summary["Longest Smoke-Free Streak"], "0")


class GetConsumptionStatsWithLogsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("logstats", password="pass")
        self.craving_low = CravingLevel.objects.create(name="low")
        self.craving_high = CravingLevel.objects.create(name="high")
        self.profile = UserProfile.objects.create(
            user=self.user,
            cigarettes_per_day=20,
            pack_price=Decimal("15.00"),
            reason_to_quit="Health",
        )

    def _create_log(self, cigarettes, smoke_free, craving=None):
        return DailyLog.objects.create(
            user=self.user,
            cigarettes_smoked=cigarettes,
            smoke_free_day=smoke_free,
            craving_level=craving or self.craving_low,
        )

    def test_total_cigarettes_summed_correctly(self):
        self._create_log(10, False)
        self._create_log(5, False)
        stats = get_consumption_stats(self.user)
        self.assertEqual(stats["total_cigarettes"], 15)

    def test_smoke_free_log_does_not_increase_cigarettes(self):
        self._create_log(0, True)
        stats = get_consumption_stats(self.user)
        self.assertEqual(stats["total_cigarettes"], 0)

    def test_summary_card_smoke_free_days_counted(self):
        self._create_log(0, True)
        self._create_log(5, False)
        stats = get_consumption_stats(self.user)
        summary = {card["title"]: card["value"] for card in stats["summary_cards"]}
    
        self.assertEqual(summary["Total Smoke-Free Days"], "0")

    def test_has_today_log_is_true_when_log_exists(self):
        self._create_log(5, False)
        stats = get_consumption_stats(self.user)
        self.assertTrue(stats["has_today_log"])
        self.assertEqual(stats["cigarettes_today"], 5)


class GetEmotionStatsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("emostats", password="pass")
        self.craving = CravingLevel.objects.create(name="low")

    def test_no_logs_returns_dashes(self):
        stats = get_emotion_stats(self.user)
        self.assertEqual(stats["most_frequent_emotion_today"], "-")
        self.assertEqual(stats["most_frequent_emotion_week"], "-")
        self.assertEqual(stats["most_frequent_emotion_month"], "-")
        self.assertEqual(stats["top_3_emotions"], ["-", "-", "-"])

    def test_with_standard_emotion_counted(self):
        emotion = Emotion.objects.create(name="Stress")
        log = DailyLog.objects.create(
            user=self.user,
            cigarettes_smoked=5,
            smoke_free_day=False,
            craving_level=self.craving,
        )
        DailyLogEmotion.objects.create(daily_log=log, emotion=emotion)

        stats = get_emotion_stats(self.user)
        import json
        labels = json.loads(stats["emotion_labels_json"])
        self.assertIn("Stress", labels)

    def test_with_custom_emotion_counted(self):
        log = DailyLog.objects.create(
            user=self.user,
            cigarettes_smoked=5,
            smoke_free_day=False,
            craving_level=self.craving,
        )
        DailyLogEmotion.objects.create(daily_log=log, custom_emotion="Anxiety")

        stats = get_emotion_stats(self.user)
        import json
        labels = json.loads(stats["emotion_labels_json"])
        self.assertIn("Anxiety", labels)


class GetTriggerStatsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("trigstats", password="pass")
        self.craving = CravingLevel.objects.create(name="low")

    def test_no_logs_returns_dashes(self):
        stats = get_trigger_stats(self.user)
        self.assertEqual(stats["most_frequent_trigger_today"], "-")
        self.assertEqual(stats["top_3_triggers"], ["-", "-", "-"])

    def test_known_trigger_returns_specific_advice(self):
        situation = Situation.objects.create(name="Stress")
        log = DailyLog.objects.create(
            user=self.user,
            cigarettes_smoked=5,
            smoke_free_day=False,
            craving_level=self.craving,
        )
        DailyLogSituation.objects.create(daily_log=log, situation=situation)

        stats = get_trigger_stats(self.user)
        self.assertNotEqual(stats["trigger_advice"], "")
        self.assertIn("stress", stats["trigger_advice"].lower())

    def test_unknown_trigger_returns_default_advice(self):
        log = DailyLog.objects.create(
            user=self.user,
            cigarettes_smoked=5,
            smoke_free_day=False,
            craving_level=self.craving,
        )
        DailyLogSituation.objects.create(daily_log=log, custom_situation="UnknownTrigger")

        stats = get_trigger_stats(self.user)
        self.assertIn("Notice", stats["trigger_advice"])

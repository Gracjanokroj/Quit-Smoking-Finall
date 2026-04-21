import json
from collections import Counter
from django.utils import timezone
from datetime import timedelta
from quit_smoking_webapp.models import DailyLog, UserProfile, DailyLogEmotion, DailyLogSituation

def craving_label_from_avg(value):
        if not value:
            return "-"
        if value >= 2.5:
            return "High"
        if value >= 1.5:
            return "Medium"
        return "Low"

def get_consumption_stats(user):
    logs = DailyLog.objects.filter(user=user).select_related("craving_level").order_by("created_at")

    grouped_by_day = {}

    craving_map = {
        "low": 1,
        "medium": 2,
        "high": 3,
    }

    for log in logs:
        day = log.created_at.date()

        if day not in grouped_by_day:
            grouped_by_day[day] = {
                "cigarettes_sum": 0,
                "smoke_free": True,
                "first_cigarette_time": None,
                "craving_values": [],
                "log_ids": [],
            }

        grouped_by_day[day]["cigarettes_sum"] += log.cigarettes_smoked
        grouped_by_day[day]["log_ids"].append(log.id)

        if not log.smoke_free_day:
            grouped_by_day[day]["smoke_free"] = False

        if log.first_cigarette_time:
            current_first = grouped_by_day[day]["first_cigarette_time"]

            if current_first is None or log.first_cigarette_time < current_first:
                grouped_by_day[day]["first_cigarette_time"] = log.first_cigarette_time

        craving_name = ""
        if log.craving_level and log.craving_level.name:
            craving_name = log.craving_level.name.strip().lower()

        if craving_name in craving_map:
            grouped_by_day[day]["craving_values"].append(craving_map[craving_name])

    sorted_days = sorted(grouped_by_day.keys())
    total_days = len(grouped_by_day)

    total_cigarettes = 0
    for day in grouped_by_day:
        total_cigarettes += grouped_by_day[day]["cigarettes_sum"]

    today = timezone.localdate()
    cigarettes_today = "-"
    first_cigarette_today = "-"
    craving_today = "-"
    has_today_log = today in grouped_by_day

    if has_today_log:
        cigarettes_today = grouped_by_day[today]["cigarettes_sum"]

        if grouped_by_day[today]["first_cigarette_time"]:
            first_cigarette_today = grouped_by_day[today]["first_cigarette_time"].strftime("%H:%M")

        today_cravings = grouped_by_day[today]["craving_values"]
        
        if today_cravings:
            craving_today = round(sum(today_cravings) / len(today_cravings), 2)

    avg_per_day = 0
    if total_days > 0:
        avg_per_day = round(total_cigarettes / total_days, 2)

    last_7_days = sorted_days[-7:]
    last_30_days = sorted_days[-30:]

    avg_last_7 = 0
    if len(last_7_days) > 0:
        last_7_total = 0

        for day in last_7_days:
            last_7_total += grouped_by_day[day]["cigarettes_sum"]

        avg_last_7 = round(last_7_total / len(last_7_days), 2)

    avg_last_30 = 0
    if len(last_30_days) > 0:
        last_30_total = 0

        for day in last_30_days:
            last_30_total += grouped_by_day[day]["cigarettes_sum"]

        avg_last_30 = round(last_30_total / len(last_30_days), 2)

    consumption_labels = [d.strftime("%A") for d in last_7_days] # do zmiany
    consumption_values = [grouped_by_day[d]["cigarettes_sum"] for d in last_7_days] # do zmiany

    craving_last_7_values = []

    for d in last_7_days:
        day_cravings = grouped_by_day[d]["craving_values"]

        if day_cravings:
            craving_avg = sum(day_cravings) / len(day_cravings)
            craving_last_7_values.append(craving_avg)

    gauge_value = 0

    if len(craving_last_7_values) > 0:
        gauge_sum = 0

        for value in craving_last_7_values:
            gauge_sum += value

        gauge_value = round(gauge_sum / len(craving_last_7_values), 2)

    month_days = sorted_days[-28:]
    weekly_buckets = [0, 0, 0, 0]

    for index, day in enumerate(month_days):
        week_index = min(index // 7, 3)
        weekly_buckets[week_index] += grouped_by_day[day]["cigarettes_sum"]

    monthly_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
    monthly_values = weekly_buckets

    first_cigarette_week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
    first_cigarette_week_values = []

    for week_idx in range(4):
        start_index = week_idx * 7
        end_index = (week_idx + 1) * 7
        week_slice = month_days[start_index:end_index]
        hours = []

        for d in week_slice:
            first_time = grouped_by_day[d]["first_cigarette_time"]

            if first_time:
                hours.append(first_time.hour + first_time.minute / 60)

        if hours:
            first_cigarette_week_values.append(round(sum(hours) / len(hours), 2))
        else:
            first_cigarette_week_values.append(0)

    smoke_free_days = 0
    for day_data in grouped_by_day.values():
        if day_data["smoke_free"]:
            smoke_free_days += 1

    smoking_days = total_days - smoke_free_days

    profile = UserProfile.objects.filter(user=user).first()

    pack_price = 0
    baseline_cigarettes_per_day = 0

    if profile:
        if profile.pack_price:
            pack_price = float(profile.pack_price)

        if profile.cigarettes_per_day:
            baseline_cigarettes_per_day = profile.cigarettes_per_day

    estimated_saved = 0
    cumulative_savings = []
    cumulative_labels = []
    running_total = 0
    cigarettes_avoided = 0

    if baseline_cigarettes_per_day and pack_price:
        pack_size = 20

        for d in sorted_days:
            actual = grouped_by_day[d]["cigarettes_sum"]
            saved_cigarettes = max(baseline_cigarettes_per_day - actual, 0)
            saved_money = (saved_cigarettes / pack_size) * pack_price

            cigarettes_avoided += saved_cigarettes
            running_total += saved_money

            cumulative_labels.append(d.strftime("%d %b"))
            cumulative_savings.append(round(running_total, 2))

        estimated_saved = round(running_total, 2)

    current_smoke_free_streak = 0
    for d in reversed(sorted_days):
        if grouped_by_day[d]["smoke_free"]:
            current_smoke_free_streak += 1
        else:
            break

    longest_smoke_free_streak = 0
    current_streak = 0
    for d in sorted_days:
        if grouped_by_day[d]["smoke_free"]:
            current_streak += 1
            longest_smoke_free_streak = max(longest_smoke_free_streak, current_streak)
        else:
            current_streak = 0

    all_craving_values = []
    for d in sorted_days:
        all_craving_values.extend(grouped_by_day[d]["craving_values"])

    average_craving_level = 0
    if len(all_craving_values) > 0:
        craving_sum = 0
        for value in all_craving_values:
            craving_sum += value
        average_craving_level = round(craving_sum / len(all_craving_values), 2)

    average_craving_label = craving_label_from_avg(average_craving_level)

    log_ids = [log.id for log in logs]
    emotion_counter = Counter()
    situation_counter = Counter()

    if log_ids:
        emotion_rows = DailyLogEmotion.objects.filter(
            daily_log_id__in=log_ids
        ).select_related("emotion")

        situation_rows = DailyLogSituation.objects.filter(
            daily_log_id__in=log_ids
        ).select_related("situation")

        for row in emotion_rows:
            if row.emotion:
                emotion_counter[row.emotion.name] += 1
            elif row.custom_emotion:
                emotion_counter[row.custom_emotion] += 1

        for row in situation_rows:
            if row.situation:
                situation_counter[row.situation.name] += 1
            elif row.custom_situation:
                situation_counter[row.custom_situation] += 1

    most_common_emotion = "-"
    if emotion_counter:
        most_common_emotion = emotion_counter.most_common(1)[0][0]

    most_frequent_trigger = "-"
    if situation_counter:
        most_frequent_trigger = situation_counter.most_common(1)[0][0]

    average_craving_subtitle = "No craving data yet"
    if average_craving_level:
        average_craving_subtitle = f"Average score: {average_craving_level}"

    summary_cards = [
        {
            "title": "Total Money Saved",
            "value": f"£{estimated_saved:.2f}",
            "subtitle": "Since you started logging",
        },
        {
            "title": "Current Streak",
            "value": str(current_smoke_free_streak),
            "subtitle": "Smoke-free days in a row",
        },
        {
            "title": "Longest Smoke-Free Streak",
            "value": str(longest_smoke_free_streak),
            "subtitle": "Your best streak",
        },
        {
            "title": "Total Smoke-Free Days",
            "value": str(smoke_free_days),
            "subtitle": "All tracked days",
        },
        {
            "title": "Cigarettes Avoided",
            "value": str(cigarettes_avoided),
            "subtitle": "Compared to your baseline",
        },
        {
            "title": "Most Common Emotion",
            "value": most_common_emotion,
            "subtitle": "From all logs",
        },
        {
            "title": "Most Frequent Trigger",
            "value": most_frequent_trigger,
            "subtitle": "Most common situation",
        },
        {
            "title": "Average Craving Level",
            "value": average_craving_label,
            "subtitle": average_craving_subtitle,
        },
    ]

    return {
        "total_cigarettes": total_cigarettes,
        "cigarettes_today": cigarettes_today,
        "first_cigarette_today": first_cigarette_today,
        "craving_today": craving_today,
        "has_today_log": has_today_log,

        "avg_per_day": avg_per_day,
        "avg_last_7": avg_last_7,
        "avg_last_30": avg_last_30,
        "gauge_value": gauge_value,
        "estimated_saved": estimated_saved,

        "summary_cards": summary_cards,

        "consumption_labels_json": json.dumps(consumption_labels),
        "consumption_values_json": json.dumps(consumption_values),

        "monthly_labels_json": json.dumps(monthly_labels),
        "monthly_values_json": json.dumps(monthly_values),

        "first_cigarette_week_labels_json": json.dumps(first_cigarette_week_labels),
        "first_cigarette_week_values_json": json.dumps(first_cigarette_week_values),

        "smoke_free_days_json": json.dumps(smoke_free_days),
        "smoking_days_json": json.dumps(smoking_days),

        "cumulative_labels_json": json.dumps(cumulative_labels),
        "cumulative_savings_json": json.dumps(cumulative_savings),
    }


def get_emotion_stats(user):
    logs = DailyLog.objects.filter(user=user).order_by("created_at")
    log_ids = list(logs.values_list("id", flat=True))

    emotions_qs = DailyLogEmotion.objects.filter(
        daily_log_id__in=log_ids
    ).select_related("emotion", "daily_log")

    overall_counter = Counter()
    today_counter = Counter()
    week_counter = Counter()
    month_counter = Counter()

    today = timezone.localdate()
    week_start = today - timedelta(days=6)
    month_start = today - timedelta(days=29)

    for item in emotions_qs:
        if item.emotion:
            emotion_name = item.emotion.name
        elif item.custom_emotion:
            emotion_name = item.custom_emotion
        else:
            continue

        log_day = item.daily_log.created_at.date()

        overall_counter[emotion_name] += 1

        if log_day == today:
            today_counter[emotion_name] += 1

        if week_start <= log_day <= today:
            week_counter[emotion_name] += 1

        if month_start <= log_day <= today:
            month_counter[emotion_name] += 1

    top_3_emotions = []
    for name, count in overall_counter.most_common(3):
        top_3_emotions.append(name)

    while len(top_3_emotions) < 3:
        top_3_emotions.append("-")

    most_frequent_emotion_today = "-"
    if today_counter:
        most_frequent_emotion_today = today_counter.most_common(1)[0][0]

    most_frequent_emotion_week = "-"
    if week_counter:
        most_frequent_emotion_week = week_counter.most_common(1)[0][0]

    most_frequent_emotion_month = "-"
    if month_counter:
        most_frequent_emotion_month = month_counter.most_common(1)[0][0]

    emotion_labels = list(overall_counter.keys())
    emotion_values = list(overall_counter.values())

    return {
        "top_3_emotions": top_3_emotions,
        "most_frequent_emotion_today": most_frequent_emotion_today,
        "most_frequent_emotion_week": most_frequent_emotion_week,
        "most_frequent_emotion_month": most_frequent_emotion_month,
        "emotion_labels_json": json.dumps(emotion_labels),
        "emotion_values_json": json.dumps(emotion_values),
    }

def get_trigger_stats(user):
    logs = DailyLog.objects.filter(user=user).order_by("created_at")
    log_ids = list(logs.values_list("id", flat=True))

    situations_qs = DailyLogSituation.objects.filter(
        daily_log_id__in=log_ids
    ).select_related("situation", "daily_log")

    overall_counter = Counter()
    today_counter = Counter()
    week_counter = Counter()
    month_counter = Counter()

    today = timezone.localdate()
    week_start = today - timedelta(days=6)
    month_start = today - timedelta(days=29)

    for item in situations_qs:
        if item.situation:
            situation_name = item.situation.name
        elif item.custom_situation:
            situation_name = item.custom_situation
        else:
            continue

        log_day = item.daily_log.created_at.date()

        overall_counter[situation_name] += 1

        if log_day == today:
            today_counter[situation_name] += 1

        if week_start <= log_day <= today:
            week_counter[situation_name] += 1

        if month_start <= log_day <= today:
            month_counter[situation_name] += 1

    top_3_triggers = [name for name, _ in overall_counter.most_common(3)] # do zmiany

    while len(top_3_triggers) < 3:
        top_3_triggers.append("-")

    most_frequent_trigger_today = "-"
    if today_counter:
        most_frequent_trigger_today = today_counter.most_common(1)[0][0]

    most_frequent_trigger_week = "-"
    if week_counter:
        most_frequent_trigger_week = week_counter.most_common(1)[0][0]

    most_frequent_trigger_month = "-"
    if month_counter:
        most_frequent_trigger_month = month_counter.most_common(1)[0][0]

    trigger_labels = list(overall_counter.keys())
    trigger_values = list(overall_counter.values())

    top_trigger = None
    if overall_counter:
        top_trigger = overall_counter.most_common(1)[0][0]

    advice_map = {
        "After meal": "Try replacing the post-meal cigarette with a short walk, gum, or drinking water right after eating.",
        "Coffee": "If coffee is a strong trigger, change your routine for a few days: drink it in a different place or switch temporarily to tea.",
        "Stress": "When stress hits, delay smoking by 10 minutes and do one calming action first: deep breathing, stretching, or stepping away.",
        "Driving": "Keep your hands busy while driving, such as using gum or a bottle of water, and remove cigarettes from the car.",
        "Party": "Before social events, prepare a plan: stay near non-smokers, hold a drink in your hand, and decide how you will refuse a cigarette.",
        "Watching TV": "Pair TV time with a replacement habit like herbal tea, sunflower seeds, or squeezing a stress ball.",
        "At work": "Break the automatic work-smoke loop by taking a non-smoking break: stand up, walk, or drink water instead.",
        "With coffee": "Try changing the place or time of your coffee and immediately pair it with a non-smoking substitute.",
    }

    trigger_advice = advice_map.get(
        top_trigger,
        "Notice the situations where you smoke most often and prepare one replacement action for each of them before the craving starts."
    )

    return {
        "top_3_triggers": top_3_triggers,
        "most_frequent_trigger_today": most_frequent_trigger_today,
        "most_frequent_trigger_week": most_frequent_trigger_week,
        "most_frequent_trigger_month": most_frequent_trigger_month,
        "trigger_labels_json": json.dumps(trigger_labels),
        "trigger_values_json": json.dumps(trigger_values),
        "trigger_advice": trigger_advice,
    }
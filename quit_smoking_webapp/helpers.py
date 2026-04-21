from django.utils import timezone
from datetime import timedelta

MIN_DAYS_REQUIRED = 5
AVG_POINTS_CEILING = 20
CONSISTENCY_DAYS_CAP = 30

def is_htmx(request):
    return request.headers.get("HX-Request") == "true"

def calculate_ranking_score(avg_daily_cigarettes, smoke_free_days, days_count):
    if days_count == 0:
        return 0.0, 0.0

    smoke_free_ratio = smoke_free_days / days_count

    smoke_free_points = smoke_free_ratio * 60

    avg_left = AVG_POINTS_CEILING - avg_daily_cigarettes

    if avg_left < 0:
        avg_left = 0

    avg_points = (avg_left / AVG_POINTS_CEILING) * 30

    counted_days = days_count
    if counted_days > CONSISTENCY_DAYS_CAP:
        counted_days = CONSISTENCY_DAYS_CAP

    consistency_points = (counted_days / CONSISTENCY_DAYS_CAP) * 10

    score = smoke_free_points + avg_points + consistency_points
    smoke_free_ratio_percent = smoke_free_ratio * 100

    return round(score, 2), round(smoke_free_ratio_percent, 1)


def assign_places(ranking):
    last_key = None
    current_place = 0

    for index, entry in enumerate(ranking, start=1):
        if not entry["eligible"]:
            entry["place"] = None
            continue

        current_key = (
            entry["score"],
            entry["smoke_free_ratio"],
            entry["avg_daily_cigarettes"],
        )

        if current_key != last_key:
            current_place = index

        entry["place"] = current_place
        last_key = current_key

    return ranking

def get_ranking_week_range():
    today = timezone.localdate()
    weekday = today.weekday()  

    if weekday == 6:
        week_end = today
        week_start = today - timedelta(days=6)
    else:
        days_since_last_sunday = weekday + 1
        week_end = today - timedelta(days=days_since_last_sunday)
        week_start = week_end - timedelta(days=6)

    return week_start, week_end
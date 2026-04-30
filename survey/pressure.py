import json
import logging
import urllib.parse
import urllib.request
from datetime import date

from django.utils import timezone

from .models import Pressure

ZAGREB_LAT = 45.8150
ZAGREB_LON = 15.9819
HOURS = (7, 12, 17)
COLUMNS = ("p_morning", "p_noon", "p_evening")

logger = logging.getLogger(__name__)


def ensure_pressure_for_dates(dates):
    """Fetch and cache MSL pressure at 07/12/17 local time for the given dates.

    Skips dates that are in the future or already fully populated. Idempotent.
    Fails silently on network/API errors so the calling page still renders.
    """
    today = timezone.localdate()
    targets = []
    existing = {p.date: p for p in Pressure.objects.filter(date__in=list(dates))}
    for d in dates:
        if d > today:
            continue
        p = existing.get(d)
        if p is None or not p.is_complete():
            targets.append(d)
    if not targets:
        return

    earliest = min(targets)
    past_days = (today - earliest).days
    if past_days < 0:
        return
    past_days = min(past_days, 92)  # forecast endpoint cap

    params = {
        "latitude": ZAGREB_LAT,
        "longitude": ZAGREB_LON,
        "hourly": "pressure_msl",
        "timezone": "Europe/Zagreb",
        "past_days": past_days,
        "forecast_days": 1,
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            payload = json.loads(resp.read())
    except Exception as exc:
        logger.warning("Open-Meteo fetch failed: %s", exc)
        return

    times = payload.get("hourly", {}).get("time", [])
    pressures = payload.get("hourly", {}).get("pressure_msl", [])

    by_date = {}
    for t, p in zip(times, pressures):
        if p is None:
            continue
        date_part, time_part = t.split("T")
        d = date.fromisoformat(date_part)
        hour = int(time_part.split(":")[0])
        by_date.setdefault(d, {})[hour] = p

    target_set = set(targets)
    for d, by_hour in by_date.items():
        if d not in target_set:
            continue
        defaults = {col: by_hour.get(h) for col, h in zip(COLUMNS, HOURS)}
        Pressure.objects.update_or_create(date=d, defaults=defaults)

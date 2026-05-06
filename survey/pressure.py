import json
import logging
import math
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


def _prevailing_direction(dirs_speeds):
    """Speed-weighted vector mean of meteorological wind directions.

    Wind direction is the direction *from* which the wind blows (deg, 0=N, 90=E).
    """
    u = v = 0.0
    for deg, spd in dirs_speeds:
        if deg is None or spd is None:
            continue
        rad = math.radians(deg)
        u += spd * math.sin(rad)
        v += spd * math.cos(rad)
    if u == 0 and v == 0:
        return None
    return (math.degrees(math.atan2(u, v)) + 360) % 360


def ensure_pressure_for_dates(dates):
    """Fetch and cache MSL pressure (07/12/17 local) and prevailing wind direction.

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
        "hourly": "pressure_msl,wind_direction_10m,wind_speed_10m",
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

    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    pressures = hourly.get("pressure_msl", [])
    wind_dirs = hourly.get("wind_direction_10m", [])
    wind_spds = hourly.get("wind_speed_10m", [])

    pressure_by_date = {}
    wind_by_date = {}
    for i, t in enumerate(times):
        date_part, time_part = t.split("T")
        d = date.fromisoformat(date_part)
        hour = int(time_part.split(":")[0])
        p = pressures[i] if i < len(pressures) else None
        if p is not None:
            pressure_by_date.setdefault(d, {})[hour] = p
        wd = wind_dirs[i] if i < len(wind_dirs) else None
        ws = wind_spds[i] if i < len(wind_spds) else None
        wind_by_date.setdefault(d, []).append((wd, ws))

    target_set = set(targets)
    for d in target_set:
        by_hour = pressure_by_date.get(d, {})
        defaults = {col: by_hour.get(h) for col, h in zip(COLUMNS, HOURS)}
        defaults["wind_direction"] = _prevailing_direction(wind_by_date.get(d, []))
        if all(v is None for v in defaults.values()):
            continue
        Pressure.objects.update_or_create(date=d, defaults=defaults)

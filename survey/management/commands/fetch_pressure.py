from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from survey.data import EXPERIMENT_DAYS, EXPERIMENT_START
from survey.models import Pressure
from survey.pressure import ensure_pressure_for_dates


class Command(BaseCommand):
    help = "Fetch and cache Zagreb atmospheric pressure for experiment dates."

    def handle(self, *args, **options):
        start = datetime.strptime(EXPERIMENT_START, "%Y-%m-%d").date()
        dates = {start + timedelta(days=i) for i in range(EXPERIMENT_DAYS)}
        dates.update(Pressure.objects.values_list("date", flat=True))
        ensure_pressure_for_dates(sorted(dates))
        self.stdout.write(self.style.SUCCESS("Pressure data refreshed."))

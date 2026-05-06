from django.db import models


DEPRESSION_ITEMS = (3, 5, 10, 13, 16, 17, 21)
ANXIETY_ITEMS = (2, 4, 7, 9, 15, 19, 20)
STRESS_ITEMS = (1, 6, 8, 11, 12, 14, 18)

# Lovibond & Lovibond cutoffs (already multiplied by 2 for DASS-21).
SEVERITY_BANDS = {
    "depression": [(9, "Normalno"), (13, "Blago"), (20, "Umjereno"), (27, "Teško"), (1000, "Izrazito teško")],
    "anxiety":    [(7, "Normalno"), (9, "Blago"),  (14, "Umjereno"), (19, "Teško"), (1000, "Izrazito teško")],
    "stress":     [(14, "Normalno"), (18, "Blago"), (25, "Umjereno"), (33, "Teško"), (1000, "Izrazito teško")],
}


def severity(scale, score):
    for upper, label in SEVERITY_BANDS[scale]:
        if score <= upper:
            return label
    return "Izrazito teško"


CARDINAL_POINTS = (
    "S", "SSI", "SI", "ISI", "I", "IJI", "JI", "JJI",
    "J", "JJZ", "JZ", "ZJZ", "Z", "ZSZ", "SZ", "SSZ",
)


def cardinal(deg):
    """Convert degrees (meteorological, from-direction) to a 16-point Croatian compass label."""
    if deg is None:
        return None
    idx = int((deg % 360) / 22.5 + 0.5) % 16
    return CARDINAL_POINTS[idx]


class Pressure(models.Model):
    date = models.DateField(unique=True)
    p_morning = models.FloatField(null=True, blank=True)  # 07:00 local
    p_noon = models.FloatField(null=True, blank=True)     # 12:00 local
    p_evening = models.FloatField(null=True, blank=True)  # 17:00 local
    wind_direction = models.FloatField(null=True, blank=True)  # prevailing, degrees (meteorological)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("date",)

    def __str__(self):
        return f"P({self.date}) {self.p_morning}/{self.p_noon}/{self.p_evening}"

    def is_complete(self):
        return all(
            v is not None
            for v in (self.p_morning, self.p_noon, self.p_evening, self.wind_direction)
        )

    def wind_cardinal(self):
        return cardinal(self.wind_direction)


class Response(models.Model):
    person = models.CharField(max_length=64)
    date = models.DateField()

    q1 = models.PositiveSmallIntegerField()
    q2 = models.PositiveSmallIntegerField()
    q3 = models.PositiveSmallIntegerField()
    q4 = models.PositiveSmallIntegerField()
    q5 = models.PositiveSmallIntegerField()
    q6 = models.PositiveSmallIntegerField()
    q7 = models.PositiveSmallIntegerField()
    q8 = models.PositiveSmallIntegerField()
    q9 = models.PositiveSmallIntegerField()
    q10 = models.PositiveSmallIntegerField()
    q11 = models.PositiveSmallIntegerField()
    q12 = models.PositiveSmallIntegerField()
    q13 = models.PositiveSmallIntegerField()
    q14 = models.PositiveSmallIntegerField()
    q15 = models.PositiveSmallIntegerField()
    q16 = models.PositiveSmallIntegerField()
    q17 = models.PositiveSmallIntegerField()
    q18 = models.PositiveSmallIntegerField()
    q19 = models.PositiveSmallIntegerField()
    q20 = models.PositiveSmallIntegerField()
    q21 = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("person", "date")
        ordering = ("-date", "person")

    def __str__(self):
        return f"{self.person} @ {self.date}"

    def answers(self):
        return [getattr(self, f"q{i}") for i in range(1, 22)]

    def _subscale(self, items):
        return sum(getattr(self, f"q{i}") for i in items) * 2

    def depression(self):
        return self._subscale(DEPRESSION_ITEMS)

    def anxiety(self):
        return self._subscale(ANXIETY_ITEMS)

    def stress(self):
        return self._subscale(STRESS_ITEMS)

    def scores(self):
        d, a, s = self.depression(), self.anxiety(), self.stress()
        return {
            "depression": {"score": d, "severity": severity("depression", d)},
            "anxiety": {"score": a, "severity": severity("anxiety", a)},
            "stress": {"score": s, "severity": severity("stress", s)},
        }

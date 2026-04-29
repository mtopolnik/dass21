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

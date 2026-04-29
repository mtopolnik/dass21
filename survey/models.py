from django.db import models


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

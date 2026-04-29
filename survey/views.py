from datetime import datetime, timedelta

from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .data import (
    EXPERIMENT_DAYS,
    EXPERIMENT_START,
    PEOPLE,
    PEOPLE_BY_NAME,
    questions_for,
)
from .models import Response


def _experiment_dates():
    start = datetime.strptime(EXPERIMENT_START, "%Y-%m-%d").date()
    return [start + timedelta(days=i) for i in range(EXPERIMENT_DAYS)]


def _get_person(name):
    person = PEOPLE_BY_NAME.get(name)
    if person is None:
        raise Http404("Unknown person")
    return person


def _parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as exc:
        raise Http404("Invalid date") from exc


def home(request):
    return render(request, "survey/home.html", {"people": PEOPLE})


def calendar(request, person):
    _get_person(person)
    today = timezone.localdate()
    dates = _experiment_dates()
    filled = set(
        Response.objects.filter(person=person, date__in=dates).values_list(
            "date", flat=True
        )
    )
    entries = []
    for d in dates:
        entries.append(
            {
                "date": d,
                "iso": d.isoformat(),
                "is_today": d == today,
                "is_future": d > today,
                "is_filled": d in filled,
            }
        )
    return render(
        request,
        "survey/calendar.html",
        {"person": person, "today": today, "entries": entries},
    )


def questionnaire(request, person, date_str):
    person_obj = _get_person(person)
    d = _parse_date(date_str)
    if d not in _experiment_dates():
        raise Http404("Date outside experiment range")

    today = timezone.localdate()
    if d > today:
        return render(
            request,
            "survey/too_early.html",
            {"person": person, "date": d, "today": today},
        )

    questions_text = questions_for(person_obj["sex"])
    instance = Response.objects.filter(person=person, date=d).first()

    def build_questions(selected_map):
        return [
            {"num": i, "text": questions_text[i - 1], "selected": selected_map.get(i)}
            for i in range(1, 22)
        ]

    if request.method == "POST":
        values = {}
        errors = []
        selected_map = {}
        for i in range(1, 22):
            raw = request.POST.get(f"question_{i}")
            if raw in (None, ""):
                errors.append(i)
                continue
            try:
                v = int(raw)
            except ValueError:
                errors.append(i)
                continue
            if v < 0 or v > 3:
                errors.append(i)
                continue
            values[f"q{i}"] = v
            selected_map[i] = v

        if errors:
            return render(
                request,
                "survey/questionnaire.html",
                {
                    "person": person,
                    "date": d,
                    "questions": build_questions(selected_map),
                    "errors": errors,
                    "is_edit": instance is not None,
                },
            )

        if instance:
            for k, v in values.items():
                setattr(instance, k, v)
            instance.save()
        else:
            Response.objects.create(person=person, date=d, **values)

        return redirect(reverse("calendar", args=[person]))

    selected_map = {}
    if instance:
        for i in range(1, 22):
            selected_map[i] = getattr(instance, f"q{i}")

    return render(
        request,
        "survey/questionnaire.html",
        {
            "person": person,
            "date": d,
            "questions": build_questions(selected_map),
            "errors": [],
            "is_edit": instance is not None,
        },
    )

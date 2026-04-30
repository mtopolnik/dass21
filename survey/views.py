import csv
from datetime import datetime, timedelta

from django.http import Http404, HttpResponse
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
from .models import Pressure, Response
from .pressure import ensure_pressure_for_dates


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


def results(request, person):
    _get_person(person)
    responses = Response.objects.filter(person=person).order_by("date")

    ensure_pressure_for_dates(_experiment_dates())
    pressure_by_date = {p.date: p for p in Pressure.objects.all()}

    rows = []
    d_scores = []
    a_scores = []
    s_scores = []
    for r in responses:
        sc = r.scores()
        rows.append({"date": r.date, "scores": sc, "pressure": pressure_by_date.get(r.date)})
        d_scores.append(sc["depression"]["score"])
        a_scores.append(sc["anxiety"]["score"])
        s_scores.append(sc["stress"]["score"])

    averages = None
    if rows:
        from .models import severity as _sev
        avg_d = sum(d_scores) / len(d_scores)
        avg_a = sum(a_scores) / len(a_scores)
        avg_s = sum(s_scores) / len(s_scores)
        averages = {
            "depression": {"score": round(avg_d, 1), "severity": _sev("depression", avg_d)},
            "anxiety": {"score": round(avg_a, 1), "severity": _sev("anxiety", avg_a)},
            "stress": {"score": round(avg_s, 1), "severity": _sev("stress", avg_s)},
        }

    return render(
        request,
        "survey/results.html",
        {"person": person, "rows": rows, "averages": averages},
    )


def export_csv(request):
    ensure_pressure_for_dates(_experiment_dates())
    pressure_by_date = {p.date: p for p in Pressure.objects.all()}

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="dass21_export.csv"'
    writer = csv.writer(response)
    header = ["person", "sex", "date", "submitted_at", "updated_at"]
    header += ["depression", "anxiety", "stress"]
    header += ["pressure_07", "pressure_12", "pressure_17"]
    header += [f"q{i}" for i in range(1, 22)]
    writer.writerow(header)

    for r in Response.objects.all().order_by("person", "date"):
        person = PEOPLE_BY_NAME.get(r.person)
        sex = person["sex"] if person else ""
        p = pressure_by_date.get(r.date)
        submitted_at = timezone.localtime(r.created_at).isoformat(timespec="seconds")
        updated_at = timezone.localtime(r.updated_at).isoformat(timespec="seconds")
        row = [r.person, sex, r.date.isoformat(), submitted_at, updated_at]
        row += [r.depression(), r.anxiety(), r.stress()]
        row += [
            p.p_morning if p else "",
            p.p_noon if p else "",
            p.p_evening if p else "",
        ]
        row += [getattr(r, f"q{i}") for i in range(1, 22)]
        writer.writerow(row)

    return response


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

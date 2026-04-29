from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("export.csv", views.export_csv, name="export_csv"),
    path("p/<str:person>/", views.calendar, name="calendar"),
    path("p/<str:person>/results/", views.results, name="results"),
    path("p/<str:person>/<str:date_str>/", views.questionnaire, name="questionnaire"),
]

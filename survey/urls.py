from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("p/<str:person>/", views.calendar, name="calendar"),
    path("p/<str:person>/<str:date_str>/", views.questionnaire, name="questionnaire"),
]

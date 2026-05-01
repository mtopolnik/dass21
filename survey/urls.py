from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),
    path("admin-home/", views.admin_home, name="admin_home"),
    path("export.csv", views.export_csv, name="export_csv"),
    path("p/<str:person>/", views.calendar, name="calendar"),
    path("p/<str:person>/results/", views.results, name="results"),
    path("p/<str:person>/<str:date_str>/", views.questionnaire, name="questionnaire"),
]

from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.hub, name="hub"),
    path("automations/", include("automations.urls")),
]

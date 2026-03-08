from django.urls import path
from . import views

urlpatterns = [
    path("eventbrite-mailchimp/", views.eb_mc_import, name="eb_mc_import"),
    path("eventbrite-mailchimp-unsubscribe/", views.eb_mc_unsubscribe, name="eb_mc_unsubscribe"),
]

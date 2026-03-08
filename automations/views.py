import requests as http_requests
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from . import services


@require_http_methods(["GET", "POST"])
def eb_mc_import(request):
    context = {"title": "Eventbrite → Mailchimp", "icon": "🎟️"}

    if request.method == "POST":
        event_id = request.POST.get("event_id", "").strip()
        context["event_id"] = event_id

        if not event_id:
            context["error"] = "Please enter an Eventbrite Event ID."
            return render(request, "automations/eb_mc_import.html", context)

        # Check API keys configured
        if not services.EVENTBRITE_API_TOKEN or not services.MAILCHIMP_API_KEY or not services.MAILCHIMP_LIST_ID:
            context["error"] = "Missing API credentials. Please set EVENTBRITE_API_TOKEN, MAILCHIMP_API_KEY, and MAILCHIMP_LIST_ID in your .env file."
            return render(request, "automations/eb_mc_import.html", context)

        try:
            event = services.get_eventbrite_event(event_id)
            context["event_name"] = event.get("name", {}).get("text", event_id)
            results = services.sync_attendees_to_mailchimp(event_id)
            context["results"] = results
        except http_requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                context["error"] = f"Event '{event_id}' not found on Eventbrite. Check the Event ID."
            elif e.response is not None and e.response.status_code == 401:
                context["error"] = "Eventbrite authentication failed. Check your EVENTBRITE_API_TOKEN."
            else:
                context["error"] = f"Eventbrite API error: {e}"
        except Exception as e:
            context["error"] = f"Unexpected error: {e}"

    return render(request, "automations/eb_mc_import.html", context)


@require_http_methods(["GET", "POST"])
def eb_mc_unsubscribe(request):
    context = {"title": "Eventbrite Unsubscribe → Mailchimp", "icon": "🔕"}

    if request.method == "POST":
        event_id = request.POST.get("event_id", "").strip()
        confirmed = request.POST.get("confirmed") == "yes"
        context["event_id"] = event_id

        if not event_id:
            context["error"] = "Please enter an Eventbrite Event ID."
            return render(request, "automations/eb_mc_unsubscribe.html", context)

        if not services.EVENTBRITE_TOKEN or not services.MAILCHIMP_API_KEY or not services.MAILCHIMP_LIST_ID:
            context["error"] = "Missing API credentials. Please set EVENTBRITE_API_TOKEN, MAILCHIMP_API_KEY, and MAILCHIMP_LIST_ID in your .env file."
            return render(request, "automations/eb_mc_unsubscribe.html", context)

        try:
            event = services.get_eventbrite_event(event_id)
            context["event_name"] = event.get("name", {}).get("text", event_id)

            if not confirmed:
                # Preview step: fetch attendees and show a confirmation
                attendees = services.get_eventbrite_attendees(event_id)
                emails = [
                    a.get("profile", {}).get("email", "")
                    for a in attendees
                    if a.get("profile", {}).get("email")
                ]
                context["preview_emails"] = emails
                context["preview_count"] = len(emails)
            else:
                # Confirmed: execute unsubscribe
                results = services.unsubscribe_attendees_from_mailchimp(event_id)
                context["results"] = results

        except http_requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                context["error"] = f"Event '{event_id}' not found on Eventbrite. Check the Event ID."
            elif e.response is not None and e.response.status_code == 401:
                context["error"] = "Eventbrite authentication failed. Check your EVENTBRITE_API_TOKEN."
            else:
                context["error"] = f"Eventbrite API error: {e}"
        except Exception as e:
            context["error"] = f"Unexpected error: {e}"

    return render(request, "automations/eb_mc_unsubscribe.html", context)

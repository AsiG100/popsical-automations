from django.shortcuts import render


AUTOMATIONS = [
    {
        "id": "eventbrite-mailchimp-import",
        "title": "Eventbrite → Mailchimp Import",
        "description": "Export event attendees from Eventbrite and sync them as subscribers into a Mailchimp audience.",
        "icon": "🎟️",
        "url": "/automations/eventbrite-mailchimp/",
        "tags": ["eventbrite", "mailchimp", "audience", "sync", "email"],
        "status": "active",
    },
    {
        "id": "eventbrite-mailchimp-unsubscribe",
        "title": "Eventbrite → Mailchimp Unsubscribe",
        "description": "Unsubscribe attendees that asked to be excluded from the mailing list.",
        "icon": "🔕",
        "url": "/automations/eventbrite-mailchimp-unsubscribe/",
        "tags": ["eventbrite", "mailchimp", "unsubscribe", "email"],
        "status": "active",
    },
]


def hub(request):
    return render(request, "hub/hub.html", {"automations": AUTOMATIONS})

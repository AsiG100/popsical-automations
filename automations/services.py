import os
import math
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

EVENTBRITE_API_TOKEN = os.environ.get("EVENTBRITE_API_TOKEN", "")
MAILCHIMP_API_KEY = os.environ.get("MAILCHIMP_API_KEY", "")
MAILCHIMP_LIST_ID = os.environ.get("MAILCHIMP_LIST_ID", "")


def _mailchimp_dc():
    """Extract data center from Mailchimp API key (e.g. 'us1' from 'key-us1')."""
    if "-" in MAILCHIMP_API_KEY:
        return MAILCHIMP_API_KEY.split("-")[-1]
    return "us1"


def _mailchimp_auth():
    return ("anystring", MAILCHIMP_API_KEY)


def _mailchimp_base():
    return f"https://{_mailchimp_dc()}.api.mailchimp.com/3.0"


# ── Eventbrite ────────────────────────────────────────────────────────────────

def get_eventbrite_attendees(event_id: str) -> list[dict]:
    """Fetch all attendees for an Eventbrite event (handles pagination)."""
    attendees = []
    page = 1
    while True:
        url = f"https://www.eventbriteapi.com/v3/events/{event_id}/attendees/"
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {EVENTBRITE_API_TOKEN}"},
            params={"page": page},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        attendees.extend(data.get("attendees", []))
        pagination = data.get("pagination", {})
        if pagination.get("page_number", 1) >= pagination.get("page_count", 1):
            break
        page += 1
    return attendees


def get_eventbrite_event(event_id: str) -> dict:
    """Fetch basic event info."""
    url = f"https://www.eventbriteapi.com/v3/events/{event_id}/"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {EVENTBRITE_API_TOKEN}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


# ── Mailchimp ─────────────────────────────────────────────────────────────────

def _subscriber_hash(email: str) -> str:
    return hashlib.md5(email.lower().encode()).hexdigest()


def upsert_mailchimp_member(email: str, first_name: str, last_name: str) -> dict:
    """Add or update a Mailchimp subscriber (subscribed status)."""
    url = f"{_mailchimp_base()}/lists/{MAILCHIMP_LIST_ID}/members/{_subscriber_hash(email)}"
    payload = {
        "email_address": email,
        "status_if_new": "subscribed",
        "merge_fields": {"FNAME": first_name, "LNAME": last_name},
    }
    resp = requests.put(url, json=payload, auth=_mailchimp_auth(), timeout=10)
    return {"email": email, "status_code": resp.status_code, "ok": resp.ok, "body": resp.json()}


def unsubscribe_mailchimp_member(email: str) -> dict:
    """Set a Mailchimp member's status to unsubscribed."""
    url = f"{_mailchimp_base()}/lists/{MAILCHIMP_LIST_ID}/members/{_subscriber_hash(email)}"
    payload = {"status": "unsubscribed"}
    resp = requests.patch(url, json=payload, auth=_mailchimp_auth(), timeout=10)
    return {"email": email, "status_code": resp.status_code, "ok": resp.ok}


# ── High-level operations ─────────────────────────────────────────────────────

def sync_attendees_to_mailchimp(event_id: str) -> dict:
    """
    Fetch all Eventbrite attendees and upsert them into Mailchimp.
    Returns a summary dict.
    """
    attendees = get_eventbrite_attendees(event_id)
    results = {"total": len(attendees), "success": 0, "errors": [], "skipped": 0}

    for a in attendees:
        profile = a.get("profile", {})
        email = profile.get("email", "").strip()
        if not email:
            results["skipped"] += 1
            continue
        first = profile.get("first_name", "")
        last = profile.get("last_name", "")
        res = upsert_mailchimp_member(email, first, last)
        if res["ok"]:
            results["success"] += 1
        else:
            results["errors"].append({"email": email, "detail": res["body"].get("detail", "Unknown error")})

    return results


def unsubscribe_attendees_from_mailchimp(event_id: str) -> dict:
    """
    Fetch all Eventbrite attendees and unsubscribe them from Mailchimp.
    Returns a summary dict.
    """
    attendees = get_eventbrite_attendees(event_id)
    results = {"total": len(attendees), "success": 0, "errors": [], "skipped": 0}

    for a in attendees:
        profile = a.get("profile", {})
        email = profile.get("email", "").strip()
        if not email:
            results["skipped"] += 1
            continue
        res = unsubscribe_mailchimp_member(email)
        if res["ok"]:
            results["success"] += 1
        else:
            results["errors"].append({"email": email, "status_code": res["status_code"]})

    return results

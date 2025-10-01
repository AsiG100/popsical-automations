import os
import requests
from flask import Flask, redirect, url_for, session, render_template, request, flash
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecret")

google_blueprint = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
)
app.register_blueprint(google_blueprint, url_prefix="/login")


app.config["AUTHORIZED_EMAILS"] = [
    "popsical.test@gmail.com",
]


@app.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    email = resp.json()["email"]

    if email not in app.config["AUTHORIZED_EMAILS"]:
        return "<h1>You are not authorized to access this application.</h1>"

    return render_template("hub.html")

@app.route("/purge-cache", methods=["GET", "POST"])
def purge_cache():
    if not google.authorized:
        return redirect(url_for("google.login"))

    if request.method == "POST":
        url_to_purge = request.form.get("url")
        if not url_to_purge:
            flash("Please enter a URL to purge.", "error")
        else:
            try:
                cloudflare_api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
                cloudflare_zone_id = os.environ.get("CLOUDFLARE_ZONE_ID")

                headers = {
                    "Authorization": f"Bearer {cloudflare_api_token}",
                    "Content-Type": "application/json",
                }
                data = {"files": [url_to_purge]}
                response = requests.post(
                    f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone_id}/purge_cache",
                    headers=headers,
                    json=data,
                )
                response.raise_for_status()
                flash(f"Successfully purged cache for: {url_to_purge}", "success")
            except requests.exceptions.RequestException as e:
                flash(f"Error purging cache: {e}", "error")

    return render_template("purge_cache.html")


if __name__ == "__main__":
    app.run(debug=True)
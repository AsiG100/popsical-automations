# popsical-automations

A hub for Popsical's business automations.

## Docker

Build the image locally:

```bash
docker build -t popsical-automations:local .
```

Run with Docker:

```bash
docker run --rm -p 8000:8000 popsical-automations:local
```

Or use docker-compose (recommended for development):

```bash
docker-compose up --build
```

The app will be available at http://localhost:8000/

Notes:

- The repository's `requirements.txt` is used to install Python dependencies.
- The container runs the Flask development server; for production use a WSGI server (gunicorn/uvicorn) behind a reverse proxy.
# popsical-automations
A hub for Popsical's business automations

FROM python:3.11-slim

WORKDIR /app

# Install runtime deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=popsical.settings

EXPOSE 8000

# Collect static files and run gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn popsical.wsgi:application --bind 0.0.0.0:8000 --workers 2"]

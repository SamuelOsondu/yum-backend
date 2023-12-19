#!/usr/bin/env bash
# exit on error
set -o errexit

# Install project dependencies using pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# cache table
python manage.py createcachetable

# Apply database migrations
python manage.py migrate



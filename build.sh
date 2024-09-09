#!/usr/bin/env basn
# Exit on error
set -o errexit

# Modify this line as needed for pack age manager (pie, poetry, etc.)
pip install -r requirements.txt

#Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python nanage.py migrate
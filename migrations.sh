#!/bin/bash

# Set default message or use user input
MESSAGE=${1:-"fix schema"}

# Get the path to the last migration file
LAST_MIGRATION=$(ls -t alembic/versions/*.py | head -n 1)

if [ -f "$LAST_MIGRATION" ]; then
    echo "Deleting last migration: $LAST_MIGRATION"
    rm "$LAST_MIGRATION"
else
    echo "No existing migration found to delete."
fi

# Regenerate migration
echo "Generating new migration: \"$MESSAGE\""
alembic revision --autogenerate -m "$MESSAGE"
alembic upgrade head

python seed_dev_data.py

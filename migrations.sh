#!/bin/bash

set -e

MESSAGE=${1:-"fix schema"}
ALEMBIC_DIR="./alembic/versions"
DB_NAME=$(grep DATABASE_URL .env | sed -E 's|.*/(.*)\?.*|\1|')
SA_PASSWORD="MySecure@123"  # Make sure this matches docker-compose.yml
MSSQL_CONTAINER="timesheet-mssql"

echo "========================================"
echo "🔄 Step 0: Stopping and wiping previous SQL container"
echo "========================================"
docker-compose down -v || echo "No container running."

echo "========================================"
echo "🚀 Step 1: Starting fresh SQL Server container"
echo "========================================"
docker-compose up -d
sleep 10

echo "========================================"
echo "🧠 Step 2: Checking if database \"$DB_NAME\" exists"
echo "========================================"

docker run --rm --network oracle_copy_default mcr.microsoft.com/mssql-tools /opt/mssql-tools/bin/sqlcmd -S timesheet-mssql -U sa -P 'MySecure@123' -Q "IF DB_ID('$DB_NAME') IS NULL CREATE DATABASE [$DB_NAME];"

echo "========================================"
echo "🧹 Step 3: Cleaning old migrations"
echo "========================================"
if [ -d "$ALEMBIC_DIR" ]; then
    rm -f $ALEMBIC_DIR/*.py
    echo "✅ Deleted previous migration files"
else
    echo "⚠️  No alembic/versions directory found"
fi

echo "========================================"
echo "🛠️ Step 4: Generating new migration: \"$MESSAGE\""
echo "========================================"

alembic revision --autogenerate -m "$MESSAGE"

echo "========================================"
echo "⏫ Step 5: Applying migrations"
echo "========================================"
alembic upgrade head

echo "========================================"
echo "🌱 Step 6: Seeding database"
echo "========================================"
python seed_dev_data.py

echo "✅ DONE! Database created, schema migrated, and data seeded."

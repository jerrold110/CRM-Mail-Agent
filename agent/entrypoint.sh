#!/bin/sh
set -e

echo "Waiting for database to be ready..."

python app/memory_setup.py

exec fastapi run app/api_entrypoint.py 

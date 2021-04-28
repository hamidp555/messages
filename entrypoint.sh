#!/usr/bin/env bash
set -e

echo "Running messages webservice"
/usr/local/bin/gunicorn -b 0.0.0.0:80 --access-logfile - --error-logfile - wsgi
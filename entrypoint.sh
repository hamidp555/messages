#!/usr/bin/env bash
set -e

while true; do
    flask db upgrade 
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Migation failed, retrying in 5 secs...
    sleep 5
done

echo "Running messages webservice"
/usr/local/bin/gunicorn -b 0.0.0.0:80 --access-logfile - --error-logfile - wsgi
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
/usr/local/bin/gunicorn -w 2 -b 0.0.0.0:80 wsgi --timeout 300 --log-level=debug
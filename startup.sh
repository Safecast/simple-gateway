#!/bin/bash
# setup crontab -e  with:
# @reboot  /home/grafana.safecast.jp/startup.sh
# make executable with chmod +x /home/grafana.safecast.jp/startup.sh
cd /home/grafana.safecast.jp/public_html/gateway/simple-gateway/
service grafana start
python -m gunicorn -w 4 -k uvicorn.workers.UvicornWorker grafana_duckdb_api:app --bind 0.0.0.0:8000
exit
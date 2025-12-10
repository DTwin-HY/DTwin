import os


workers = int(os.environ.get("GUNICORN_PROCESSES", "2"))

timeout = 1200

graceful_timeout = 120

threads = int(os.environ.get("GUNICORN_THREADS", "4"))

bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:5000")

forwarded_allow_ips = "*"

secure_scheme_headers = {"X-Forwarded-Proto": "https"}

accesslog = "-"
errorlog = "-"
loglevel = "info"

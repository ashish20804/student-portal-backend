# gunicorn.conf.py — used automatically by gunicorn on Render
workers = 1          # Render free tier has limited RAM, 1 worker is safest
timeout = 120        # seconds before killing a worker (default is 30 — too short for SMTP)
keepalive = 5
loglevel = "info"

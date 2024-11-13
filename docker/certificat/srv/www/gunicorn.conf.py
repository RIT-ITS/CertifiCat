workers = 4
threads = 10
timeout = 60
bind = "unix:/run/certificat/gunicorn.sock"
access_log = "-"
error_log = "-"
preload_app = True

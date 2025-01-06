workers = 4
threads = 10
timeout = 60
bind = "unix:/run/certificat/gunicorn.sock"
accesslog = "-"
errorlog = "-"
preload_app = True

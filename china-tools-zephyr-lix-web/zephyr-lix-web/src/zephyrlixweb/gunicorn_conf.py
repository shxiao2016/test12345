from linkedin.web.gunicorn_defaults import *  # noqa


workers = 5
worker_class = "gevent"

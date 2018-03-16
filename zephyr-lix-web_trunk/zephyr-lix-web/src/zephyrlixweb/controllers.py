from linkedin.gunicorn.controller import WebAppController


class SimpleWebAppController(WebAppController):
    wsgi_app = 'zephyrlixweb.webapp:app'

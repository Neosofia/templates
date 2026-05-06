from core.config import settings


bind = f"0.0.0.0:{settings.port}"
workers = settings.web_concurrency
threads = settings.gunicorn_threads
timeout = settings.gunicorn_timeout
keepalive = settings.gunicorn_keepalive
accesslog = "-"
errorlog = "-"
capture_output = True
loglevel = settings.log_level
logger_class = "src.gunicorn_logger.JSONLogger"

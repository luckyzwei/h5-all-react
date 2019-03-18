import os


home_path = os.path.expandvars('$HOME')


LOGGING_CONFIG_FILE_HANDLER = dict(
    version=1,
    disable_existing_loggers=False,

    loggers={
        "root": {
            "level": "INFO",
            "handlers": ["handler"]
        },
        "tasks": {
            "level": "INFO",
            "handlers": ["tasks_handler"]
        },
        "sanic.error": {
            "level": "ERROR",
            "handlers": ["error_handler"],
            "propagate": True,
            "qualname": "sanic.error"
        },
        "sanic.access": {
            "level": "INFO",
            "handlers": ["access_handler"],
            "propagate": True,
            "qualname": "sanic.access"
        }
    },
    handlers={
        "handler": {
            "class": "logging.FileHandler",
            "formatter": "generic",
            "filename": os.path.join(home_path, "logs/gpet_info.log"),
            "encoding": "utf-8"
        },
        "tasks_handler": {
            "class": "logging.FileHandler",
            "formatter": "generic",
            "filename": os.path.join(home_path, "logs/gpet_tasks.log"),
            "encoding": "utf-8"
        },
        "error_handler": {
            "class": "logging.FileHandler",
            "formatter": "generic",
            "filename": os.path.join(home_path, "logs/gpet_error.log"),
            "encoding": "utf-8"
        },
        "access_handler": {
            "class": "logging.FileHandler",
            "formatter": "access",
            "filename": os.path.join(home_path, "logs/gpet_access.log"),
            "encoding": "utf-8"
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        },
        "access": {
            "format": "%(asctime)s - (%(name)s)[%(levelname)s][%(host)s]: " +
                      "%(request)s %(message)s %(status)d %(byte)d",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        },
    })

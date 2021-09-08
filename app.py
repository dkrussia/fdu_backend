from pprint import pprint

import uvicorn
from core.config import settings

logging_config = uvicorn.config.LOGGING_CONFIG

logging_config["disable_existing_loggers"] = True
logging_config["formatters"]["error_formatter"] = {
    '()': 'logging.Formatter',
    'fmt': '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
}


logging_config['handlers']['error_file_handler'] = {
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': 'logs/main.log',
    'maxBytes': 1 * 1024 * 1024,
    'backupCount': 10,
    'mode': 'a',
    'formatter': 'error_formatter',
}

logging_config["loggers"]["uvicorn.error"]['handlers'] = ['error_file_handler']

if __name__ == "__main__":
    uvicorn.run('app.main:app',
                host=settings.HOST,
                port=settings.PORT,
                use_colors=True,
                reload = settings.RELOAD_SERVER,
                )

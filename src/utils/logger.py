import sys
from loguru import logger
from pathlib import Path
from datetime import datetime

from config.settings import LOGS_DIR


log_file = LOGS_DIR / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logger.remove()


logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)

logger.add(
    log_file,
    rotation="500 MB",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)
logger.info(f"Logs enregistrés: {log_file.name}")

def get_logger():
    """
    Nom        : get_logger
    Input      : aucun
    Output     : logger - instance loguru configurée
    Description: Retourne le logger configuré pour le projet
    """
    return logger
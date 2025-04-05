import os
import sys

from loguru import logger
from config import Config

logger.remove()
logger.add(sys.stderr, level=Config().get_log_level())
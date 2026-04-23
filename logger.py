# logger.py
from os import getenv
from path import get_logger_path, get_logs_path
import logging.config
from json import load

def setup_logger() -> None:
    env = getenv("ENV", "prod")
    config_path = get_logger_path(env)
    
    with open(config_path, "r") as f:
        config = load(f)
    
    logging.config.dictConfig(config)
    root_logger = logging.getLogger()
    
    handler = logging.FileHandler(get_logs_path())
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    
    root_logger.addHandler(handler)

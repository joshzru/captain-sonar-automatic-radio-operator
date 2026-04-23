# main.py
import pygame as pg
import logging

from config import AppConfig
from core import GameManager
from logger import setup_logger


def main():

    setup_logger()
    log = logging.getLogger(__name__)
    
    log.info("pygame initialized")
    pg.init()
    
    manager: GameManager = GameManager(AppConfig.fetch())

    manager.run()
    log.info("Game terminated\n")

if __name__ == "__main__":
    main()

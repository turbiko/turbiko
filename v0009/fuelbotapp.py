"""
FuelBot v0009 20.06.2020
"""

from configs.configtools import Config
from tgtools.tgbot import TGBot


def main():
    config = Config()
    telegram_bot = TGBot(config.get())
    telegram_bot.bot_start()


if __name__ == '__main__':
    main()

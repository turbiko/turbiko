"""
inline keyboard creation. keyboard as menu
Levels of menu (in callback) defined by index position
0 - top-level command
1 - next-level after top, etc
this rule for parsing menu levels
"""
import logging
from functools import wraps
# from python-telegram-bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async, CallbackContext
from telegram import InlineKeyboardMarkup, Update, InlineKeyboardButton
# from this project
from gstools.gsutils import get_all_data, write_to_doc, decode_commands, find_and_modify_cell_by_other_cell_value
from telegram import InlineKeyboardButton
from configs.constans import *
import filmdevstrings.fortgmenus as tg_str
import datetime












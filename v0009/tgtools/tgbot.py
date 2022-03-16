""" v0008
FuelTicketsBot main part. Class and top-level functions
"""
import logging
from functools import wraps
# from python-telegram-bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async, CallbackContext
from telegram import InlineKeyboardMarkup, Update, InlineKeyboardButton
from telegram import InlineKeyboardButton
# from this project
from gstools.gsutils import get_all_data, write_to_doc, decode_commands, find_and_modify_cell_by_other_cell_value
from configs.constans import *
import filmdevstrings.fortgmenus as tg_str
import datetime


class TGBot:
    def __init__(self, cfg):
        self.config = cfg
        self.tg_admins = [263255207, 297360613, 421392418, 696626950, 297360613, 158450093, 429032923, 340851561]
        self.tg_drivers = [1270451600]
        self.users = []
        self.users = self.tg_admins + self.tg_drivers
        logging.basicConfig(filename='bot.log',
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.updater = Updater(self.config.get('telegram', 'bot_token'), use_context=True)
        self.dp = self.updater.dispatcher
        self.message_handler = MessageHandler(Filters.text, self.chat_text_processor)
        self.current_menu_command = START_MENU
        self.tickets = []
        self.drivers = []
        self.projects = []
        self.all_data = {"Tickets": [], "Drivers": [], "Projects":[]}  # all workbook data
        self.update_data()
        self.process_all_data()

    def update_data(self):  # get source data from GSheet document
        self.all_data = get_all_data('telegram-filmfuel')  # {"Tickets": [], "Drivers": [], "Projects":[]}
        # print('update_data => now we get all data ')

    def process_all_data(self):  # from source data create dictionaries for each data type
        print('self.tickets:')
        for id, ticket in enumerate(self.all_data["Tickets"]):
            ticket_status = FREE_
            if ticket[7]:
                if ticket[8]:
                    ticket_status = CLOSED_
                else:
                    ticket_status = BUSY_
            add_tickets = {'id': id,
                           'created': ticket[0],
                           'seller': ticket[1],
                           'fuel': ticket[2],
                           'litres': ticket[3],
                           'price': ticket[5],
                           'ticket_num': ticket[6],
                           'driver': ticket[7],
                           'close_date': ticket[8],
                           'status': ticket_status}
            self.tickets.append(add_tickets)
            # print(add_tickets)
        print('self.drivers:')
        for id, add_driver in enumerate(self.all_data["Drivers"]):
            the_driver = {'id': id,
                          'driver_name': add_driver[0],
                          'project': add_driver[1],
                          'telegram_id':add_driver[2]}
            self.drivers.append(the_driver)
            # print(the_driver)
        print('self.projects:')
        for id, add_project in enumerate(self.all_data["Projects"]):
            the_project = {'id': id,
                           'project_name': add_project[0]}
            self.projects.append(the_project)
            print(the_project)
        print('process_all_data => data NOW recalculated')

    def help(self, update: Update, context: CallbackContext):
        reply_markup = InlineKeyboardMarkup(self.get_inline_buttons())
        update.message.reply_text('Сброс и возврат в начало команда /start\n',
                                  reply_markup=reply_markup)

    def error(self, bot, update, error):
        import traceback
        self.logger.warning('Update "%s" caused error "%s"' % (update, error))
        traceback.print_exc()

    def restricted(func):
        @wraps(func)
        def wrapped(self, update, context, *args, **kwargs):
            # print(update)
            user_id = update.effective_user.id
            user_name = update.effective_user.name
            if user_id not in self.users:
                print((user_id not in self.users), (user_id not in self.tg_drivers))
                print("  Unauthorized access denied for {}.".format(user_id))
                self.logger.info("Unauthorized access denied for {}.{}".format(user_id, user_name))
                return
            return func(self, update, context, *args, **kwargs)  #

        return wrapped

    @restricted
    def start(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        user = update.message.from_user
        self.logger.warning('user  "%s"."%s" start interact with Bot', user_id, user.username)
        welcome_text = f" {BOT_VERSION} \nПриветствуем Вас, {update.effective_user.name}\n Талонов в базе:  {len(self.tickets)}\n проектов: {len(self.projects)}\n водителей: {len(self.drivers)} "
        # update.message.reply_text(BOT_VERSION + ' \nПриветствует Вас, ' + update.effective_user.name)
        reply_markup = InlineKeyboardMarkup(self.get_inline_buttons(tg_user_id=user_id))
        update.message.reply_text(welcome_text + '\nСброс и возврат в начало команда /start\n',
                                  reply_markup=reply_markup)

    @run_async
    def button_pressed(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        driver_name = ''
        print(f'user_id:{user_id}, Drivers: {self.tg_drivers}')
        for tg_drv in self.tg_drivers:
            if user_id == tg_drv:
                for driver in self.drivers:
                    print(driver)
                    if driver['telegram_id'] == str(user_id):
                        driver_name = driver['driver_name']
                        print("----driver['driver_name'] = ", driver_name)
                        break
        query = update.callback_query
        self.current_menu_command = query.data
        inline_markup = self.get_inline_buttons(query.data, tg_user_id=user_id)
        reply_markup = InlineKeyboardMarkup(inline_markup)
        # print('button_pressed => query.data: ', query.data, '\n', inline_markup)
        modify_message_text = query.data
        if TICKETS in self.current_menu_command:
            modify_message_text = "Талоны" + query.data
            if LIST_ in self.current_menu_command:
                # print('button_pressed => if LIST_ in self.current_menu_command:')
                modify_message_text = 'Список талонов '
                if (A95 in self.current_menu_command) or (DIZEL in self.current_menu_command) or (
                        GAZ in self.current_menu_command):
                    fuel_type = decode_commands(self.current_menu_command.split(';')[-1])
                    index1 = 0
                    for index, ticket in enumerate(self.tickets):
                        if index1 > 20:
                            modify_message_text += '\n' + ' output > 20 '
                            break
                        if user_id in self.tg_drivers:
                            if (ticket['driver'] == driver_name) and (ticket['status'] != FREE_):
                                if (ticket['fuel'] == fuel_type) and (ticket['status'] in self.current_menu_command):
                                    index1 += 1
                                    # print('\n' + ticket['created'] + ' ' + ticket['ticket_num'] + ' ' + ticket['driver'] + '' +
                                    #       ticket['close_date'])

                                    modify_message_text += '\n' + ticket['created'] + ' ' + ticket['fuel'] + ' ' + ticket['litres'] + 'л. ' + ticket['ticket_num'] + ' ' + ticket[
                                        'driver'] + '' + ticket['close_date']
                            else:
                                if (ticket['fuel'] == fuel_type) and (ticket['status'] in self.current_menu_command):
                                    index1 += 1
                                    # print('\n' + ticket['created'] + ' ' + ticket['ticket_num'] + ' ' + ticket['driver'] + '' +
                                    #       ticket['close_date'])

                                    modify_message_text += '\n' + ticket['created'] + ' ' + ticket['fuel'] + ' ' + \
                                                           ticket['litres'] + 'л. ' + ticket['ticket_num'] + ' ' + \
                                                           ticket[
                                                               'driver'] + '' + ticket['close_date']
                query.edit_message_text(text=modify_message_text)
        elif DRIVER in self.current_menu_command:
            if LIST_DRIVER in self.current_menu_command:
                modify_message_text = 'Список всех водителей'
                for index, driver in enumerate(self.drivers):

                    if index > 20:
                        modify_message_text += '\n' + ' output > 20 '
                        break
                    modify_message_text += '\n id:' + str(driver['id']) + ' ФИО:' + driver['driver_name'] + ' Telegram:' + driver[
                        'telegram_id'] + ' проект:' + driver['project']
        elif PROJECTS in self.current_menu_command:
            if PROJECTS == self.current_menu_command:
                modify_message_text = 'Список всех водителей \n всех проектов'
                for index, driver in enumerate(self.drivers):
                    if index > 20:
                        modify_message_text += '\n' + ' output > 20 '
                        break
                    modify_message_text += '\n id:' + str(driver['id']) + ' ФИО:' + driver[
                        'driver_name'] + ' Telegram:' + \
                                           driver[
                                               'telegram_id'] + ' проект:' + driver['project']
            else:
                modify_message_text = 'Список водителей проекта: '
                project_by_id = ''
                for prj1 in self.projects:
                    if prj1['id'] == int(self.current_menu_command.split(';')[-1]):
                        project_by_id = prj1['project_name']
                        modify_message_text+= ' ' + prj1['project_name']
                for index, driver in enumerate(self.drivers):
                    if index > 20:
                        modify_message_text += '\n' + ' output > 20 '
                        break
                    if driver['project'] == project_by_id:
                        modify_message_text += '\n id:' + str(driver['id']) + ' ФИО:' + driver['driver_name'] + ' Telegram:' +  driver['telegram_id'] + ' проект:' + driver['project']

        query.edit_message_text(text=modify_message_text, reply_markup=reply_markup)

    def get_inline_buttons(self, callback_from_inline_kb=START_MENU, tg_user_id=tg_super_admin):
        buttons_list = []
        print('get_inline_buttons => callback_from_inline_kb:', callback_from_inline_kb)
        for tg_drv in self.tg_drivers:
            if tg_user_id == tg_drv:
                for driver in self.drivers:
                    print(driver)
                    if driver['telegram_id'] == str(tg_user_id):
                        driver_name = driver['driver_name']
                        print("----driver['driver_name'] = ", driver_name)
                        break
        if callback_from_inline_kb == START_MENU:
            buttons_list = self.create_start_inline_kb(tg_user_id)
        elif TICKETS in callback_from_inline_kb.split(';')[0]:
            # print('get_inline_buttons=> elif TICKETS in callback_from_inline_kb.split(;)[0]: ', callback_from_inline_kb.split(';')[0])
            buttons_list = self.create_ticket_inline_kb(
                callback_from_inline_kb=callback_from_inline_kb,
                tg_user_id=tg_user_id,
            )
        elif DRIVER in callback_from_inline_kb.split(';')[0]:
            buttons_list = self.create_driver_inline_kb(callback_from_inline_kb)
        elif PROJECTS in callback_from_inline_kb.split(';')[0]:
            print("elif PROJECTS in callback_from_inline_kb.split(';')[0]:", callback_from_inline_kb.split(';')[0])
            buttons_list = self.create_project_inline_kb(callback_from_inline_kb)
        if not (callback_from_inline_kb == START_MENU):
            buttons_list.append([InlineKeyboardButton(tg_str.str_to_start, callback_data=START_MENU)])
        return buttons_list

    def create_start_inline_kb(self, tg_user_id=tg_super_admin):  # start inline keyboard
        """
        :return: buttons list for start menu
        """
        if tg_user_id in self.tg_admins:
            buttons_list = [[InlineKeyboardButton("Талоны", callback_data=TICKETS)],
                            [InlineKeyboardButton("Водители", callback_data=DRIVER)],
                            [InlineKeyboardButton("Проекты", callback_data=PROJECTS)]
                            ]
        elif tg_user_id in self.tg_drivers:
            buttons_list = [[InlineKeyboardButton("Талоны", callback_data=TICKETS)],
                            ]
        return buttons_list

    def create_ticket_inline_kb(self, callback_from_inline_kb=TICKETS, tg_user_id=tg_super_admin):
        """
        create menu for tickets
        :param callback_from_inline_kb:
        :return: buttons list for tickets menu
        """
        print('create_ticket_inline_kb => callback_from_inline_kb: ', callback_from_inline_kb)
        buttons_list = []
        if callback_from_inline_kb == TICKETS:
            if tg_user_id in self.tg_admins:
                buttons_list = [[InlineKeyboardButton("Добавить талоны", callback_data=TICKETS + ';' + ADD_)],
                                [InlineKeyboardButton("Список талонов", callback_data=TICKETS + ';' + LIST_)],
                                [InlineKeyboardButton("Закрыть талон", callback_data=TICKETS + ';' + CLOSE_)]
                                ]
            elif tg_user_id in self.tg_drivers:
                buttons_list = [[InlineKeyboardButton("Список талонов", callback_data=TICKETS + ';' + LIST_)],
                                [InlineKeyboardButton("Закрыть талон", callback_data=TICKETS + ';' + CLOSE_)]
                                ]
        elif callback_from_inline_kb == TICKETS + ';' + ADD_:
            print("create_ticket_inline_kb=> elif callback_from_inline_kb == TICKETS + ';' + ADD_:")
            if tg_user_id in self.tg_admins:
                buttons_list = [
                    [InlineKeyboardButton("А-95 10л", callback_data=TICKETS + ';' + ADD_ + ';' + A95 + ';' + L10),
                     InlineKeyboardButton("Дизель 10л",
                                          callback_data=TICKETS + ';' + ADD_ + ';' + A95 + ';' + L10),
                     InlineKeyboardButton("Газ 10л", callback_data=TICKETS + ';' + ADD_ + ';' + A95 + ';' + L10)],
                    [InlineKeyboardButton("А-95 20л", callback_data=TICKETS + ';' + ADD_ + ';' + A95 + ';' + L20),
                     InlineKeyboardButton("Дизель 20л",
                                          callback_data=TICKETS + ';' + ADD_ + ';' + A95 + ';' + L20),
                     InlineKeyboardButton("Газ 20л", callback_data=TICKETS + ';' + ADD_ + ';' + A95 + ';' + L20)]
                ]
            elif tg_user_id in self.tg_drivers:
                buttons_list = []

        elif callback_from_inline_kb == TICKETS + ';' + LIST_:
            print("create_ticket_inline_kb => elif callback_from_inline_kb == TICKETS + ; + LIST_:")
            buttons_list = []
            buttons_list.append([InlineKeyboardButton("свободно А-95", callback_data=TICKETS + ';' + LIST_ + ';' + FREE_ + ';' + A95),
                 InlineKeyboardButton("Дизель", callback_data=TICKETS + ';' + LIST_ + ';' + FREE_ + ';' + A95),
                 InlineKeyboardButton("Газ", callback_data=TICKETS + ';' + LIST_ + ';' + FREE_ + ';' + A95)])
            buttons_list.append([
                InlineKeyboardButton("занято А-95 ", callback_data=TICKETS + ';' + LIST_ + ';' + BUSY_ + ';' + A95),
                InlineKeyboardButton("Дизель",
                                      callback_data=TICKETS + ';' + LIST_ + ';' + BUSY_ + ';' + A95),
                InlineKeyboardButton("Газ", callback_data=TICKETS + ';' + LIST_ + ';' + BUSY_ + ';' + A95)])
            buttons_list.append([InlineKeyboardButton("Закр.  А-95 ", callback_data=TICKETS + ';' + LIST_ + ';' + CLOSED_ + ';' + A95),
                 InlineKeyboardButton("Дизель",
                                      callback_data=TICKETS + ';' + LIST_ + ';' + CLOSED_ + ';' + A95),
                 InlineKeyboardButton("Газ", callback_data=TICKETS + ';' + LIST_ + ';' + CLOSED_ + ';' + A95)])
        elif callback_from_inline_kb == TICKETS + ';' + CLOSE_:
            print("create_ticket_inline_kb => elif callback_from_inline_kb == TICKETS + ';' + CLOSE_:")
        return buttons_list

    def create_driver_inline_kb(self, callback_from_inline_kb=DRIVER, tg_user_id=tg_super_admin):
        """
        drivers buttons
        :param callback_from_inline_kb:
        :return: buttons list for drivers menu
        """
        buttons_list = []
        if callback_from_inline_kb == DRIVER:
            buttons_list = [[InlineKeyboardButton("Добавить водителя", callback_data=DRIVER + ';' + ADD_)],
                            [InlineKeyboardButton("Список водителей", callback_data=DRIVER + ';' + LIST_)],
                            [InlineKeyboardButton("Выдать талон", callback_data=DRIVER + ';' + GIVE_TIK)]
                            ]
        elif (DRIVER + ';' + ADD_) in callback_from_inline_kb:
            print('elif (DRIVER + \';\' + ADD_) in callback_from_inline_kb:', callback_from_inline_kb)
            buttons_list = [[InlineKeyboardButton("Проект 1",
                                              callback_data=ADD_DRIVER + ';' + PROJECT1),
                             InlineKeyboardButton("Проект 2",
                                              callback_data=ADD_DRIVER + ';' + PROJECT2),
                             InlineKeyboardButton("Проект 3",
                                              callback_data=ADD_DRIVER + ';' + PROJECT3)]]

        elif (DRIVER + ';' + LIST_) in callback_from_inline_kb:
            print('elif (DRIVER + \';\' + LIST_) in callback_from_inline_kb:')
        elif (DRIVER + ';' + GIVE_TIK) == callback_from_inline_kb:
            buttons_list = []
            button_text1 = ''
            print('elif (DRIVER + \';\' + GIVE_TIK) in callback_from_inline_kb:')
            for index, driver in enumerate(self.drivers):
                if index > 75:
                    modify_message_text += '\n' + ' output > 20 '
                    break
                button_text1 += ' ФИО: ' + driver['driver_name'] + ' проект: ' + driver['project']
                callback_comm1 = DRIVER + ';' + GIVE_TIK + ';' + str(driver['id'])
                buttons_list.append([InlineKeyboardButton(button_text1, callback_data=callback_comm1)])
                button_text1 = ''
        elif (DRIVER in callback_from_inline_kb) and (CLOSE_TICKETS in callback_from_inline_kb):
            print("elif (DRIVER in callback_from_inline_kb) and (CLOSE_TICKETS in callback_from_inline_kb):")
        return buttons_list

    def create_project_inline_kb(self, callback_from_inline_kb='PRJs', tg_user_id=tg_super_admin):
        buttons_list = []
        if callback_from_inline_kb == 'PRJs':
            button_text1 = ''
            callback_comm1 = ''
            # buttons_list = [[InlineKeyboardButton("Добавить проект", callback_data=PROJECTS + ';' + ADD_)],
            #                 [InlineKeyboardButton("Список проектов", callback_data=PROJECTS + ';' + LIST_)]
            #                 ]
            for proj in self.projects:
                button_text1 = str(proj['id'])+' '+proj['project_name']
                callback_comm1 = callback_from_inline_kb + ';' +  str(proj['id'])
                buttons_list.append([InlineKeyboardButton(button_text1, callback_data=callback_comm1)])
        elif PROJECTS in callback_from_inline_kb:
            print("create_project_inline_kb => elif callback_from_inline_kb == PROJECTS;ADD_:", callback_from_inline_kb)
        return buttons_list

    def chat_text_processor(self, update: Update, context: CallbackContext, tg_user_id=tg_super_admin):
        # global current_action
        self.logger.info('do_echo => повторим...' + update.message.text + ' ' + self.current_menu_command)
        chat_id = update.message.chat_id
        user_id = update.effective_user.id
        active_reply_text = update.message.text
        if TICKETS == self.current_menu_command.split(';')[0]:
            if ADD_ in self.current_menu_command:
                test_reply = write_to_doc(user_id, self.current_menu_command, active_reply_text)
                reply_text = "Добавляем талон: " + test_reply[0] + ' ' + test_reply[1]
                update.message.reply_text(text=reply_text)
            if CLOSE_ in self.current_menu_command:
                print('try to close ticket')
                found_reply = []
                for ticket in self.tickets:
                    if (BUSY_ == ticket['status']) and (active_reply_text in ticket['ticket_num']):
                        found_reply.append(ticket['ticket_num'])
                        print('Closing ticket:', ticket)
                print('found_reply: ', found_reply)
                if len(found_reply) > 1:
                    new_text_reply = ''
                    for ticket in self.tickets:
                        if ticket['ticket_num'] in found_reply:
                            new_text_reply += '\n{0} {1} {2} {3}'.format(ticket['created'], ticket['ticket_num'],
                                                                         ticket['driver'], ticket['close_date'])
                    update.message.reply_text(text=' найдено больше одного талона, уточните номер:\n' + new_text_reply)
                elif len(found_reply) == 0:
                    update.message.reply_text(
                        text=' Не найдено  выданных талонов, \n содержащих такие знаки в номере\n уточните номер:\n')
                else:
                    print('chat_text_processor => if ADD_TICKETS in self.current_menu_command: ',
                          self.current_menu_command)
                    date_for_enter = datetime.date.today().strftime("%d.%m.%Y")
                    test_reply = find_and_modify_cell_by_other_cell_value('telegram-filmfuel', 'Талоны', 6, active_reply_text,
                                             9, date_for_enter)
                    self.update_data()
                    self.process_all_data()
                    action_reply = f'Close ticket {test_reply[1]} {test_reply[2]}'
                    update.message.reply_text(text=action_reply)
        elif DRIVER == self.current_menu_command.split(';')[0]:
            if 'DRIVER;ADD;' in self.current_menu_command:
                print("chat_text_processor => if 'DRIVER;ADD;PROJECT1' == self.current_menu_command.split: ", self.current_menu_command)
                test_reply = write_to_doc(user_id, self.current_menu_command, active_reply_text)
                reply_text = "Добавляем водителя: " + test_reply[0] + ' ' + test_reply[1]
                update.message.reply_text(text=reply_text)
            elif 'DRIVER;GIVE_TIK' in self.current_menu_command:
                driver_id = int(self.current_menu_command.split(';')[-1])
                for driver1 in self.drivers:
                    if driver1['id'] == driver_id:
                        driver_name = driver1['driver_name']
                        break
                print('chat_text_processor => DRIVER;GIVE_TIK:try to give ticket')
                found_reply = []
                for ticket in self.tickets:
                    if (FREE_ == ticket['status']) and (active_reply_text in ticket['ticket_num']):
                        found_reply.append(ticket['ticket_num'])
                        print(*found_reply)
                if len(found_reply) > 1:
                    new_text_reply = ''
                    for ticket in self.tickets:
                        if ticket['ticket_num'] in found_reply:
                            new_text_reply += '\n{0} {1} {2} {3}'.format(ticket['created'], ticket['ticket_num'],
                                                                         ticket['driver'], ticket['close_date'])
                    update.message.reply_text(text=' найдено больше одного талона, уточните номер:\n' + new_text_reply)
                elif len(found_reply) == 0:
                    update.message.reply_text(
                        text=' Не найдено свободных талонов, \n содержащих такие знаки в номере\n уточните номер:\n')
                else:
                    print('chat_text_processor => if DRIVER;GIVE_TIK in self.current_menu_command: ',
                          self.current_menu_command)
                    date_for_action = datetime.date.today().strftime("%d.%m.%Y")
                    self.logger.info(date_for_action + '  отдать талон: ' + driver_name + ' талон: ' + active_reply_text)
                    test_reply = find_and_modify_cell_by_other_cell_value('telegram-filmfuel', 'Талоны', 6,
                                                                          active_reply_text,
                                                                          8, driver_name)
                    self.update_data()
                    self.process_all_data()
                    action_reply = f'Отдали талон {test_reply[1]} {test_reply[2]}'
                    update.message.reply_text(text=action_reply)
        elif PROJECT == self.current_menu_command.split(';')[0]:
            pass

    def bot_start(self):
        # Enable logging
        print('Bot start.')
        print('Bot users: ', self.users)

        # Setup bot
        self.logger.info(self.updater.bot.get_me())

        # Add commands
        self.dp.add_handler(CommandHandler(['start'], self.start))
        self.dp.add_handler(CommandHandler(['help'], self.help))

        # callback_handler for inline_menus
        self.dp.add_handler(CallbackQueryHandler(self.button_pressed))

        # text messages handler
        self.dp.add_handler(self.message_handler)

        # log all errors
        self.dp.add_error_handler(self.error)
        self.updater.start_polling()  # Start the Bot
        self.logger.info(BOT_VERSION + '  Start&Listening...')
        self.updater.idle()  # Run the bot until you press Ctrl-C or the process receives SIGINT

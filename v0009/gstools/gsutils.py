""" v0008
googledisk read-write tools
"""
# Googlesheet operations
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from configs.constans import *
import datetime

def read_from_worksheet(work_book_name, worksheet_name):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('filmdev-fuel-675ae24587fa.json', scope)
    client = gspread.authorize(creds)
    worksheet = client.open(work_book_name).worksheet(worksheet_name)
    return worksheet


def write_to_workbook(row_name, row_data, work_book_name, worksheet_name):
    # document-specific operation! Be careful if copy it
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('filmdev-fuel-675ae24587fa.json', scope)
    client = gspread.authorize(creds)
    worksheet1 = client.open(work_book_name).worksheet(worksheet_name)
    worksheet1.update('A' + str(row_name), [row_data])


def find_and_modify_cell_by_other_cell_value(work_book_name, worksheet_name, column_number, cell_value_to_search,
                                             column_cell_number_to_edit, data_for_enter):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('filmdev-fuel-675ae24587fa.json', scope)
    client = gspread.authorize(creds)
    worksheet1 = client.open(work_book_name).worksheet(worksheet_name)
    sheet = worksheet1.get_all_values()
    for row_number, row in enumerate(sheet):
        if cell_value_to_search in row[column_number]:
            worksheet1.update_cell(row_number+1, column_cell_number_to_edit, data_for_enter)
            print('update status for ', cell_value_to_search, 'driver= ', data_for_enter)
            return worksheet_name, row[column_number], data_for_enter


def write_to_doc(user_id, callback_command, text_from_user):
    """
    :param user_id:
    :param callback_command: inlineKeyboard callback string delimiter ';'
    :param text_from_user:
    :return: True
    """
    print('write_to_doc start', user_id, callback_command, text_from_user)
    if TICKETS in callback_command:
        print('write_to_doc => if TICKETS in callback_command ', callback_command)
        if ADD_TICKETS in callback_command:
            worksheet1 = read_from_worksheet('telegram-filmfuel', 'Талоны')
            sheet = worksheet1.get_all_values()
            sheet_rows_new = len(sheet) + 1
            fuel_type = get_fuel_type(callback_command)  # ok
            fuel_litres = get_fuel_litres(callback_command)  # ok
            # print('fuel_litres= ',fuel_litres, '\n ticket_number= ', ticket_number)
            input_date = datetime.date.today().strftime("%d.%m.%Y")
            my_str1 = text_from_user.split()
            res1 = my_str1[-1]
            manager_name = get_username_from_telegramid(user_id)  # ok
            write_to_workbook(str(sheet_rows_new),
                              [input_date, '', fuel_type, fuel_litres, '', '', res1, '', '', '', manager_name],
                              'telegram-filmfuel', 'Талоны')
            ticket_reply_text = 'нов.талон: Дата:' + input_date + ' ' + fuel_type + ' ' + fuel_litres + 'л.' + res1 + ' добавил:' + manager_name
            return ticket_reply_text
    elif DRIVER in callback_command:
        print('write_to_doc => elif DRIVER in callback_command ', callback_command)
        if ADD_DRIVER in callback_command:
            # print('write_drivers => start:\n ', 'user = ', user_id, 'text_from_user = ', text_from_user)
            worksheet1 = read_from_worksheet('telegram-filmfuel', 'Водитель')
            sheet = worksheet1.get_all_values()
            # print(sheet)
            # print('write_drivers=> connected, rows= ', len(sheet) )
            sheet_rows_new = len(sheet) + 1
            # driver_date = datetime.date.today().strftime("%d.%m.%Y")
            # print('write_drivers => text_from_user = ', text_from_user)
            driver_project = parse_project_name(callback_command)
            fuel_drivers = ' '
            # manager_name = get_username_from_telegramid(user_id)
            worksheet1.update('A' + str(sheet_rows_new),
                              [[text_from_user, driver_project, '', '', '', fuel_drivers]])

            write_to_workbook(str(sheet_rows_new), [text_from_user, driver_project, '', '', '', fuel_drivers],
                              'telegram-filmfuel', 'Водитель')
            return text_from_user, driver_project
    print('write_to_doc => finished')
    return True

def get_all_data(file_name):  # get from gs_file allTickets, allDrivers, allProjects
    # self.all_data = {"Tickets": [], "Drivers": [], "Projects":[]}
    result_data = {"Tickets": [], "Drivers": [], "Projects":[]}
    worksheet1 = read_from_worksheet(file_name, 'Талоны')
    result_data["Tickets"] = worksheet1.get_all_values()
    result_data["Tickets"].pop(0)
    worksheet1 = read_from_worksheet(file_name, 'Водитель')
    result_data["Drivers"] = worksheet1.get_all_values()
    for i in range(3):
        result_data["Drivers"].pop(0)
    worksheet1 = read_from_worksheet(file_name, 'Проект')
    result_data["Projects"] = worksheet1.get_all_values()
    result_data["Projects"].pop(0)
    return result_data

def get_fuel_litres(fuel_type_str):
    if '10L' in fuel_type_str:
        return '10'
    elif '20L' in fuel_type_str:
        return '20'
    else:
        return '0'

def parse_project_name(menu_command_string):
    # for drivers operations
    if PROJECT1 in menu_command_string:
        return 'ПРОЕКТ 1'
    elif PROJECT2 in menu_command_string:
        return 'ПРОЕКТ 2'
    elif PROJECT3 in menu_command_string:
        return 'ПРОЕКТ 3'
    else:
        return 'все проекты'

def get_fuel_type(fuel_type_str):
    if 'A95' in fuel_type_str:
        return 'А-95'
    elif 'GAZ' in fuel_type_str:
        return 'ГАЗ'
    elif 'DIZEL' in fuel_type_str:
        return 'ДТ'


def get_ticket_status(ticket_string):
    print('get_fuel_status => ', ticket_string, '\n len= ', len(ticket_string))
    if len(ticket_string) == TICKET_ELEMENTS:
        row = ticket_string
        print(row[0], ' ', row[2], ' ', row[3], ' ', row[6], ' ', row[7], ' ', row[8])
        if not row[7]:  # нікому не видані
            return FREE_
        elif (row[7]) and (not row[8]):  # видані не закриті
            return BUSY_
        elif (row[7]) and (row[8]):  # видані та закриті
            return CLOSED_
    return ''


def get_username_from_telegramid(telegram_user_id):
    # static definitions - need migrate to config
    if telegram_user_id == 263255207:
        telegram_user_name = 'Андрій Вознюк'
    elif telegram_user_id == 421392418:
        telegram_user_name = 'Демидов Сергей'
    elif telegram_user_id == 696626950:
        telegram_user_name = 'OrcinusO'
    elif telegram_user_id == 297360613:
        telegram_user_name = 'Владимир Бугай'
    elif telegram_user_id == 340851561:
        telegram_user_name = 'Валерия Каноник'
    else:
        telegram_user_name = 'наверное ктото из наших'
    # print('get_username_from_telegramid: ',telegram_user_id)
    return telegram_user_name

def decode_commands(command_str):
    # print('decode_commands_for_humans ', command_str)
    if TICKETS == command_str:
        return 'талон'
    elif DRIVER == command_str:
        return 'водитель'
    elif PROJECT == command_str:
        return 'проект'
    elif ADD_ == command_str:
        return 'добавить'
    elif RUN_ == command_str:
        return 'обработка'
    elif LIST_ == command_str:
        return 'список'
    elif STATINFO_ == command_str:
        return 'статистика'
    elif FREE_ == command_str:
        return 'свободн'
    elif BUSY_ == command_str:
        return 'выданное'
    elif CLOSED_ == command_str:
        return 'закрытые'
    elif CLOSE_ == command_str:
        return 'закрыть'
    elif RETURN_ == command_str:
        return 'вернуть'
    elif GIVE_ == command_str:
        return 'выдать'
    elif A95 == command_str:
        return 'А-95'
    elif DIZEL == command_str:
        return 'ДТ'
    elif GAZ == command_str:
        return 'газ'
    elif NOPROJECT == command_str:
        return 'все проекты'
    elif START_MENU == command_str:
        return 'главное меню'
    elif L10 == command_str:
        return '10л'
    elif L20 == command_str:
        return '20л'
    elif GIVE_TIK == command_str:
        return 'выдать талон'
    else:
        return command_str
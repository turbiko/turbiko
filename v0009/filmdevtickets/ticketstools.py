""" v0008
Tickets class and functions
"""
from filmdevdrivers.devdrivers import *
from gstools.gsutils import read_from_worksheet


class Ticket:

    def __init__(self, ticket_data_list):
        self.date = ticket_data_list[0]
        self.gas_station = ticket_data_list[1]
        self.fuel_tupe = ticket_data_list[2]
        self.fuel_litres = ticket_data_list[3]
        self.ticket_price = ticket_data_list[5]
        self.ticket_id = ticket_data_list[6]
        self.driver_name = ticket_data_list[7]
        self.closed_date = ticket_data_list[8]

    def compare_for_search(self, text_to_search):
        if text_to_search in self.ticket_id:
            return True
        else:
            return False


# ==========================

class FuelTickets:

    def __init__(self, gsfile_name: str, gstickets_sheet: str):
        worksheet = read_from_worksheet(gsfile_name, gstickets_sheet)
        all_tickets = []
        for ticket_counter, ticket in enumerate(worksheet):
            all_tickets[ticket_counter] = Ticket(ticket)

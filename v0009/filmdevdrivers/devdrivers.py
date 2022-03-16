""" v0008
FuelBot Drivers class and functions
"""

class FuelDevDriver:

    def __init__(self, driver_name: str, driver_project: str, driver_id: str):
        self.driver_name = driver_name
        self.driver_project = driver_project
        self.driver_id = driver_id

    def compare_for_driver_name_search(self, text_to_search: str):
        if text_to_search in self.driver_name:
            return True
        else:
            return False

    def compare_for_driver_id_search(self, text_to_search: str):
        if text_to_search in self.driver_id:
            return True
        else:
            return False


class FuelDevDrivers:

    def __init__(self, gsfile_name: str, gsdrivers_sheet: str):
        worksheet = read_from_worksheet(gsfile_name, gsdrivers_sheet)
        all_drivers = []
        for driver_counter, driver in enumerate(worksheet):
            if driver_counter > 2:
                all_drivers.append(FuelDevDriver(driver[0], driver[1], driver[2]))

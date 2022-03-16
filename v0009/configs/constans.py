BOT_VERSION: str = 'Fuel Bot v0009 20.06.2020'
START_MENU = 'START_MENU'
PROJECTS = 'PRJs'

# ============== First Level kb  ==============
TICKETS = 'TICKETS'
DRIVER = 'DRIVER'
PROJECT = 'PROJECT'

# ============== PREFIXES ==============
ADD_ = 'ADD'  # add something
RUN_ = 'RUN'  # Run action
LIST_ = 'LIST'  # show data mentioned after prefix
STATINFO_ = 'STATINFO'
FREE_ = "FREE"  # status for item
BUSY_ = 'BUSY'  # status for item
CLOSED_ = 'CLOSED'  # status for item

L10 = '10L'
L20 = '20L'

# ============== ACTIONS
CLOSE_ = 'OFF'
RETURN_ = 'RETURN'  # повернути виданий талон
GIVE_ = 'GIVE'  # Видати талон водію
tg_super_admin = 263255207  # andrii voznyuk Telegram user_id

# Fuel tupes
A95 = 'A95'
DIZEL = 'DIZEL'
GAZ = 'GAZ'

# ============== Projects ==============
NOPROJECT = 'NO_PROJECT'
PROJECT1 = 'PROJECT1'
PROJECT2 = 'PROJECT2'
PROJECT3 = 'PROJECT3'

# ready to use combinations for callback in inline keyboard
ADD_TICKETS = TICKETS + ';' + ADD_  # add new tickets
LIST_TICKETS = TICKETS + ';' + LIST_  # list tickets
CLOSE_TICKETS = TICKETS + ';' + CLOSE_  # filter closed tickets
OFF_TICKETS = TICKETS + ';' + CLOSE_  # close open/busy ticket
GIVE_TICKETS = TICKETS + ';' + GIVE_  # give ticket to driver
ADD_DRIVER = DRIVER + ';' + ADD_
LIST_DRIVER = DRIVER + ';' + LIST_
ADD_PROJECT = DRIVER + ';' + ADD_

# LIST TICKETS strings
START_CALCULATION_RESULT = '\n'

# ============== conversations ==============
SELECT_DRV = 'SEL_DRV'
SELECT_TIK = 'SEL_TIK'
SELECT_FUEL = 'SEL_FL'
SET_PRICE = 'SET_PRICE'
ENTER_TIK = 'ENTER_TIK'
GIVE_TIK = 'GIVE_TIK'

# ================ googleSheet properties
TICKET_ELEMENTS = 11
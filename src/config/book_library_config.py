"""
Library configuration settings for book transactions and library operations
"""


class BookLibraryConfig:
    # Book transaction settings
    DEFAULT_DUE_DAYS = 15
    MAX_BOOKS_PER_MEMBER = 5
    FINE_PER_DAY = 10  # Fine amount per overdue day
    RENEWAL_DAYS = 7  # Additional days when renewing a book

    # Library operational settings
    LIBRARY_NAME = "City Central Library"
    OPENING_HOURS = "9:00 AM - 6:00 PM"
    CLOSED_DAYS = ["Sunday", "Public Holidays"]

    # Book settings
    MAX_BORROW_DURATION = 30  # Maximum total days a book can be borrowed
    RESERVATION_HOLD_DAYS = 3  # Days to hold a reserved book
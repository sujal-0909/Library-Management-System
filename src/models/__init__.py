from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .member import Member
from .book import Book
from .borrowing import Borrowing
from .fine import Fine
from .reservation import Reservation


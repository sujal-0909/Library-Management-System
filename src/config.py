import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdf#FGSgvasgf$5$WGT'
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or 3306
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'library_management'
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # Fine calculation settings
    FINE_PER_DAY = 1.00  # $1 per day overdue
    MAX_BORROW_DAYS = 14  # 2 weeks default borrow period
    MAX_RENEWALS = 2  # Maximum number of renewals allowed
    GRACE_PERIOD_DAYS = 2  # 2 days grace period before fines start accumulating


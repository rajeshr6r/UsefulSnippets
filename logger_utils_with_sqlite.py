import logging
import os
import sqlite3
from datetime import datetime
 
class SQLiteHandler(logging.Handler):
    def __init__(self, conn, batchid, application):
        super().__init__()
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.batchid = batchid
        self.application = application
 
    def ensure_table(self):
        self.cursor.executecursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                logger_name TEXT,
                batchid TEXT,
                application TEXT,
                message TEXT
            )
        ''')
 
        self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_logs_batchid_application
                ON logs ( batchid, application)            
        ''')
        self.conn.commit()
    
 
    def emit(self, record):
        log_entry = self.format(record)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(
            'INSERT INTO logs (timestamp, level, logger_name, batchid, application, message) VALUES (?, ?, ?, ?, ?, ?)',
            (timestamp, record.levelname, record.name, self.batchid, self.application, record.getMessage())
        )
        self.conn.commit()
 
class LoggerManager:
    batchid = None
    application = None
    log_dir = "logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sqlite_conn = None
 
    @classmethod
    def configure(cls, batchid, application):
        cls.batchid = batchid
        cls.application = application
 
    @classmethod
    def setup_sqlite_logging(cls, db_file='logs/logs.db'):
        os.makedirs(cls.log_dir, exist_ok=True)
        cls.sqlite_conn = sqlite3.connect(db_file, check_same_thread=False)
 
        cursor = cls.sqlite_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                logger_name TEXT,
                batchid TEXT,
                application TEXT,
                message TEXT
            )
        ''')
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_batchid ON logs(batchid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_application ON logs(application)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)')
 
        cls.sqlite_conn.commit()
 
        print(f"SQLite log DB created at: {os.path.abspath(db_file)}")
 
    @classmethod
    def setup_logger(cls, name, log_file, level=logging.INFO, format_str=None):
        os.makedirs(cls.log_dir, exist_ok=True)
 
        logger = logging.getLogger(name)
        logger.setLevel(level)
 
        if logger.hasHandlers():
            logger.handlers.clear()
 
        file_handler = logging.FileHandler(log_file)
 
        if not format_str:
            format_str = '%(asctime)s | %(levelname)s | %(message)s'
 
        formatter = logging.Formatter(format_str)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
 
        # Attach SQLite logging handler if DB is initialized
        if cls.sqlite_conn:
            sqlite_handler = SQLiteHandler(
                cls.sqlite_conn, cls.batchid, cls.application
            )
            sqlite_handler.setFormatter(formatter)
            logger.addHandler(sqlite_handler)
 
        return logger
 
    @classmethod
    def get_automation_logger(cls):
        log_file = os.path.join(cls.log_dir, f"{cls.application}_automation_{cls.batchid}.log")
        return cls.setup_logger("automation_logger", log_file)
 
    @classmethod
    def close_sqlite_connection(cls):
        if cls.sqlite_conn:
            cls.sqlite_conn.close()
            cls.sqlite_conn = None


"""
Example Implementation 
from logger_utils import LoggerManager
batchid = "yourbatchid" # generate using a timestamp to seperate log files 
application = "yourapplicationname" # this is to add an application name 
LoggerManager.configure(batchid,applicationname)
LoggerManager.setup_sqlite_logging() # only if this is line is added the db gets initiated 
"""

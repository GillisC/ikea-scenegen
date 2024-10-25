import sqlite3
import threading
import os
import shutil
from datetime import datetime, timedelta


class DatabaseHandler:
    """
    Singleton class for handling interactions with the database.
    """

    instance = None

    def __new__(cls, is_local_copy=True):
        """Constructor for the singleton class DatabaseHandler"""
        if not cls.instance:
            if sqlite3.threadsafety != 3:
                print("*** WARNING *** sqlite3 is not fully thread safe")

            cls.instance = super().__new__(cls)

            global_db_filename = "database.db"
            local_db_filename = "database_local.db"

            if is_local_copy:
                file_name = local_db_filename
                if not os.path.isfile(local_db_filename): # 
                    shutil.copyfile(global_db_filename, local_db_filename)
            else:
                file_name = global_db_filename

            cls.instance.db = sqlite3.connect(file_name, check_same_thread=False) # Connects to the given database
            cls.instance.lock = threading.Lock() # Prevents multiple threads from accessing the database at the same time
            cls.instance.db.row_factory = sqlite3.Row # Allows for accessing columns by name instead of index

            cursor = cls.instance.db.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")  # Enables foreign key constraints
            cls.setup_tables(cls.instance)
            return cls.instance

    def setup_tables(self):
        """Initializes the database tables if they do not exist."""
        
        print("Setting up tables")
        
            #"""
            #DROP TABLE IF EXISTS Images;
            #""",
            #""
            #ROP TABLE IF EXISTS RecentImages;
            #"",
            #"""
            #DROP TABLE IF EXISTS SavedImages;
            #""",
            #"""
            #ROP TABLE IF EXISTS SharedImages;
            #""",

        queries = [
            """
            CREATE TABLE IF NOT EXISTS Users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS UserSessions(
                token_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                expiration TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES Users(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Images(
                image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                image BLOB NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS FavoriteImages(
                user_id TEXT NOT NULL,
                image_url TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES Users(id)
                PRIMARY KEY (user_id, image_url)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS RecentImages(
                user_id TEXT NOT NULL,
                image_id INTEGER NOT NULL,
                num INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES Users(id)
                FOREIGN KEY(image_id) REFERENCES Images(image_id)
                PRIMARY KEY (user_id, image_id)
            );
            """,
            """
            CREATE TRIGGER IF NOT EXISTS maintain_recent_images
            AFTER INSERT ON RecentImages
            BEGIN
                UPDATE RecentImages
                SET num = num + 1
                WHERE user_id = NEW.user_id AND num <= 21;

                DELETE FROM RecentImages
                WHERE user_id = NEW.user_id AND num > 21;
            END;
            """,
            """
            CREATE TABLE IF NOT EXISTS SavedImages(
                user_id TEXT NOT NULL,
                image_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES Users(id)
                FOREIGN KEY(image_id) REFERENCES Images(image_id)
                PRIMARY KEY (user_id, image_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS SharedImages(
                sender_user_id TEXT NOT NULL,
                receiver_user_id TEXT NOT NULL,
                image_id INTEGER NOT NULL,
                FOREIGN KEY (sender_user_id) REFERENCES Users(id)
                FOREIGN KEY (receiver_user_id) REFERENCES Users(id)
                FOREIGN KEY (image_id) REFERENCES Images(image_id) 
                PRIMARY KEY (sender_user_id, receiver_user_id, image_id)
            );
            """,
        ]
        with self.lock:
            cursor = self.db.cursor()
            try:
                for query in queries:
                    cursor.execute(query)
            except Exception as e:
                print(f"Database setup error: {e}")
                raise
            self.db.commit()

    def select_query(self, query: str, values: tuple=(), return_one=False):
        """
        Performs a select query on the database.

        Parameters:
        query (str): The query to be executed.
        values (tuple): The values to be inserted into the query.
        return_one (bool): Whether to return one row or all rows.

        Returns:
        dict: A dictionary containing the row(s) information.
        """
        try:
            with self.lock:
                cursor = self.db.cursor()
                cursor.execute(query, values)

                if return_one:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error when inserting: {e}")

    def insert_query(self, query: str, values: tuple):
        """
        Performs an insert query on the database.

        Parameters:
        query (str): The query to be executed.
        values (tuple): The values to be inserted into the query.

        Returns:
        None
        """
        try:
            with self.lock:
                cursor = self.db.cursor()   
                cursor.execute(query, values)
                self.db.commit()
        
        except Exception as e:
            print(f"Error when inserting: {e}")


    def delete_query(self, query: str, values: tuple):
        """
        Performs a delete query on the database.

        Parameters:
        query (str): The query to be executed.
        values (tuple): The values to be used in the query.

        Returns:
        None
        """
        try:
            with self.lock:
                cursor = self.db.cursor()   
                cursor.execute(query, values)
                self.db.commit()

        except Exception as e:
            print(f"Error when deleting: {e}")


    def get_last_image_inserted(self):
        """
        Performs a select query on the database.

        Returns:
        dict: The image id of the last image inserted into the Images table.
        """
        print("we are here")
        try:
            with self.lock:
                cursor = self.db.cursor()
                query = "SELECT last_insert_rowid() AS image_id;"
                cursor.execute(query)

                last_inserted = cursor.fetchone()
                if last_inserted:
                    print(f"image_id: {last_inserted['image_id']}")
                    return last_inserted["image_id"]
                
        except Exception as e:
            print(f"Error when trying to get last image_id: {e}")

    # Takes string date_string, for example '2023-01-17 10:42:08', and returns DateTime object
    @staticmethod
    def str_to_datetime(date_string):
        return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    # Takes DateTime object dt, returns string such as '2023-01-17 10:42:08'
    @staticmethod
    def datetime_to_str(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S")


    

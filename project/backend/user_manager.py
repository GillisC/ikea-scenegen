import threading
import uuid
import os
import hashlib
import time
import sqlite3
from datetime import datetime, timedelta
from .database_handler import DatabaseHandler
import re


class UserManager:
    """Class for handling user-related operations."""

    def __init__(self, database_handler):
        self.db_handler = database_handler
        self.lock = threading.Lock()
        self.tokens = {}

        # Load previously saved sessions
        tokens_saved = self.db_handler.select_query(
            "SELECT token_id, user_id, expiration FROM UserSessions;"
        )
        for token in tokens_saved:
            user = self.find_user_with_id(token["user_id"])
            self.tokens[token["token_id"]] = Token(user, expiration_str=token["expiration"])


    def find_user_with_id(self, user_id):
        """Finds and returns a user-object using a given user_id."""
        user = self.db_handler.select_query(
            "SELECT username, password_hash, salt FROM Users WHERE id=?;",
            (user_id,),
            return_one=True,
        )
        if user == None:
            return None
        else:
            favorites = self.db_handler.select_query(
                "SELECT image_url FROM FavoriteImages WHERE user_id=?;",
                (user_id,)
            )
            return User(
                user_id,
                user["username"],
                bytes.fromhex(user["password_hash"]),
                bytes.fromhex(user["salt"]),
                [row["image_url"] for row in favorites]
            )

    def find_user_with_name(self, username):
        """Finds and returns a user-object using a given username, only used for login and registration"""
        # time.sleep(0.1) # Make brute force harder
        user = self.db_handler.select_query(
            "SELECT id, password_hash, salt FROM Users WHERE username=?;",
            (username,),
            return_one=True,
        )
        if user == None:
            return None
        else:
            favorites = self.db_handler.select_query(
                "SELECT image_url FROM FavoriteImages WHERE user_id=?;",
                (user["id"],)
            )
            return User(
                user["id"],
                username,
                bytes.fromhex(user["password_hash"]),
                bytes.fromhex(user["salt"]),
                [row["image_url"] for row in favorites]
            )

    def register(self, username, password):
        """Inserts a new user into the Users table using the given username and password."""

        if not re.match("^[a-zA-Z0-9_-]+$", username):
            raise ValueError("Username contains invalid characters")

        if not re.match("^[^\s]{8,}$", password):
            raise ValueError("Password contains invalid characters or is too short")

        user_id = str(uuid.uuid4())
        SALT_LENGTH = 16
        salt = os.urandom(SALT_LENGTH) 
        password_hash = secure_hash(password, salt)

        self.db_handler.insert_query(
            "INSERT INTO Users(id, username, password_hash, salt) VALUES (?, ?, ?, ?);",
            (user_id, username, password_hash.hex(), salt.hex()),
        )   

    def get_user(self, token_id):
        """Returns the user associated with the given token_id."""
        token = None
        with self.lock:
            token = self.tokens.get(token_id)

        if token:
            if datetime.now() > token.expiration: # Check if token has expired
                self.delete_token(token_id)
                return None
            else:
                return token.user

        return None

    def get_users(self):
        results = self.db_handler.select_query("SELECT id, username FROM Users;")
        users = []
        for row in results:
            user = User(row["id"], row["username"], None, None)
            users.append(user)
        return users


    def create_token(self, user, lifetime):
        """Creates a new token for the given user with the given lifetime. Returns a token_id."""
        token_id = str(uuid.uuid4())
        token = Token(user, lifetime)

        if lifetime == Token.LIFETIME_LONG: # Save token in database if session should be remembered
            self.db_handler.insert_query(
                "INSERT INTO UserSessions(token_id, user_id, expiration) VALUES (?, ?, ?);",
                (token_id, user.id, DatabaseHandler.datetime_to_str(token.expiration))
            )

        with self.lock:
            self.tokens[token_id] = token

        return token_id

    def delete_token(self, token_id):
        """Deletes the token with the given token_id."""
        with self.lock:
            self.tokens.pop(token_id, None)
            self.db_handler.insert_query(
                "DELETE FROM UserSessions WHERE token_id=?;",
                (token_id,)
            )

    
    def get_all_usernames(self, user_id):
        result = self.db_handler.select_query(
            "SELECT id, username FROM Users WHERE NOT id=?",
            (user_id,)
            )
        usernames = [{"id": row[0], "username": row[1]} for row in result]
        
        return usernames


class User:
    """
    Class representing a user.

    Attributes:
    id (str): The unique id of the user.
    username (str): The username of the user.
    password_hash (bytes): The hashed password of the user.
    salt (bytes): The salt used in hashing the password.
    favorite_images (arr[str]): Array containing image_urls, can be None
    """

    def __init__(self, user_id, username, password_hash, salt, favorite_images=None):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.salt = salt
        self.favorite_images = favorite_images or []

    def __str__(self):
        #return f"id: {self.id}, username: {self.username}, password_hash: {self.password_hash.hex()}, salt: {self.salt.hex()}, favorite_images: {self.favorite_images}"
        return f"id: {self.id}, username: {self.username}, favorite_images: {self.favorite_images}"

    def has_password(self, password):
        """Checks if the given password is correct for the user."""
        new_pw_hash = secure_hash(password, self.salt)

        # Check password securely
        same = True
        for i in range(len(new_pw_hash)):
            if new_pw_hash[i] != self.password_hash[i]:
                same = False

        return same and (len(new_pw_hash) == len(self.password_hash))


class Token:
    """Class representing a user session token, used to remember logged in users."""

    LIFETIME_LONG  = timedelta(days=31)
    LIFETIME_SHORT = timedelta(minutes=15)

    def __init__(self, user, lifetime = None, expiration_str = None):
        assert isinstance(user, User)
        assert (bool(lifetime) != bool(expiration_str)) # Assert either exclusively

        if lifetime:
            assert (lifetime == Token.LIFETIME_LONG or lifetime == Token.LIFETIME_SHORT)
            self.expiration = datetime.now() + lifetime
        else:
            assert(isinstance(expiration_str, str))
            self.expiration = DatabaseHandler.str_to_datetime(expiration_str)

        self.user = user


def secure_hash(plaintext, salt):
    N = 16384  # CPU/Memory cost factor
    R = 8      # Block size
    P = 2      # Parallelization factor
    DKLEN = 64 # Length of derived key
    return hashlib.scrypt(plaintext.encode("utf-8"), salt=salt, n=N, r=R, p=P, dklen=DKLEN)

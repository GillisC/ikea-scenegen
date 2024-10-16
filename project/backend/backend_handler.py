from project.backend.database_handler import DatabaseHandler
from project.backend.user_manager import UserManager

class BackendHandler:
    """
    Singleton class for handling the database connection.
    Consolidates all the managers into one class.
    All backend operations should be done through this class.
    """

    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            cls.instance.db_handler = DatabaseHandler(is_local_copy=True)
            cls.setup(cls.instance)  # Setup the managers once the instance is created
        return cls.instance

    def setup(self):
        self.user_manager = UserManager(self.db_handler)
import threading
import os
from project.backend.database_handler import DatabaseHandler
import uuid
import base64
import requests

class ImagesManager:

    def __init__(self, database_handler: DatabaseHandler):
        self.db_handler = database_handler
        self.lock = threading.Lock()
        
    
    def store_recent_image(self, user_id, image_url) -> None:
        """Downloads the image from the url, stores it in the Images table and adds a reference to the recentImages table"""
        print("storing generated image...")
        image_path = download_image(image_url)
        blob = convert_data_to_binary(image_path)
    
        self.db_handler.insert_query(
            "INSERT INTO Images (image) VALUES (?);",
            (blob,)
        )
        last_inserted = self.db_handler.get_last_image_inserted()

        # Update RecentImages table
        self.db_handler.insert_query(
            "INSERT INTO RecentImages (user_id, image_id, num) VALUES (?, ?, ?)",
            (user_id, last_inserted, 1)
        )
    
        delete_file(image_path)


    def store_and_save(self, user_id, image_url) -> None:
        """Downloads the image from the url, stores it in the Images table and adds a reference to the recentImages table"""
        print("storing generated image...")
        image_path = download_image(image_url)
        blob = convert_data_to_binary(image_path)
    
        self.db_handler.insert_query(
            "INSERT INTO Images (image) VALUES (?);",
            (blob,)
        )
        last_inserted = self.db_handler.get_last_image_inserted()

        self.db_handler.insert_query(
            "INSERT INTO SavedImages (user_id, image_id) VALUES (?, ?)",
            (user_id, last_inserted)
        )        
    
        delete_file(image_path)

    
    def get_recent_images(self, user_id):
        """Returns a list of images that has recently been generated by the user"""
        result = self.db_handler.select_query(
            """
            SELECT Images.image_id, Images.image
            FROM Images
            JOIN RecentImages ON Images.image_id = RecentImages.image_id
            WHERE RecentImages.user_id = ?
            """,
            (user_id,)
        )

        if result == None:
            return None
        
        result = [(row["image_id"], row["image"]) for row in result]
        # Returns a list of dictionaries
        result = encode_images_for_frontend(result)

        for i in result:
            image_id = i["image_id"]
            i["is_saved"] = self.check_if_image_saved(user_id, image_id)

        return result


    def get_saved_images(self, user_id):
        """Returns a list of tuples (image_id, image) that the user has saved"""
        result = self.db_handler.select_query(
            """
            SELECT Images.image_id, Images.image
            FROM Images
            JOIN SavedImages ON Images.image_id = SavedImages.image_id
            WHERE SavedImages.user_id = ?
            """,
            (user_id,)
        )

        if result == None:
            return None
        
        result = [(row["image_id"], row["image"]) for row in result]
        # Returns a list of dictionaries
        result = encode_images_for_frontend(result)

        for i in result:
            image_id = i["image_id"]
            i["is_saved"] = self.check_if_image_saved(user_id, image_id) 
        
        return result
    

    def get_shared_images(self, user_id):
        """Returns a list of images that has been shared with the user"""
        result = self.db_handler.select_query(
            """
            SELECT Images.image_id, Images.image
            FROM Images
            JOIN SharedImages ON Images.image_id = SharedImages.image_id
            WHERE SharedImages.receiver_user_id = ?
            """,
            (user_id,)
        )

        if result == None:
            return None
        
        result = [(row["image_id"], row["image"]) for row in result]
        # Returns a list of dictionaries
        result = encode_images_for_frontend(result)

        for i in result:
            image_id = i["image_id"]
            i["is_saved"] = self.check_if_image_saved(user_id, image_id)

        return result

    def toggle_save(self, user_id, image_id):
        """Adds or deleted the image from the saved table"""
        result = self.db_handler.select_query(
            "SELECT 1 FROM SavedImages WHERE user_id=? AND image_id=?;",
            (user_id, image_id,)
        )
        print(f"result: {result}")
        if len(result) == 0:
            # Save the image for the user
            self.db_handler.insert_query(
                "INSERT INTO SavedImages (user_id, image_id) VALUES (?, ?);",
                (user_id, image_id,)
            )
            print("toggled on saved")
        else:
            # The user wants to remove the image as saved
            self.db_handler.delete_query(
                "DELETE FROM SavedImages WHERE user_id=? AND image_id=?;",
                (user_id, image_id,)
            )
            print("toggled off saved")


    def share_image(self, sender_id, receiver_id, image_id):
        # Check if the image is already shared
        result = self.db_handler.select_query(
            "SELECT 1 FROM SharedImages WHERE sender_user_id=? AND receiver_user_id=? AND image_id=?;",
            (sender_id, receiver_id, image_id,)
        )
        if result is not None:
            # Share the image
            self.db_handler.insert_query(
                "INSERT INTO SharedImages (sender_user_id, receiver_user_id, image_id) VALUES (?, ?, ?);",
                (sender_id, receiver_id, image_id,)
            )
        else:
            print("already been shared brah")

    def check_if_image_saved(self, user_id, image_id):
        result = self.db_handler.select_query(
            "SELECT 1 FROM SavedImages WHERE user_id=? AND image_id=?;",
            (user_id, image_id,),
            return_one=True
        )
        return result is not None
    
    def save_image_blob(self, user_id, image_blob):
        """Stores the image in the SavedImages table directly from a blob"""
        self.db_handler.insert_query(
                "INSERT INTO SavedImages (user_id, image) VALUES (?, ?);",
            (user_id, image_blob,)
        )


def download_image(url) -> str:
    """Downloads an image from the url and return the path of the stored image"""
    project_root = os.getcwd()
    save_directory = os.path.join(project_root, "project\static\img\downloads")
    
    try:
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            image_name = random_stream() # The numbers part
            save_path = "project/static/img/downloads/" + image_name + ".jpg"

            with open(save_path, "wb") as file:
                file.write(response.content)
            print(f"image successfully downloaded: {save_path}")
            return save_path
        
        else:
            #print(f"Failed to retreive the image: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"An error occurred while trying to download the image: {e}")
        return None

def delete_file(file_path):
    """Is used after table insertion to clean up hehe, is maybe unnecassary"""
    try:
        # Check if the file exists
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {file_path} has been deleted.")
        else:
            print(f"File {file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

def random_stream() -> str:
    return str(uuid.uuid4())

def convert_data_to_binary(image_path):
    with open(image_path, "rb") as file:
        binary_data = file.read()
    return binary_data

def convert_blob_to_base64(image_blob):
    image_base64 = base64.b64encode(image_blob).decode("utf-8")
    return image_base64

def encode_images_for_frontend(images):
    """
    Encodes image data to Base64 format for frontend display.
    
    Args:
        recent_images (list of tuples): A list of tuples with (image_id, image_blob).
        
    Returns:
        list of dicts: A list of dictionaries containing image_id and Base64-encoded image data.
    """
    encoded_images = []
    for image_id, image_blob in images:
        base64_image = base64.b64encode(image_blob).decode('utf-8')
        encoded_images.append({
            'image_id': image_id,
            'image_data': f"data:image/png;base64,{base64_image}"  # Format it as a data URL
        })
    return encoded_images
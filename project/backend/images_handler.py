import threading
import requests
import os
from project.backend.database_handler import DatabaseHandler
import uuid
import base64

class ImagesManager:

    def __init__(self, database_handler: DatabaseHandler):
        self.db_handler = database_handler
        self.lock = threading.Lock()
        
    
    def store_image(self, user_id, image_url) -> None:
        """Downloads the image from the url, stores it in the RecentImages table"""
        image_path = download_image(image_url)
        blob = convert_data_to_binary(image_path)
        self.db_handler.insert_query(
            "INSERT INTO RecentImages (user_id, image, num) VALUES (?, ?, ?);",
            (user_id, blob, 1,)
        )
        delete_file(image_path)

    
    def get_recent_images(self, user_id):
        result = self.db_handler.select_query(
            "SELECT image FROM RecentImages WHERE user_id=?;",
            (user_id,)
        )

        if result == None:
            return None
        
        recent_images = []
        for row in result:
            base64_image = convert_blob_to_base64(row["image"])  # If select_query returns tuples
            recent_images.append(base64_image)
        
        return recent_images


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
            print(f"Failed to retreive the image: {response.status_code}")
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
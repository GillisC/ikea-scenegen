from flask import Flask, jsonify, render_template, request, redirect, session, g
from dotenv import load_dotenv
import os
from openai import OpenAI
from .backend.backend_handler import BackendHandler
from .backend.user_manager import Token
import requests
from PIL import Image
from io import BytesIO
from transformers import BlipProcessor, BlipForConditionalGeneration


app = Flask(__name__)
app.secret_key = "this is super secret"
app.permanent_session_lifetime = Token.LIFETIME_LONG
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Set SameSite to None
app.config['SESSION_COOKIE_SECURE'] = True      # Ensure the cookie is only sent over HTTPS

backend = BackendHandler()

# Set your OpenAI API key
load_dotenv()
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Global variables to store the latest image's set of parameters, image url and image description 
last_style = ""
last_time = ""
last_season = ""
last_feeling = ""
last_materials = []
last_audience = ""
last_market = ""
last_pov = ""
last_country = ""

last_image_url = None
last_image_description = None


@app.before_request
def before_request_handler():
    # Ignore static resources
    if request.endpoint == "static":
        return

    # Retrieve user information from session
    g.token_id = session.get("token")
    g.user = backend.user_manager.get_user(g.token_id)

    # Allow access to the register page even if not logged in
    if request.path == "/register":
        return

    # If user is logged in, redirect away from login page
    if g.user:
        if request.path == "/login":
            return redirect("/")
        return
    else:
        # If not logged in and not on the login page, redirect to login
        if request.path != "/login":
            return redirect("/login")


def generate_prompt(style: str, time: str, season: str, feeling: str, materials: list[str], audience: str, market: str, pov: str, country: str):
    
    update_latest_image_info(style, time, season, feeling, materials, audience, market, pov, country)

    base_prompt = f"""
        Generate an image of a kitchen with the following parameters:
        - Style: {style}
        - Time of day: {time}
        - Season: {season}
        - Feeling/atmosphere: {feeling}
        - Materials: {', '.join(materials)}
        - Intended audience: {audience}
        - Intended market where the kitchen will be made for: {market}
        - Point of view: {pov}
        - Let this country influence the design: {country}
        If a field is empty simply ignore that constraint, and the image should not include any depiction of a human and should not contain any visible text.
        """
    # define update parameters as global last parameters set, and include those in the new edit prompt
    return base_prompt


def update_latest_image_info(style: str, time: str, season: str, feeling: str, materials: list[str], audience: str, market: str, pov: str, country: str): 
     global last_style, last_time, last_season, last_feeling, last_materials, last_audience, last_market, last_pov, last_country
     last_style = style
     last_time = time
     last_season = season
     last_feeling = feeling
     last_materials = materials
     last_audience = audience
     last_market = market
     last_pov = pov
     last_country = country

@app.route('/generate-image', methods=['POST'])
def generate_image():
    print("Starting to generate mockup...")
    try:
        # Get the data from the JSON request
        data = request.get_json()
        print(repr(data))
        
        # Extract the values sent from the client
        style = data.get('style')
        time = data.get('time')
        season = data.get('season')
        feeling = data.get('feeling')
        materials = data.get('materials')
        audience = data.get('audience')
        market = data.get('market')
        pov = data.get('pov')
        country = data.get("country")

        # Generate the prompt dynamically based on the input
        prompt = generate_prompt(style, time, season, feeling, materials, audience, market, pov, country)
        print(prompt)
       
        image_url = generate_image_from_prompt(prompt)
        
        # Return the image URL in the response as JSON
        return jsonify({'image_url': image_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_image_from_prompt(prompt): 
    global last_image_url
    global last_image_description

    try: 
    # Call DALL·E API to generate the image
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,  # Number of images
        )
        
        # Extract the image URL from the response
        image_url = response.data[0].url
        last_image_url = image_url
        last_image_description = generate_image_description(image_url)

        return image_url
    except Exception as e: 
        raise RuntimeError(f"Failed to generate image: {str(e)}")


def generate_image_description(image_url):
    try:
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful
        image = Image.open(BytesIO(response.content))

        # Generate a description using the BLIP model
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs)
        description = processor.decode(out[0], skip_special_tokens=True)
        return description
    except Exception as e:
        raise RuntimeError(f"Failed to generate image description: {str(e)}")


@app.route('/submit-input', methods=['POST'])
def submit_input():
    global last_image_url
    global last_image_description
    try:
        # Get the data from the JSON request
        data = request.get_json()
        user_input = data.get('user_input')
        print(f"Received user input: {user_input}")
    
        if last_image_url:
            prompt = f"""
            Generate a realistic looking market image of a kitchen that is as similar as possible as the following image url: {last_image_url},
            with the following description: {last_image_description}.
            The image should also have the following parameters:
            - Style: {last_style}
            - Time of day: {last_time}
            - Season: {last_season}
            - Feeling/atmosphere: {last_feeling}
            - Materials: {', '.join(last_materials)}
            - Intended audience: {last_audience}
            - Intended market where the kitchen will be made for: {last_market}
            - Point of view: {last_pov}
            - Let this country influence the design: {last_country},         
            The image should also follow this prompt: {user_input}. If the prompt contradicts any previous description of the image, give the prompt more weight
            and discard the original descriptions where necessary.  
            """
        else:
            print("no image yet") ## handle case where no image has been generated for edit to begin with 

        #png_image = convert_image_url_to_PNG(last_image_url)
        image_url = generate_image_from_prompt(prompt)
        last_image_url = image_url

        print("edited image url generated")

        # Return the image URL in the response as JSON
        return jsonify({'image_url': image_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route("/login", methods = ["GET"])
def login():
    return render_template("login.html")


@app.route("/login", methods = ["POST"])
def handle_login():
    username = request.form["username"]
    password = request.form["password"]
    remember = request.form.get("remember")

    user = backend.user_manager.find_user_with_name(username)
    if user and user.has_password(password):
        if remember:
            session.permanent = True
            session["token"] = backend.user_manager.create_token(user, Token.LIFETIME_LONG)
        else:
            session.permanent = False
            session["token"] = backend.user_manager.create_token(user, Token.LIFETIME_SHORT)

        return "success"

    return "wrong username or password", 403

@app.route("/register", methods = ["GET"])
def register():
    return render_template("register.html")

@app.route("/register", methods = ["POST"])
def handle_register():
    username = request.form["username"]
    password = request.form["password"]

    user = backend.user_manager.find_user_with_name(username)
    if user == None:
        backend.user_manager.register(username, password)   
        return "success"

    return "username already exists", 403


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/list-files', methods=['GET'])
def get_files():
    return jsonify(os.listdir("./project/static/boundries"))

@app.route("/generate_image", methods = ["GET"])
def home():
    return render_template("index.html")

@app.route("/logout", methods = ["POST"])
def handle_logout():
    backend.user_manager.delete_token(g.token_id)
    session.pop("token", None)
    return redirect("/login")


if __name__ == '__main__':
    app.run(debug=True)

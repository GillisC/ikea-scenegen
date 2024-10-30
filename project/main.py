from flask import Flask, jsonify, render_template, request, redirect, session, g
from dotenv import load_dotenv
import os
from openai import OpenAI
from .backend.backend_handler import BackendHandler
from .backend.user_manager import Token


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


def generate_prompt(style: str, time: str, season: str, feeling: str, materials: list[str], audience: str, pov: str, country: str, lighting: str, aperture: str):
    base_prompt = f"""
        Generate an image of a kitchen with the following parameters:
        - Style: {style}
        - Time of day: {time}
        - Season: {season}
        - Feeling/atmosphere: {feeling}
        - Materials: {', '.join(materials)}
        - Intended audience: {audience}
        - Point of view: {pov}
        - Let this country influence the design: {country}
        - Make the image look like this lighting was used to photograph it: {lighting}
        - Make the image look like it was taken with a camera with an aperture of: {aperture}
        If a field is empty simply ignore that constraint, and the image should not include any depiction of a human and should not contain any visible text.
        """
    return base_prompt

@app.route('/generate-image', methods=['POST'])
def generate_image():
    user = backend.user_manager.get_user(g.token_id)
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
        pov = data.get('pov')
        country = data.get("country")
        lighting = data.get("lighting")
        aperture = data.get("aperture")

        # Generate the prompt dynamically based on the input
        prompt = generate_prompt(style, time, season, feeling, materials, audience, pov, country, lighting, aperture)
        print(prompt)
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
        # Store the generated image in recently generated section
        backend.images_manager.store_recent_image(user.id, image_url)
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
    return render_template("index.html", active_tab="generate")

@app.route('/saved_images')
def saved_images():
    user = backend.user_manager.get_user(g.token_id)

    # Reverse the lists so the newly added is on the left most side of the page
    recent_images = backend.images_manager.get_recent_images(user.id)[::-1]
    saved_images = backend.images_manager.get_saved_images(user.id)[::-1]
    shared_images = backend.images_manager.get_shared_images(user.id)[::-1]

    return render_template(
        "saved.html", active_tab="saved",
        recent_images=recent_images, 
        saved_images=saved_images, 
        shared_images=shared_images
        )


@app.route('/list-files', methods=['GET'])
def get_files():
    return jsonify(os.listdir("./project/static/boundries"))


@app.route("/logout", methods = ["POST"])
def handle_logout():
    backend.user_manager.delete_token(g.token_id)
    session.pop("token", None)
    return redirect("/login")


@app.route("/save-image", methods = ["POST"])
def save_image():
    image_id = request.get_json().get("image_id")
    user = backend.user_manager.get_user(g.token_id)
    backend.images_manager.toggle_save(user.id, image_id)
    return jsonify({"status": "success"}), 200

@app.route("/save-image-by-url", methods = ["POST"])
def save_image_by_url():
    image_url = request.get_json().get("image_url")
    user = backend.user_manager.get_user(g.token_id)
    try: 
        backend.images_manager.store_and_save(user.id, image_url)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error occurring while trying to save: {e}")
    return jsonify({"status": "failure"}), 200



@app.route('/test-generate-image', methods=['POST'])
def test_generate_image():
    """Used to test the backend with stock images"""
    try:
        random_img_url = "https://picsum.photos/1024"
        user = backend.user_manager.get_user(g.token_id)
        backend.images_manager.store_recent_image(user.id, random_img_url)
        
        # Return the image URL in the response as JSON
        return jsonify({'image_url': random_img_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/get_all_users", methods=["POST"])
def get_all_users():
    # Returns all user execept the user themselves
    user = backend.user_manager.get_user(g.token_id)
    all_usernames = backend.user_manager.get_all_usernames(user.id)
    return jsonify(all_usernames)


@app.route("/share-image", methods=["POST"])
def share_image():
    user = backend.user_manager.get_user(g.token_id)
    receiver_user_id = request.get_json().get("receiver_user_id")
    image_id = request.get_json().get("image_id")

    backend.images_manager.share_image(user.id, receiver_user_id, image_id)
    
    return jsonify({"status": "success"}), 200



if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import os
from openai import OpenAI

app = Flask(__name__)

# Set your OpenAI API key
load_dotenv()
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

def generate_prompt(style: str, time: str, season: str, feeling: str, materials: list[str], audience: str, market: str, pov: str):
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
        If a field is empty simply ignore that constraint, and the image should not include any depiction of a human
        """
    return base_prompt

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        # Get the data from the JSON request
        data = request.get_json()
        
        # Extract the values sent from the client
        style = data.get('style')
        time = data.get('time')
        season = data.get('season')
        feeling = data.get('feeling')
        materials = data.get('materials')
        audience = data.get('audience')
        market = data.get('market')
        pov = data.get('pov')

        # Generate the prompt dynamically based on the input
        prompt = generate_prompt(style, time, season, feeling, materials, audience, market, pov)
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
        
        # Return the image URL in the response as JSON
        return jsonify({'image_url': image_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

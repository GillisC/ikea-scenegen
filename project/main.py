from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
from openai import OpenAI

app = Flask(__name__)

# Set your OpenAI API key
load_dotenv()
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form['prompt']

        try:
            # Call DALL·E API to generate an image
            response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,  # Number of images
            )

            print(response)
            # Extract the image URL
            image_url = response.data[0].url
            return render_template('index.html', image_url=image_url, prompt=prompt)
        except Exception as e:
            return str(e)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

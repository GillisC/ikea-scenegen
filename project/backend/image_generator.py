class ImageGenerator:
    def __init__(self, client):
        self.client = client


def generate_prompt(style: str, time: str, season: str, feeling: str, materials: list[str], audience: str, market: str, pov: str, country: str):
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
    return base_prompt


def generate_image(request):
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
        # Call DALL·E API to generate the image
        response = self.client.images.generate(
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
    

    def get_parameters(request):


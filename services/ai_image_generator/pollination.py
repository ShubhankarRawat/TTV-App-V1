import settings
import random
import requests
import urllib

def get_pollinationAI(image_prompts, width, height, model, folder_name, negative_prompt = settings.NEGATIVE_IMAGE_PROMPT):
    #negative_prompt = "bad quality, worse quality, low quality, deformed body, deformation, deformed hands, deformed eyes, deformed face, deformed lips, deformed legs, distorted legs, distorted hands, multiple heads, multiple bodies"
    results = []
    i = 1
    for image_prompt in image_prompts:
        generated_image_received = False
        used_seeds = []
        while generated_image_received == False:
            seed = random.randint(1, 10000000000)
            if seed not in used_seeds:
                params = {
                    "width": width,
                    "height": height,
                    "seed": seed,
                    "model": model,
                    "nologo": "true", # Optional
                    "transparent": "false", # Optional - generates transparent background (gptimage model only)
                    "private": "true",
                    "enhance": "false",
                    "token": settings.POLLINATIONS_API_TOKEN,
                    "negative_prompt": negative_prompt,
                    "quality": "high",
                    "safe": "true"
                    #"referrer": "MyPythonApp" # Optional
                }

                encoded_prompt = urllib.parse.quote(image_prompt)
                image_url = f"{settings.POLLINATION_URL}/{encoded_prompt}"
                image_name = folder_name + 'image_' + str(i) + '.jpg'

                try:
                    response = requests.get(image_url, params=params, timeout=300) # Increased timeout for image generation
                    response.raise_for_status() # Raise an exception for bad status codes

                    with open(image_name, 'wb') as f:
                        f.write(response.content)
                    generated_image_received = True
                    print("Image saved as ", image_name)
                    results.append(image_name)
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching image: {e}")
        print(f"[INFO] Generated {i}/{len(image_prompts)} images")
        i = i+1
    return results

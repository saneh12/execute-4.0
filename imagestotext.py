import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from flask import Flask, request, jsonify
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from flask_cors import CORS
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

# Load BLIP-2 Model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to("cuda" if torch.cuda.is_available() else "cpu")

def fix_url(url, base_url):
    """Ensures extracted image URLs have a proper scheme (http/https)."""
    if url.startswith("//"):
        return "https:" + url  # Add HTTPS scheme to URLs that start with //
    elif url.startswith("/"):
        return base_url + url  # Convert relative URLs to absolute using base URL
    return url  # Return unchanged if already correct


def generate_caption(image_url):
    try:
        response = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return "Failed to fetch image"

        image = Image.open(BytesIO(response.content)).convert("RGB")

        inputs = processor(image, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        output = model.generate(**inputs)
        caption = processor.batch_decode(output, skip_special_tokens=True)[0]

        return caption
    except Exception as e:
        return str(e)
@app.route('/auto-alt-text', methods=['POST'])
def auto_alt_text():
    data = request.get_json(silent=True)
    if not data or "website_url" not in data:
        return jsonify({"error": "Invalid request, 'website_url' missing"}), 400

    website_url = data["website_url"]
    try:
        response = requests.get(website_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch website"}), 500

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract and fix image URLs
        images = [
            urljoin(website_url, img["src"]) if "src" in img.attrs else None
            for img in soup.find_all("img")
        ]
        images = [img for img in images if img]  # Remove None values

        if not images:
            return jsonify({"error": "No images found"}), 404

        # Generate captions
        captions = {img: generate_caption(img) for img in images}

        return jsonify({"image_captions": captions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

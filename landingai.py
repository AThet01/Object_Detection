import requests
import streamlit as st
from PIL import Image, ImageDraw
import io

# Function to resize the image while maintaining aspect ratio
def resize_image(image, max_width=400):
    width, height = image.size
    ratio = max_width / float(width)
    new_height = int(float(height) * ratio)
    resized_image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
    return resized_image

# Function to compress the image
def compress_image(image, quality=80):
    byte_io = io.BytesIO()
    image.save(byte_io, format="JPEG", quality=quality)
    byte_io.seek(0)
    return byte_io

# Function to draw bounding boxes on the image
from PIL import Image, ImageDraw, ImageFont

# Function to draw bounding boxes with confidence scores
def draw_bounding_boxes(image, detections):
    draw = ImageDraw.Draw(image)

    # Load a font (optional, requires a font file)
    try:
        font = ImageFont.truetype("arial.ttf", 20)  # Adjust font size
    except IOError:
        font = ImageFont.load_default()  # Use default if font not available

    for detection in detections:
        bbox = detection.get('bounding_box', [])  # Fix key name
        label = detection.get('label', 'Unknown')
        confidence = detection.get('score', 0)  # Use correct confidence key

        if bbox:
            x_min, y_min, x_max, y_max = bbox

            # Draw bounding box (green)
            draw.rectangle([x_min, y_min, x_max, y_max], outline="green", width=3)

            # Prepare label text
            text = f"{label} ({confidence:.2f})"

            # Get text size for better positioning
            text_size = draw.textbbox((0, 0), text, font=font)
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1]

            # Draw filled background for text
            draw.rectangle([x_min, y_min - text_height, x_min + text_width, y_min], fill="green")

            # Draw text label
            draw.text((x_min, y_min - text_height), text, fill="white", font=font)

    return image

# Function to process the uploaded image
def process_image(uploaded_file, max_width=800, quality=80):
    image = Image.open(uploaded_file)
    resized_image = resize_image(image, max_width)
    return compress_image(resized_image, quality)

# Function to make the API call


def detect_objects(uploaded_file, object_type):
    url = "https://api.landing.ai/v1/tools/agentic-object-detection"
    api_key = ""  # Replace with your actual API key
    
    # Prepare the image for processing
    processed_image = process_image(uploaded_file)  # Make sure process_image() is defined
    
    # Prepare the request payload
    files = {
        "image": ("image.jpg", processed_image, "image/jpeg")
    }
    data = {
        "prompts": [f" {object_type} with high accuracy"],  
        "model": "best-available"  
    }
    headers = {
        "Authorization": f"Basic {api_key}",
    }

    # Make the API request
    response = requests.post(url, files=files, data=data, headers=headers)

    # Handle API response
    if response.status_code == 200:
        result = response.json()
        
        # Ensure we correctly extract detection results
        if "data" in result and isinstance(result["data"], list) and len(result["data"]) > 0:
            detections = result["data"][0]  # Extract objects from first item
            if isinstance(detections, list):  # Ensure it's a list
                return detections
    return []  # Return an empty list if no detections found

# Streamlit UI
def app():
    st.title("Object Detection")

    # Dropdown for object selection
    object_type = st.selectbox("Select Object Type to Detect", ["car", "cat", "bike", "bus","flower","cup","laptop"])

    # Upload image using Streamlit file uploader
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

    # Check if a file is uploaded before proceeding
    if uploaded_file is not None:
        st.write("Processing...")

        # Ensure the uploaded file is in a readable format
        try:
            detections = detect_objects(uploaded_file, object_type)

            if detections:
                image = Image.open(uploaded_file)
                image_with_boxes = draw_bounding_boxes(image.copy(), detections)
                st.image(image_with_boxes, caption=f"Image with {object_type.capitalize()} Bounding Boxes", use_column_width=True)
            else:
                st.write(f"No {object_type} detected in the image.")
        except Exception as e:
            st.error(f"Error processing image: {e}")
    else:
        st.write("Please upload an image first.")
# Fix the main function check
if __name__ == "__main__":
    app()

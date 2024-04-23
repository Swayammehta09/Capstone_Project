import os
import streamlit as st
import cv2
import numpy as np
from deoldify import device
from deoldify.device_id import DeviceId
from deoldify.visualize import *
from PIL import Image
import io
import tempfile
import base64

def colorize_image(uploaded_file, render_factor, watermarked):
    # Set up DeOldify
    device.set(device=DeviceId.GPU0 if torch.cuda.is_available() else DeviceId.CPU)  # Choose GPU if available, else CPU
    colorizer = get_image_colorizer(artistic=True)

    # Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file_path = temp_file.name
        uploaded_file.seek(0)
        temp_file.write(uploaded_file.read())

    # Colorize the image
    colorized_image_path = colorizer.plot_transformed_image(temp_file_path, render_factor=render_factor, watermarked=watermarked)

    # Load the colorized image as a PIL Image
    colorized_image_pil = Image.open(colorized_image_path)

    # Create an in-memory file-like object for the colorized image
    colorized_img_bytes = io.BytesIO()
    colorized_image_pil.save(colorized_img_bytes, format='JPEG')
    colorized_img_bytes.seek(0)

    # Clean up the temporary file
    os.remove(temp_file_path)

    return uploaded_file, colorized_img_bytes

def get_base64_of_image(file_path):
    """Encode the image as base64."""
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def main():
    # Path to your image
    image_path = 'static/bg.png'
    encoded_image = get_base64_of_image(image_path)

    # CSS to inject specifying the background image
    background_image_css = f"""
    <style>
    .stApp {{
        background-image: url('data:image/png;base64,{encoded_image}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: black;  /* Set text color to black */
    }}
    
    /* Style for the sidebar (white with blur effect) */
    .stSidebar {{
        background-color: #ba90e3; /* Change sidebar color */
        backdrop-filter: blur(16px);
    }}
    /* Additional styling may be needed for other sidebar elements */
    .css-1l02zno {{
        background-color: #ba90e3; /* Change sidebar color */
        backdrop-filter: blur(8px);
    }}
    </style>
    """

    # Inject the CSS with markdown
    st.markdown(background_image_css, unsafe_allow_html=True)
    st.title('Chroma')
    st.subheader("Image Colorizer")
    st.write("Upload a black and white image to colorize")
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'], accept_multiple_files=False)
    render_factor = st.slider("Render Factor", min_value=7, max_value=40, value=35)
    watermarked = True 
    
    if uploaded_file is not None:
        file_size_limit = 5000 * 1024  # 5MB limit
        if uploaded_file.size <= file_size_limit:
            if st.button("Colorize Image"):
                # Colorize the image
                with st.spinner('Colorizing...'):
                    original_file, colorized_img_bytes = colorize_image(uploaded_file, render_factor, watermarked)
                    st.success('Colorization complete!')

                # Display the original and colorized images side by side
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader('Original Image')
                    st.image(original_file, use_column_width=True)
                with col2:
                    st.subheader('Colorized Image')
                    st.image(colorized_img_bytes, use_column_width=True)

                # Download button for the colorized image
                st.download_button(label="Download Colorized Image",
                                data=colorized_img_bytes.getvalue(),
                                file_name="colorized_image.jpg",
                                mime="image/jpeg")
        else:
            st.error("The file is too large. Please upload files less than 5MB.")

if __name__ == "__main__":
    main()

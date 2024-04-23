import streamlit as st
from pages import Image_Coloriser, Video_Coloriser, Youtube_Video_Coloriser, Audio_Enhancement
import base64
from PIL import Image
from streamlit_image_comparison import image_comparison

# Function to encode the image as base64
def get_base64_of_image(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

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
    theme: light; /* Set theme to light */
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

# Main page title
st.markdown("# Chroma")
img1 = Image.open("static/Test.jpeg")
img2 = Image.open("static/Testout.jpg")

# render image-comparison
image_comparison(img1,img2,show_labels=False,make_responsive=True)

# Additional content
st.write("""
### Welcome to Chroma!

Chroma is an advanced multimedia enhancement tool powered by state-of-the-art AI technology. With Chroma, you can bring old photos and videos to life by adding vibrant colors and enhancing their visual and audio quality.

---

#### Features:

- **Image Colorizer**: Transform black and white photos into colorful masterpieces.
- **Video Colorizer**: Add vivid colors to old monochrome videos.
- **YouTube Video Colorizer**: Colorize YouTube videos directly from their URLs.
- **Audio Enhancement**: Improve the audio quality of videos by reducing background noise.

---

#### Get Started:

1. Upload your images, videos, or YouTube URLs.
2. Choose the enhancement options.
3. Sit back and watch as Chroma works its magic!

---

#### Why Chroma?

- **Advanced AI Technology**: Chroma utilizes cutting-edge Generative Adversarial Networks (GANs) for precise and realistic colorization and enhancement.
- **User-Friendly Interface**: With Chroma's intuitive interface, anyone can easily enhance their multimedia content.
- **Real-Time Processing**: Experience fast and seamless processing, delivering high-quality results in seconds.

---

#### About Us:

Chroma is developed by a team of AI enthusiasts dedicated to pushing the boundaries of multimedia enhancement. Our mission is to empower users to unlock the full potential of their digital media and preserve precious memories for generations to come.

---

Ready to experience the power of Chroma? Start enhancing your multimedia content today!

""")



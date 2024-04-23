import streamlit as st
import cv2
import numpy as np
from deoldify import device
from deoldify.device_id import DeviceId
from deoldify.visualize import *
import tempfile
import os
import moviepy.editor as mp

# Function to colorize the video frames using DeOldify
def colorize_video(video_file, render_factor):
    try:
        # Set up DeOldify
        device.set(device=DeviceId.GPU0 if torch.cuda.is_available() else DeviceId.CPU)
        colorizer = get_video_colorizer()

        # Create a temporary directory to save the uploaded video frames
        temp_dir = tempfile.mkdtemp()

        # Save the uploaded video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file_path = temp_file.name
            video_file.seek(0)
            temp_file.write(video_file.read())

        # Colorize the video
        colorized_video_path = colorizer.colorize_from_file_name(temp_file_path, render_factor=render_factor)

        # Clean up the temporary video file
        os.remove(temp_file_path)

        return colorized_video_path
    except Exception as e:
        st.error(f"Error: {e}")
        st.error("An error occurred while colorizing the video. Please check the file format and try again.")

# Function to add audio to the colorized video
def add_audio(video_file, audio_file, colorized_frames, temp_dir):
    # Compile colorized frames into video without audio
    temp_video_path = os.path.join(temp_dir, 'colorized_temp.mp4')
    frame_height, frame_width, _ = colorized_frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video_path, fourcc, 24.0, (frame_width, frame_height))
    for frame in colorized_frames:
        out.write(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Convert color format to RGB before writing
    out.release()

    # Add audio to the colorized video
    video = mp.VideoFileClip(temp_video_path)
    audio = mp.AudioFileClip(audio_file)
    video = video.set_audio(audio)
    video.write_videofile("colorized_temp_with_audio.mp4", codec="libx264", audio_codec="aac")

def get_base64_of_image(file_path):
    """Encode the image as base64."""
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

# Main function to run the Streamlit app
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
    st.subheader("Video Colorizer")
    st.write("Upload a black and white video to colorize")
    
    # Set up DeOldify
    device.set(device=DeviceId.GPU0)  # or DeviceId.CPU if using CPU
    colorizer = get_image_colorizer(artistic=True)

    uploaded_file = st.file_uploader("Choose a video file...", type=["mp4"])

    if uploaded_file is not None:
        # Create a temporary directory to save the uploaded video and audio
        temp_dir = tempfile.mkdtemp()
        video_file_path = os.path.join(temp_dir, 'video.mp4')
        audio_file_path = os.path.join(temp_dir, 'audio.mp3')

        # Save the uploaded video to a temporary file
        with open(video_file_path, 'wb') as f:
            f.write(uploaded_file.read())

        # Extract audio from the uploaded video and save it as a temporary file
        video = mp.VideoFileClip(video_file_path)
        audio = video.audio
        audio.write_audiofile(audio_file_path)

        # Read the video from the temporary file
        cap = cv2.VideoCapture(video_file_path)

        # Initialize lists to store colorized frames
        colorized_frames = []

        # Add a slider to select the render factor
        render_factor = st.slider("Select Render Factor", min_value=1, max_value=40, value=10)

       # Add a button to initiate colorization
        if st.button("Colorize"):
            # Colorize the video frame by frame
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert frame to bytes
                _, buffer = cv2.imencode('.jpg', frame)
                byte_frame = buffer.tobytes()

                # Save byte stream as an image file
                temp_image_path = os.path.join(temp_dir, 'temp_image.jpg')
                with open(temp_image_path, 'wb') as f:
                    f.write(byte_frame)

                # Colorize the frame
                with st.spinner('Colorizing...'):
                    colorized_frame_pil = colorizer.get_transformed_image(temp_image_path, render_factor=render_factor, post_process=True)
                    colorized_frame_np = np.array(colorized_frame_pil)

                # Append the colorized frame to the list
                colorized_frames.append(colorized_frame_np)

            # Release the video capture object and delete the temporary files
            cap.release()

            # Compile colorized frames into video with audio
            add_audio(video_file_path, audio_file_path, colorized_frames, temp_dir)

            # Display original video
            st.subheader("Original Video")
            st.video(video_file_path)

            # Display colorized video with audio
            st.subheader('Colorized Video with Audio')
            st.video("colorized_temp_with_audio.mp4")

            # Display colorized video with audio
            st.subheader('The Colorized Video is Downloaded')

            # Offer the option to download the colorized video
            st.text("Download colorized video:")
            with open("colorized_temp_with_audio.mp4", "rb") as f:
                bytes_data = f.read()
            st.download_button(
                label="Click here to download",
                data=bytes_data,
                file_name="colorized_video_with_audio.mp4",
                mime="video/mp4",
            )

if __name__ == "__main__":
    main()

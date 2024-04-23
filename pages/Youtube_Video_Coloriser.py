import os
import streamlit as st
import cv2
import numpy as np
from deoldify import device
from deoldify.device_id import DeviceId
from deoldify.visualize import *
from PIL import Image
import tempfile
import base64
from pytube import YouTube
import moviepy.editor as mp
from http.client import IncompleteRead

# Function to download a YouTube video
def download_video(url, output_path):
    try:
        yt = YouTube(url)
        ys = yt.streams.get_highest_resolution()
        if ys:
            ys.download(output_path)
            return os.path.join(output_path, ys.title + ".mp4")
        else:
            st.error("No suitable streams found for the provided YouTube URL.")
            return None
    except IncompleteRead as e:
        st.error(f"Error occurred while downloading video: {e}. The video download was incomplete.")
        return None
    except Exception as e:
        st.error(f"Error occurred while downloading video: {e}")
        return None

# Function to colorize the video frames using DeOldify
def colorize_video(video_path, colorizer, render_factor):
    cap = cv2.VideoCapture(video_path)
    colorized_frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to PIL image
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Save frame to a temporary file
        temp_image_path = tempfile.NamedTemporaryFile(suffix='.jpg').name
        frame_pil.save(temp_image_path)

        # Colorize the frame
        colorized_frame_pil = colorizer.get_transformed_image(temp_image_path, render_factor=render_factor, post_process=True)
        colorized_frame_np = np.array(colorized_frame_pil)

        colorized_frames.append(colorized_frame_np)

    cap.release()
    return colorized_frames

# Function to add audio to the colorized video
def add_audio(video_file, colorized_frames):
    # Compile colorized frames into video without audio
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory
    temp_video_path = os.path.join(temp_dir, 'colorized_temp.mp4')
    frame_height, frame_width, _ = colorized_frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video_path, fourcc, 24.0, (frame_width, frame_height))
    for frame in colorized_frames:
        out.write(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Convert color format to RGB before writing
    out.release()

    # Add audio to the colorized video
    video = mp.VideoFileClip(temp_video_path)
    audio = mp.AudioFileClip(video_file)
    video = video.set_audio(audio)
    video.write_videofile("colorized_temp_with_audio.mp4", codec="libx264", audio_codec="aac")

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
    st.subheader("Youtube Video Colorizer")
    device.set(device=DeviceId.GPU0)  # or DeviceId.CPU if using CPU
    colorizer = get_image_colorizer(artistic=True)

    youtube_link = st.text_input("Enter YouTube Video URL:")

    render_factor = st.slider("Select Render Factor", min_value=1, max_value=40, value=10)

    if youtube_link:
        if st.button("Colorize YouTube Video"):
            # Download the YouTube video
            st.text("Downloading video... Please wait.")
            video_path = download_video(youtube_link, "./")
            
            if video_path:
                st.text("Video downloaded successfully.")
                st.video(video_path)

                # Colorize the downloaded video
                st.text("Colorizing video... Please wait.")
                colorized_frames = colorize_video(video_path, colorizer, render_factor)

                # Display the colorized video
                if colorized_frames:
                    st.subheader('Colorized Video')

                    # Write colorized frames to a temporary video file
                    add_audio(video_path, colorized_frames)

                    # Display the colorized video
                    st.video("colorized_temp_with_audio.mp4")

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
                else:
                    st.error("Failed to colorize the video.")
            else:
                st.error("Failed to download the video.")

if __name__ == "__main__":
    main()

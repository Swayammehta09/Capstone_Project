import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from voicefixer import VoiceFixer
import IPython.display as ipd
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy import signal
import streamlit as st
import base64

def load_audio(file_path):
    sr = 44100  # Define the 'sr' variable with a value
    y, sr = librosa.load(file_path, mono=True, sr=sr, offset=0, duration=10)
    return y, sr

def freq(y, sr):
    b, a = signal.butter(10, 2000/(sr/2), btype='highpass')
    yf = signal.lfilter(b, a, y)
    return yf

def show_spectrogram(samples, sr, title):
    plt.figure(figsize=(12, 4))
    plt.title(title)
    S = librosa.feature.melspectrogram(y=samples, sr=sr)
    S_DB = librosa.power_to_db(S, ref=np.max)
    librosa.display.specshow(S_DB, sr=sr, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')
    plt.xlabel('Time')
    plt.ylabel('Frequency (Hz)')
    plt.tight_layout()
    st.pyplot()

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

    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title("Audio Enhancer")

    upload_file = st.file_uploader("Upload an audio file", type=["wav"])

    if upload_file is not None:
        audiofile, sr = load_audio(upload_file)

        st.write("Original audio")
        st.audio(audiofile, format='audio/wav', start_time=0, sample_rate=sr)

        st.write("Spectrogram of the original audio")
        show_spectrogram(audiofile, sr, "Spectrogram of the original audio")

        if st.button("Enhance"):
            vf = VoiceFixer()

            second = librosa.get_duration(y=audiofile, sr=sr)
            rate = sr

            input_file = "out{}_{}.wav".format(second, rate)
            output_file = "out{}_{}_restored.wav".format(second, rate)

            with open(input_file, 'wb') as f:
                f.write(upload_file.getvalue())

            vf.restore(input=input_file, output=output_file, cuda=False, mode=0)

            enhanced_audio, enhanced_sr = load_audio(output_file)

            st.write("Enhanced audio")
            st.audio(enhanced_audio, format='audio/wav', start_time=0, sample_rate=enhanced_sr)

            st.write("Spectrogram of the enhanced audio")
            show_spectrogram(enhanced_audio, enhanced_sr, "Spectrogram of the enhanced audio")
if __name__ == "__main__":
    main()
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
import requests
from io import BytesIO
from PIL import Image
import RPi.GPIO as GPIO
import time

# Set up Spotify OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="8a3bf93750f54ed4b1aea814928df5eb",
    client_secret="91b1672f2bd74b598e676396365c0224",
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-playback-state,user-modify-playback-state"
))

# Set up GPIO
GPIO_PIN = 24  # GPIO pin number
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Helper function to display album art as ASCII art
def display_album_art(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert('L')  # Convert to grayscale

        # Resize the image to a fixed width and height for ASCII art
        new_width, new_height = 80, 40
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        img_data = list(img.getdata())

        for i in range(0, len(img_data), new_width):
            row = img_data[i:i + new_width]
            row_ascii = "".join([ASCII_CHARS[pixel // 10] for pixel in row])
            print(row_ascii)

# ASCII characters to represent different shades
ASCII_CHARS = "@%#*+=-:. "

# Function to handle play/pause on GPIO button press
def play_pause_callback(channel):
    current_track = sp.current_playback()

    if current_track and 'is_playing' in current_track:
        if current_track['is_playing']:
            sp.pause_playback(device_id=current_track['device']['id'])
            print("Playback paused.")
        else:
            sp.start_playback(device_id=current_track['device']['id'])
            print("Playback started.")
        current_track = sp.current_playback()
        display_album_art(current_track['item']['album']['images'][0]['url'])
    else:
        print("No track is currently playing.")

# Add event detection for GPIO button press
GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=play_pause_callback, bouncetime=300)

try:
    # Retrieve information about the currently playing track
    current_track = sp.current_playback()

    # Check if there is a currently playing track
    if current_track and 'item' in current_track:
        # Display the currently playing track title, artist, device name, and ASCII art
        print("Currently playing:", current_track['item']['name'])
        print("Artist:", ", ".join([artist['name'] for artist in current_track['item']['artists']]))
        print("Device:", current_track['device']['name'])
        display_album_art(current_track['item']['album']['images'][0]['url'])
    else:
        print("No track is currently playing.")

    # Keep the script running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Exiting.")

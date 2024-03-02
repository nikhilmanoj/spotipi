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
    scope="user-read-playback-state,user-modify-playback-state,playlist-read-private"
))

# Set up GPIO
GPIO_PIN_PLAY_PAUSE = 24  # GPIO pin number for play/pause
GPIO_PIN_NEXT = 23        # GPIO pin number for next track
GPIO_PIN_PREV = 5         # GPIO pin number for previous track and shuffling the playlist
GPIO_PIN_CHANGE_PLAYLIST = 6  # GPIO pin number for changing the playlist

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

# Function to handle next track on GPIO button press
def next_track_callback(channel):
    sp.next_track()

# Function to handle previous track and shuffling the playlist on GPIO button press
def prev_track_shuffle_callback(channel):
    current_track = sp.current_playback()
    if current_track and 'context' in current_track:
        # Check if the current GPIO pin is the one assigned for changing the playlist
        if channel == GPIO_PIN_CHANGE_PLAYLIST:
            playlists = sp.current_user_playlists()['items']
            playlist_index = sp.current_playback()['context']['uri'].split(':')[-1]
            playlist_index = (int(playlist_index) + 1) % len(playlists)
            playlist_uri = playlists[playlist_index]['uri']

            sp.start_playback(context_uri=playlist_uri)
            print(f"Started playing playlist: {playlists[playlist_index]['name']}")

        else:
            sp.shuffle(True, device_id=current_track['device']['id'])
            print("Shuffling playlist.")
    else:
        print("No playlist is currently playing.")

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN_PLAY_PAUSE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_PIN_NEXT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_PIN_PREV, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_PIN_CHANGE_PLAYLIST, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Add event detection for GPIO button presses
GPIO.add_event_detect(GPIO_PIN_PLAY_PAUSE, GPIO.FALLING, callback=play_pause_callback, bouncetime=300)
GPIO.add_event_detect(GPIO_PIN_NEXT, GPIO.FALLING, callback=next_track_callback, bouncetime=300)
GPIO.add_event_detect(GPIO_PIN_PREV, GPIO.FALLING, callback=prev_track_shuffle_callback, bouncetime=300)
GPIO.add_event_detect(GPIO_PIN_CHANGE_PLAYLIST, GPIO.FALLING, callback=prev_track_shuffle_callback, bouncetime=300)

try:
    # Keep the script running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Exiting.")

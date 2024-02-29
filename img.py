import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
import requests
from io import BytesIO
from PIL import Image

# Set up Spotify OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="8a3bf93750f54ed4b1aea814928df5eb",
    client_secret="91b1672f2bd74b598e676396365c0224",
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-playback-state,user-modify-playback-state"
))

# Helper function to display album art as ASCII art
def display_album_art(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert('L')  # Convert to grayscale

        # Resize the image to a fixed width and height for ASCII art
        new_width, new_height = 40, 20
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        img_data = list(img.getdata())

        for i in range(0, len(img_data), new_width):
            row = img_data[i:i + new_width]
            row_ascii = "".join([ASCII_CHARS[pixel // 25] for pixel in row])
            print(row_ascii)

# ASCII characters to represent different shades
ASCII_CHARS = "@%#*+=-:. "

# Retrieve information about the currently playing track
try:
    current_track = sp.current_playback()
except spotipy.SpotifyException as e:
    print(f"Error: {e}")
    current_track = None

# Check if there is a currently playing track
if current_track and 'item' in current_track:
    # Display the currently playing track title, artist, device name, and album art
    print("Currently playing:", current_track['item']['name'])
    print("Artist:", ", ".join([artist['name'] for artist in current_track['item']['artists']]))
    print("Device:", current_track['device']['name'])
    display_album_art(current_track['item']['album']['images'][0]['url'])
else:
    print("No track is currently playing.")

# Terminal prompts to control playback
while True:
    print("\nOptions:")
    print("1. Toggle Play/Pause")
    print("2. Next Track")
    print("3. Exit")

    choice = input("Enter your choice (1-3): ")

    if choice == '1':
        if current_track['is_playing']:
            sp.pause_playback(device_id=current_track['device']['id'])
            print("Playback paused.")
        else:
            sp.start_playback(device_id=current_track['device']['id'])
            print("Playback started.")
        current_track = sp.current_playback()
        display_album_art(current_track['item']['album']['images'][0]['url'])
    elif choice == '2':
        sp.next_track(device_id=current_track['device']['id'])
        current_track = sp.current_playback()
        print("Skipping to next track:")
        print("Track:", current_track['item']['name'])
        print("Artist:", ", ".join([artist['name'] for artist in current_track['item']['artists']]))
        display_album_art(current_track['item']['album']['images'][0]['url'])
    elif choice == '3':
        print("Exiting.")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 3.")

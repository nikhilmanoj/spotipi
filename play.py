import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util

# Set up Spotify OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="8a3bf93750f54ed4b1aea814928df5eb",
    client_secret="91b1672f2bd74b598e676396365c0224",
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-playback-state,user-modify-playback-state"
))

# Retrieve information about the currently playing track
try:
    current_track = sp.current_playback()
except spotipy.SpotifyException as e:
    print(f"Error: {e}")
    current_track = None

# Check if there is a currently playing track
if current_track and 'item' in current_track:
    # Display the currently playing track title and device name
    print("Currently playing:", current_track['item']['name'])
    print("Device:", current_track['device']['name'])
else:
    print("No track is currently playing.")

# Terminal prompts to control playback
while True:
    print("\nOptions:")
    print("1. Play")
    print("2. Pause")
    print("3. Skip to next track")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        sp.start_playback(device_id=current_track['device']['id'])
        print("Playback started.")
    elif choice == '2':
        sp.pause_playback(device_id=current_track['device']['id'])
        print("Playback paused.")
    elif choice == '3':
        sp.next_track(device_id=current_track['device']['id'])
        print("Skipped to next track.")
    elif choice == '4':
        print("Exiting.")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 4.")

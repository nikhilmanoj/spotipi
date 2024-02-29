import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set up Spotify OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="8a3bf93750f54ed4b1aea814928df5eb",
    client_secret="91b1672f2bd74b598e676396365c0224",
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-playback-state"
))

# Retrieve information about the currently playing track
current_track = sp.current_playback()

# Check if there is a currently playing track
if current_track is not None and 'item' in current_track:
    # Display the currently playing track title
    print("Currently playing:", current_track['item']['name'])
else:
    print("No track is currently playing.")

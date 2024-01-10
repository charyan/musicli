import spotipy
from spotipy.oauth2 import SpotifyOAuth
import subprocess
import requests
import json
import random
import argparse

# Spotify
client_id = 'SPOTIFY_CLIENT_ID'
client_secret = 'SPOTIFY_CLIENT_SECRET'
redirect_uri = 'http://127.0.0.1:8088'

# Ollama
ollama_server_url = "http://localhost:11434/api/generate"
ollama_model_name = "dolphin-mistral"
ollama_prompt = """
Choose a song based on a command output. Give the name of the song. Do not write anything else. Choose a song according to the situation. Be concise. Give me the name of the song and the artist, only. No comment. Be concise.
"""


# Authentication and creating Spotify object
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri=redirect_uri,
                                                scope="user-modify-playback-state user-read-playback-state"))

def search_and_play(song_name, device_id=None):
    # Searching for the song
    result = sp.search(q=song_name, limit=1, type='track')
    tracks = result['tracks']['items']

    actual_device_id = device_id

    if tracks:
        # Get the first track's URI
        track_uri = tracks[0]['uri']

        if actual_device_id is None:
            # Use the first available device
            devices = sp.devices()
            actual_device_id = devices['devices'][0]['id'] if devices['devices'] else None

        if actual_device_id:
            sp.add_to_queue(device_id=actual_device_id, uri=track_uri)
            sp.next_track(device_id=actual_device_id)

            # Play if paused
            if sp.current_playback()['is_playing'] is False:
                sp.start_playback(device_id=actual_device_id)

            # Set the text to green
            print(f"\033[92mPlaying: {tracks[0]['name']} by {tracks[0]['artists'][0]['name']}\033[0m")
        else:
            print("No active devices found")
    else:
        print("Song not found")


# Generate a response for a given prompt with a provided model. This is a streaming endpoint, so will be a series of responses.
# The final response object will include statistics and additional data from the request. Use the callback function to override
# the default handler.
def generate_song_name(command, return_code, output):
    """
    MIT License
    Source: https://github.com/jmorganca/ollama/blob/main/api/client.py
    """
    try:
        payload = {
            "model": ollama_model_name, 
            "prompt": f"{ollama_prompt} - Command: {command} - Return code: {return_code} - Output: {output}", 
            "system": None, 
            "template": None, 
            "context": None, 
            "options": None,
            "format": None,
        }
        
        # Remove keys with None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        with requests.post(ollama_server_url, json=payload, stream=True) as response:
            response.raise_for_status()
            
            
            # Variable to hold concatenated response strings if no callback is provided
            full_response = ""

            progress_counter = 0

            # Iterating over the response line by line and displaying the details
            for line in response.iter_lines():
                if line:
                    # Parsing each line (JSON chunk) and extracting the details
                    chunk = json.loads(line)
                    
                    # If this is not the last chunk, add the "response" field value to full_response and print it
                    if not chunk.get("done"):
                        response_piece = chunk.get("response", "")
                        full_response += response_piece


                        if progress_counter % 3 == 0:
                            chars = "🎜🎝"
                            color_list = ["\033[92m", "\033[93m", "\033[91m", "\033[94m", "\033[95m", "\033[96m", "\033[97m"]
                            stop_color = "\033[0m"

                            # Print a random char with a random color
                            random_char = chars[random.randint(0, len(chars)-1)]
                            random_color = color_list[random.randint(0, len(color_list)-1)]
                            print(f"{random_color}{random_char}{stop_color}   ", end="", flush=True)
                    
                    progress_counter += 1
            
            # print over current line '\r'
            print("\r\033[K", end="", flush=True)
            
            # Return the full response and the final context
            return full_response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None, None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play music on Spotify based on what's happening in your terminal")

    parser.add_argument('--list-devices', action='store_true', help='see what devices are connected to the Spotify account')
    parser.add_argument('--device-id', metavar='DEVICE_ID', type=str, help='the device ID to play the song on')

    args = parser.parse_args()
    
    if args.list_devices:
        devices = sp.devices()

        for device in devices['devices']:
            print (f"{device['name']} - {device['id']} - {device['type']}")

        exit()

    while True:
        
        try:
            user_input = input("🎝 > ")

            if user_input == "exit":
                break

            if user_input == "":
                continue

            proc = subprocess.Popen([user_input], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()


            if out:
                print(out.decode('utf-8'))


            song_name = generate_song_name(user_input, proc.returncode, out.decode('utf-8'))
            search_and_play(song_name, device_id=args.device_id)


        except KeyboardInterrupt:
            print()
            pass
        except EOFError:
            break
    
    print()
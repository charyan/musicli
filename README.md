# MusiCLI: Play music on Spotify based on what's happening in your terminal using a local LLM

![screenshot](screenshot.png)

```
usage: musicli.py [-h] [--list-devices] [--device-id DEVICE_ID]

Play music on Spotify based on what's happening in your terminal

options:
  -h, --help            show this help message and exit
  --list-devices        see what devices are connected to the Spotify account
  --device-id DEVICE_ID
                        the device ID to play the song on
```

# Usage
## Ollama
Install [ollama](https://ollama.ai/)

Pull the model:
```
ollama pull dolphin-mistral
```

Start the ollama server:
```
ollama serve
```

## Spotify
You'll need a [developer account](https://developer.spotify.com/), and to create an app with the permissions `Web Playback SDK` and `Web API`.

Add the `client_id`, `client_secret`, `redirect_uri` for your Spotify app at the top of the script in `musicli.py`.


## MusiCLI
### Setup
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run
```
source venv/bin/activate
python musicli.py

```
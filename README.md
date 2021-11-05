# discord-music-bot
A simple Python music bot for Discord using Lavalink and slash commands that also supports playing songs from Spotify. You can also make use of context menus (right click on user -> apps -> play from Spotify) to add songs to queue through Spotify presence of users. Primarily was made for use in small servers of me and my friends after Groovy died. Bot is very minimal, easy to setup and simple enough to host.

# How to setup
Install all packages in `requirements.txt`. 
Setup a lavalink node or use any of publicly available lavalink node and make a `config.json` file from the following template. You can use your own 18 digit discord user id for "owners". You will also need your own Spotify API key.
```json
{
    "bot_prefix": "!",
    "token": "your token",
    "spotify_api": {
        "client_id": "your spotify client id", 
        "client_secret": "your spotify client secret"
    },
    "nodes": {
        "MAIN": {
            "host": "your lavalink host",
            "port": "your port for lavalink",
            "rest_uri": "your rest uri",
            "password": "lavalink password",
            "identifier": "MAIN",
            "region": "europe"
        }
    },
    "owners": [123456789123456789]
}
```
The `config.json` file should be placed in base directory of bot along with `bot.py`. After this is done simply execute `bot.py`. 

Slash commands can take some time to get registered globally. Prefix commands can be used meanwhile but recommended way to use is through slash commands and context menus. 

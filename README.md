# discord-music-bot
A simple Python music bot for Discord using Lavalink and slash commands that also supports playing songs from Spotify. You can make use of context menus (right click on user -> apps -> play from Spotify) to add songs to queue through Spotify presence of users. You can also use `play` option in context menu to `play` and `play-next` (right click on message containing name of a song -> apps -> play/play-next). Primarily was made for use in small servers of me and my friends after Groovy died. Bot is very minimal, easy to setup and simple enough to host.

# How to setup
Install all packages in `requirements.txt`. 
Setup a lavalink node or use any of publicly available lavalink node and make a `config.json` file from the `sample-config.json` template. You can use your own 18 digit discord user id for "owners". You will also need your own Spotify API key. Along with it you can add some priority guild ids in `guild_ids` so 
slash commands will instantly sync with those guilds.

The `config.json` file should be placed in base directory of bot along with `bot.py`. After this is done simply execute `bot.py`. 

Slash commands can take some time to get registered globally. Prefix commands can be used meanwhile but recommended way to use is through slash commands and context menus. 

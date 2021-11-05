import json

from discord.ext import commands

from helpers.audio.spotify_api.spotify_client import Spotify
from helpers.audio.spotify_api.oauth2 import SpotifyClientCredentials

class Bot(commands.Bot):

    """ 
    This is a custom object which extends default commands.Bot class
    """ 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {}
        self.config_file = kwargs.get("config_file","config.json")
        #self.spotify_client = None
                                                           

    def load_config(self, filename: str=None):
        """
        Load config from a .JSON file. If not specified will default to `Bot.config_file`.
        """

        if not filename:
            filename = self.config_file

        #pro tip: google difference between json `load,dump` and `loads,dumps`.
        with open(filename) as file_object:
            config = json.load(file_object)
            #print(config)
        #also google `isinstance` vs `type`. Hint: `isinstance` is better.
        if isinstance(config, dict):
            for key,value in config.items():
                self.config[key] = value


    def load_spotify_client(self):
        self.spotify_client = Spotify(auth_manager=SpotifyClientCredentials(client_id=self.config["spotify_api"]["client_id"], client_secret=self.config["spotify_api"]["client_secret"]))
import json

import aiohttp
from discord.ext import commands

class Bot(commands.Bot):

    """ 
    This is a custom object which extends default commands.Bot class and provides
    a configuration handler and a common aiohttp ClientSession.
    """ 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {}
    
        self.config_file = kwargs.get("config_file","config.json")
        self.session = aiohttp.ClientSession(loop = self.loop)
    

    def load_config(self, filename: str=None):
        """
        Load congig from a .JSON file. If not specified will default to 
        `Bot.config_file`.
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

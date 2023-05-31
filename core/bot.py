import json

import discord
import wavelink
from discord.ext import commands
from wavelink.ext import spotify


class Bot(commands.Bot):
    def __init__(self, *, intents: discord.Intents):

        # load config
        self.__load_config()
        
        # set intents and command prefix
        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or(self.config["bot_prefix"]),
        )
        

    async def setup_hook(self):
        # sync or remove commands of priority guilds right away, instead of waiting for global sync
        # only for testing
        # for guild_id in self.config["guild_ids"]:
        #     guild = discord.Object(id=guild_id)
            #self.tree.copy_global_to(guild=guild)
            #await self.tree.sync(guild=guild)

        # global sync
        await self.tree.sync()

        #nodes: wavelink.Node = [wavelink.Node(**node) for node in self.config["nodes"]]
        
        # _nodes = list()
        # for node in self.config["nodes"]:
        #     print(node)
        #     node: wavelink.Node = wavelink.Node(uri=node["uri"], password=node["password"], secure=node["secure"])
        #     _nodes.append(node)
        sc = spotify.SpotifyClient(**self.config["spotify_api"])
        
        node: wavelink.Node = wavelink.Node(**self.config["nodes"][0])
        self.node = node
        await wavelink.NodePool.connect(client=self, nodes=[node], spotify=sc)

    def __load_config(self, filename: str = None):
        """
        Load config from a .JSON file. If not specified will default to `config.json`.
        """

        if not filename:
            filename = "config.json"

        with open(filename) as file_object:
            config = json.load(file_object)

        if isinstance(config, dict):
            self.config = config

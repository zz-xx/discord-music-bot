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
        # sync with priority guilds right away, instead of waiting for global sync
        for guild_id in self.config["guild_ids"]:
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

        # for now using only first node, in future use all nodes as fail safe
        self.wavelink_node = await wavelink.NodePool.create_node(
            bot=self,
            **self.config["nodes"][0],
            spotify_client=spotify.SpotifyClient(
                client_id=self.config["spotify_api"]["client_id"],
                client_secret=self.config["spotify_api"]["client_secret"],
            )
        )

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

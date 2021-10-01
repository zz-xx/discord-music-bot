import datetime as dt
import re
import typing as t

import aiohttp
import discord
import wavelink
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

from helpers.audio.exception_handler import *
from helpers.audio.queue import RepeatMode
from helpers.audio.player import Player


# really didn't want to do this
GUILD_IDS = [435683837641621514]


class Audio(commands.Cog, wavelink.WavelinkMixin):

    url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    lyrics_url = "https://some-random-api.ml/lyrics?title="
    hz_bands = (
        20,
        40,
        63,
        100,
        150,
        250,
        400,
        450,
        630,
        1000,
        1600,
        2500,
        4000,
        10000,
        16000,
    )
    time_regex = r"([0-9]{1,2})[:ms](([0-9]{1,2})s?)?"

    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())
        # global GUILD_IDS
        # GUILD_IDS = self.bot.config['guild_ids']

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).teardown()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f" Wavelink node `{node.identifier}` ready.")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not available in DMs.")
            return False

        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        nodes = self.bot.config["nodes"]
        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, SlashContext):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    # @commands.command(name="connect", aliases=["join"])
    @cog_ext.cog_slash(
        name="connect", description="Connect to a VC.", guild_ids=GUILD_IDS
    )
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        if ctx.author.id in ctx.bot.config["owners"]:
            player = self.get_player(ctx)
            channel = await player.connect(ctx, channel)
            await ctx.send(f"Connected to {channel.name}.")
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B,
            )
            await ctx.send(embed=embed)

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            await ctx.send("Already connected to a voice channel.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.")

    @cog_ext.cog_slash(
        name="disconnect",
        description="Disconnect from a VC.",
        guild_ids=GUILD_IDS,
    )
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        await ctx.send("Disconnected.")

    @cog_ext.cog_slash(
        name="play",
        description="Play music.",
        guild_ids=GUILD_IDS,
    )
    async def play_command(self, ctx: SlashContext, *, audio: t.Optional[str]):
        # print(ctx)
        query = audio
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            await ctx.send("Playback resumed.")

        else:
            if "https://open.spotify.com/track" in query:
                await ctx.send("Spotify track detected.")
                response = await ctx.bot.spotify_client.track(track_id=query)
                query = f"{response['name']} {response['album']['artists'][0]['name']}"
                if not re.match(self.url_regex, query):
                    query = f"ytsearch:{query}"

                test = await self.wavelink.get_tracks(query)

                try:
                    await player.add_spotify_tracks(ctx, [test[0]])
                    await ctx.send(f"Added {response['name']} to queue.")
                except Exception as e:
                    print(e)

            elif "https://open.spotify.com/playlist" in query:
                await ctx.send("Spotify playlist detected.")
                response = await ctx.bot.spotify_client.playlist_items(
                    query,
                    offset=0,
                    fields="items.track.name,items.track.artists.name,total",
                    additional_types=["track"],
                )

                for item in response["items"]:

                    query = f"{item['track']['name']} {item['track']['artists'][0]['name']}".strip(
                        "<>"
                    )
                    if not re.match(self.url_regex, query):
                        query = f"ytsearch:{query}"

                    test = await self.wavelink.get_tracks(query)

                    try:
                        await player.add_spotify_tracks(ctx, [test[0]])
                    except Exception as e:
                        print(e)

                await ctx.send(f"Added {response['total']} tracks.")

            elif "https://open.spotify.com/album" in query:
                await ctx.send("Spotify album detected.")
                response = await ctx.bot.spotify_client.album_tracks(query)
                artist_name = response["items"][0]["artists"][0]["name"]
                print(artist_name)

                for item in response["items"]:

                    query = f"{item['name']} {artist_name}"
                    if not re.match(self.url_regex, query):
                        query = f"ytsearch:{query}"

                    test = await self.wavelink.get_tracks(query)

                    try:
                        await player.add_spotify_tracks(ctx, [test[0]])
                    except Exception as e:
                        print(e)

                await ctx.send(f"Added {response['total']} tracks.")

            else:
                query = query.strip("<>")
                if not re.match(self.url_regex, query):
                    query = f"ytsearch:{query}"

                await player.add_tracks(ctx, await self.wavelink.get_tracks(query))

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("No songs to play as the queue is empty.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.")

    @cog_ext.cog_slash(
        name="pause",
        description="Pause currently playing song.",
        guild_ids=GUILD_IDS,
    )
    async def pause_command(self, ctx):
        player = self.get_player(ctx)

        if player.is_paused:
            raise PlayerIsAlreadyPaused

        await player.set_pause(True)
        await ctx.send("Playback paused.")

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("Already paused.")

    # @commands.command(name="stop")
    @cog_ext.cog_slash(
        name="stop", description="Stop the playback.", guild_ids=GUILD_IDS
    )
    async def stop_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.empty()
        await player.stop()
        await ctx.send("Playback stopped.")

    @cog_ext.cog_slash(
        name="next",
        description="Skip the currently playing song.",
        guild_ids=GUILD_IDS,
    )
    async def next_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming:
            raise NoMoreTracks

        await player.stop()
        await ctx.send("Playing next track in queue.")

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send(
                "This could not be executed as the queue is currently empty."
            )
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("There are no more tracks in the queue.")

    @cog_ext.cog_slash(
        name="previous",
        description="Play previous song in queue.",
        guild_ids=GUILD_IDS,
    )
    async def previous_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        await ctx.send("Playing previous track in queue.")

    @previous_command.error
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send(
                "This could not be executed as the queue is currently empty."
            )
        elif isinstance(exc, NoPreviousTracks):
            await ctx.send("There are no previous tracks in the queue.")

    @cog_ext.cog_slash(
        name="shuffle", description="Shuffle the queue.", guild_ids=GUILD_IDS
    )
    async def shuffle_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.shuffle()
        await ctx.send("Queue shuffled.")

    @shuffle_command.error
    async def shuffle_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue could not be shuffled as it is currently empty.")

    @cog_ext.cog_slash(
        name="repeat",
        description="Repeat one or all songs.",
        guild_ids=GUILD_IDS,
    )
    async def repeat_command(self, ctx, mode: str):
        if mode not in ("none", "1", "all"):
            raise InvalidRepeatMode

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        await ctx.send(f"The repeat mode has been set to {mode}.")

    @cog_ext.cog_slash(
        name="queue", description="Show current queue.", guild_ids=GUILD_IDS
    )
    async def queue_command(self, ctx):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        embed = discord.Embed(
            title="Queue",
            description=f"Showing up to next {10} tracks",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_author(name="Query Results")
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url,
        )
        embed.add_field(
            name="Currently playing",
            value=getattr(
                player.queue.current_track, "title", "No tracks currently playing."
            ),
            inline=False,
        )
        if upcoming := player.queue.upcoming:
            embed.add_field(
                name="Next up",
                value="\n".join(t.title for t in upcoming[:10]),
                inline=False,
            )

        msg = await ctx.send(embed=embed)

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is currently empty.")

    # Requests -----------------------------------------------------------------

    @cog_ext.cog_slash(
        name="volume",
        description="Manipulate volume from 0 to 150",
        guild_ids=GUILD_IDS,
    )
    async def volume_group(self, ctx, volume: int):
        player = self.get_player(ctx)

        if volume < 0:
            raise VolumeTooLow

        if volume > 150:
            raise VolumeTooHigh

        await player.set_volume(volume)
        await ctx.send(f"Volume set to {volume:,}%")

    @volume_group.error
    async def volume_group_error(self, ctx, exc):
        if isinstance(exc, VolumeTooLow):
            await ctx.send("The volume must be 0% or above.")
        elif isinstance(exc, VolumeTooHigh):
            await ctx.send("The volume must be 150% or below.")

    @cog_ext.cog_slash(
        name="lyrics",
        description="Show lyrics of song that's playing.",
        guild_ids=GUILD_IDS,
    )
    async def lyrics_command(self, ctx):
        player = self.get_player(ctx)
        name = player.queue.current_track.title

        async with aiohttp.request("GET", self.lyrics_url + name, headers={}) as r:
            if not 200 <= r.status <= 299:
                raise NoLyricsFound

            data = await r.json()

            # if len(data["lyrics"]) > 2000:
            # return await ctx.send(f"<{data['links']['genius']}>")

            embed = discord.Embed(
                title=data["title"],
                url=data["links"]["genius"],
                description=data["lyrics"][:4096],
                colour=ctx.author.colour,
                timestamp=dt.datetime.utcnow(),
            )
            embed.set_thumbnail(url=data["thumbnail"]["genius"])
            embed.set_author(name=data["author"])
            await ctx.send(embed=embed)

    @lyrics_command.error
    async def lyrics_command_error(self, ctx, exc):
        if isinstance(exc, NoLyricsFound):
            await ctx.send("No lyrics could be found.")

    @cog_ext.cog_slash(
        name="equalizer",
        description="Select an equalizer preset from 'flat', 'boost', 'metal', or 'piano'",
        guild_ids=GUILD_IDS,
    )
    async def eq_command(self, ctx, preset: str):
        player = self.get_player(ctx)

        eq = getattr(wavelink.eqs.Equalizer, preset, None)
        if not eq:
            raise InvalidEQPreset

        await player.set_eq(eq())
        await ctx.send(f"Equaliser adjusted to the {preset} preset.")

    @eq_command.error
    async def eq_command_error(self, ctx, exc):
        if isinstance(exc, InvalidEQPreset):
            await ctx.send(
                "The EQ preset must be either 'flat', 'boost', 'metal', or 'piano'."
            )

    @cog_ext.cog_slash(
        name="advance-equalizer",
        description="Band number between 1 and 15 and EQ gain between 10 dB and -10 dB.",
        guild_ids=GUILD_IDS,
    )
    async def adveq_command(self, ctx, band: int, gain: float):
        player = self.get_player(ctx)

        if not 1 <= band <= 15 and band not in self.hz_bands:
            raise NonExistentEQBand

        if band > 15:
            band = self.hz_bands.index(band) + 1

        if abs(gain) > 10:
            raise EQGainOutOfBounds

        player.eq_levels[band - 1] = gain / 10
        eq = wavelink.eqs.Equalizer(
            levels=[(i, gain) for i, gain in enumerate(player.eq_levels)]
        )
        await player.set_eq(eq)
        await ctx.send("Equaliser adjusted.")

    @adveq_command.error
    async def adveq_command_error(self, ctx, exc):
        if isinstance(exc, NonExistentEQBand):
            await ctx.send(
                "This is a 15 band equaliser -- the band number should be between 1 and 15, or one of the following "
                "frequencies: " + ", ".join(str(b) for b in self.hz_bands)
            )
        elif isinstance(exc, EQGainOutOfBounds):
            await ctx.send(
                "The EQ gain for any band should be between 10 dB and -10 dB."
            )

    @cog_ext.cog_slash(
        name="playing",
        description="Playback Information",
        guild_ids=GUILD_IDS,
    )
    async def playing_command(self, ctx):
        player = self.get_player(ctx)

        if not player.is_playing:
            raise PlayerIsAlreadyPaused

        embed = discord.Embed(
            title="Now playing",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_author(name="Playback Information")
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url,
        )
        embed.add_field(
            name="Track title", value=player.queue.current_track.title, inline=False
        )
        embed.add_field(
            name="Artist", value=player.queue.current_track.author, inline=False
        )

        position = divmod(player.position, 60000)
        length = divmod(player.queue.current_track.length, 60000)
        embed.add_field(
            name="Position",
            value=f"{int(position[0])}:{round(position[1]/1000):02}/{int(length[0])}:{round(length[1]/1000):02}",
            inline=False,
        )

        await ctx.send(embed=embed)

    @playing_command.error
    async def playing_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("There is no track currently playing.")

    @cog_ext.cog_slash(
        name="skip",
        description="Skip to nth track in queue.",
        guild_ids=GUILD_IDS,
    )
    async def skipto_command(self, ctx, index: int):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        if not 0 <= index <= player.queue.length:
            raise NoMoreTracks

        player.queue.position = index - 2
        await player.stop()
        await ctx.send(f"Playing track in position {index}.")

    @skipto_command.error
    async def skipto_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("There are no tracks in the queue.")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("That index is out of the bounds of the queue.")

    @cog_ext.cog_slash(
        name="restart",
        description="Restart currently playing track.",
        guild_ids=GUILD_IDS,
    )
    async def restart_command(self, ctx):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        await player.seek(0)
        await ctx.send("Track restarted.")

    @restart_command.error
    async def restart_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("There are no tracks in the queue.")

    @cog_ext.cog_slash(
        name="seek",
        description="Seek to nth minute in currently playing track.",
        guild_ids=GUILD_IDS,
    )
    async def seek_command(self, ctx, position: str):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        if not (match := re.match(self.time_regex, position)):
            raise InvalidTimeString

        if match.group(3):
            secs = (int(match.group(1)) * 60) + (int(match.group(3)))
        else:
            secs = int(match.group(1))

        await player.seek(secs * 1000)
        await ctx.send("Seeked.")


def setup(bot):

    bot.add_cog(Audio(bot))

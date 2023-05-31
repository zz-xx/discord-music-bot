from typing import Union
import re

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from wavelink.ext import spotify


class Play(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.soundcloud_playlist_regex = re.compile(
            r"^(https?:\/\/)?(www\.)?soundcloud\.com\/.*\/sets\/.*$"
        )
        self.soundcloud_track_regex = re.compile(
            r"^https:\/\/soundcloud\.com\/(?:[^\/]+\/){1}[^\/]+$"
        )
        self.youtube_playlist_regex = re.compile(
            r"(https://)(www\.)?(youtube\.com)\/(?:watch\?v=|playlist)?(?:.*)?&?(list=.*)"
        )
        self.youtube_track_regex = re.compile(
            r"^https?://(?:www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}$"
        )
        self.youtubemusic_track_regex = re.compile(
            r"(?:https?:\/\/)?(?:www\.)?(?:music\.)?youtube\.com\/(?:watch\?v=|playlist\?list=)[\w-]+"
        )

    @commands.hybrid_command(name="play", with_app_command=True)
    async def play(self, ctx: commands.Context, *, search: str):
        """Play a song with the given search query.
        If not connected, connect to our voice channel.

        Args:
            ctx (commands.Context): _description_
            search (str): _description_
        """

        if not ctx.author.voice:
            await ctx.send("You are not connected to any voice channel.")
            return

        if ctx.voice_client:
            if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                await ctx.send("Bot is already playing in a voice channel.")
                return

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(
                cls=wavelink.Player, self_deaf=True
            )
        else:
            vc: wavelink.Player = ctx.voice_client

        vc.autoplay = True

        if self.youtube_track_regex.match(search):
            track = (
                await vc.current_node.get_tracks(
                    cls=wavelink.YouTubeTrack, query=search
                )
            )[0]
            if vc.is_playing():
                await vc.queue.put_wait(track)
            else:
                await vc.play(track)
            await ctx.send(f"Added {track} to queue.")

        elif self.youtube_playlist_regex.match(search):
            playlist = await wavelink.YouTubePlaylist.search(search, return_first=True)
            for track in playlist.tracks:
                await vc.queue.put_wait(track)
            if not vc.is_playing():
                await vc.play(vc.queue.get())
            await ctx.send(f"Added {len(playlist.tracks)} tracks to queue.")

        elif "spotify.com" in search:
            decoded = spotify.decode_url(search)
            if decoded and decoded["type"] is not spotify.SpotifySearchType.unusable:
                if decoded["type"] is spotify.SpotifySearchType.playlist:
                    track_count = 0
                    async for track in spotify.SpotifyTrack.iterator(query=search):
                        track_count += 1
                        await vc.queue.put_wait(track)
                    if not vc.is_playing():
                        await vc.play(vc.queue.get())
                    await ctx.send(f"Added {track_count} tracks to queue.")

                elif decoded["type"] is spotify.SpotifySearchType.album:
                    track_count = 0
                    async for track in spotify.SpotifyTrack.iterator(query=search):
                        track_count += 1
                        await vc.queue.put_wait(track)
                    if not vc.is_playing():
                        await vc.play(vc.queue.get())
                    await ctx.send(f"Added {track_count} tracks to queue.")
                else:
                    track = await spotify.SpotifyTrack.search(search)
                    if vc.is_playing():
                        await vc.queue.put_wait(track)
                    else:
                        await vc.play(track)
                    await ctx.send(f"Added {track} to queue.")

        else:
            track = await wavelink.YouTubeTrack.search(search, return_first=True)
            if vc.is_playing():
                await vc.queue.put_wait(track)
            else:
                await vc.play(track)
            await ctx.send(f"Added {track} to queue.")

    @commands.hybrid_command(name="play-next", with_app_command=True)
    async def play_next_command(self, ctx: commands.Context, *, search: str):
        """Put this song next in queue, bypassing others.
        Args:
            ctx (commands.Context): _description_
            search (str): _description_
        """
        if not ctx.author.voice:
            await ctx.send("You are not connected to any voice channel.")
            return

        if ctx.voice_client is None:
            await ctx.send("Bot is not playing anything.")
            return
        else:
            # if ctx.voice_client:
            if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                await ctx.send("Bot is already playing in a voice channel.")
                return

        vc: wavelink.Player = ctx.voice_client

        if self.youtube_track_regex.match(search):
            track = (
                await vc.current_node.get_tracks(
                    cls=wavelink.YouTubeTrack, query=search
                )
            )[0]
            if vc.is_playing():
                vc.queue.put_at_front(track)
            else:
                await vc.play(track)
            await ctx.send(f"Added {track} to queue.")

        elif "spotify.com" in search:
            decoded = spotify.decode_url(search)
            if decoded and decoded["type"] is not spotify.SpotifySearchType.unusable:
                if decoded["type"] is spotify.SpotifySearchType.playlist:
                    await ctx.send(
                        "Can't add entire Spotify playlist using **play-next**."
                    )
                elif decoded["type"] is spotify.SpotifySearchType.album:
                    await ctx.send(
                        "Can't add entire Spotify album using **play-next**."
                    )
                else:
                    track = await spotify.SpotifyTrack.search(search)
                    if vc.is_playing():
                        vc.queue.put_at_front(track)
                    else:
                        await vc.play(track)
                    await ctx.send(f"Added {track} to queue.")

        else:
            track = await wavelink.YouTubeTrack.search(search, return_first=True)
            if vc.is_playing():
                vc.queue.put_at_front(track)
            else:
                await vc.play(track)

            await ctx.send(f"Added {track} to queue.")

    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Play(bot))

from typing import Union

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from wavelink.ext import spotify


class Play(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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

        await ctx.send(f"{search}")

        # this is spotify playlist or album
        if (
            "https://open.spotify.com/playlist" in search
            or "https://open.spotify.com/album" in search
        ):
            # this is spotify playlist
            if not ctx.voice_client:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(
                    cls=wavelink.Player, self_deaf=True
                )
                async for partial in spotify.SpotifyTrack.iterator(
                    query=search, partial_tracks=True
                ):
                    await self.add_spotify_track(ctx, partial)
            else:
                async for partial in spotify.SpotifyTrack.iterator(
                    query=search, partial_tracks=True
                ):
                    await self.add_track(ctx, partial)

        elif "https://www.youtube.com/playlist" in search:
            if not ctx.voice_client:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(
                    cls=wavelink.Player, self_deaf=True
                )
                playlist = await vc.node.get_playlist(wavelink.YouTubePlaylist, search)
                # print(playlist.tracks)

                if len(playlist.tracks) == 1:
                    track = await vc.play(playlist.tracks[0])
                    await ctx.send(f"Now playing: {track.title}")
                else:
                    track = await vc.play(playlist.tracks[0])
                    await ctx.send(f"Now playing: {track.title}")
                    for track in playlist.tracks[1:]:
                        await self.add_track(ctx, track)
            else:
                vc: wavelink.Player = ctx.voice_client
                playlist = await vc.node.get_playlist(wavelink.YouTubePlaylist, search)
                for track in playlist.tracks:
                    await self.add_track(ctx, track)

        else:
            partial = wavelink.PartialTrack(query=search, cls=wavelink.YouTubeTrack)
            if not ctx.voice_client:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(
                    cls=wavelink.Player, self_deaf=True
                )
                track = await vc.play(partial)
                await ctx.send(f"Now playing: {track.title}")
            else:
                await self.add_track(ctx, partial)

    @commands.hybrid_command(name="play-next", with_app_command=True)
    async def play_next(self, ctx: commands.Context, *, search: str):
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
            partial = wavelink.PartialTrack(query=search, cls=wavelink.YouTubeTrack)
            if not partial:
                await ctx.send("No tracks found.")
                return

            vc.queue.put_at_front(partial)
            await ctx.send(f"Playing {partial.title} next.")

            if not vc.is_playing() and not vc.queue.is_empty:
                await ctx.send(f"Now playing: {partial.title}")
                await vc.play(await vc.queue.get_wait())

    async def add_spotify_track(
        self, ctx: commands.Context, track: wavelink.PartialTrack
    ):
        """_summary_

        Args:
            ctx (commands.Context): _description_
            track (wavelink.PartialTrack): _description_
        """
        if not track:
            await ctx.send("No tracks found.")
            return

        vc: wavelink.Player = ctx.voice_client
        await vc.queue.put_wait(track)

        await ctx.send(f"Added {track.title} to the queue.", delete_after=20)

        if not vc.is_playing() and not vc.queue.is_empty:
            await ctx.send(f"Now playing: {track.title}")
            await vc.play(await vc.queue.get_wait())
        elif not vc.is_playing() and vc.queue.is_empty:
            await ctx.send(f"Now playing: {track.title}")
            await vc.play(track)

    async def add_track(
        self,
        ctx: commands.Context,
        track: Union[wavelink.PartialTrack, wavelink.YouTubeTrack],
    ):
        """_summary_

        Args:
            ctx (commands.Context): _description_
            track (Union[wavelink.PartialTrack, wavelink.YouTubeTrack]): _description_
        """
        if not track:
            await ctx.send("No tracks found.")
            return

        vc: wavelink.Player = ctx.voice_client
        await vc.queue.put_wait(track)

        await ctx.send(f"Added {track.title} to the queue.", delete_after=20)

        if not vc.is_playing() and not vc.queue.is_empty:
            await ctx.send(f"Now playing: {track.title}")
            await vc.play(await vc.queue.get_wait())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Play(bot))

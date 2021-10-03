from discord.ext.commands import CommandError
from discord_slash.error import SlashCommandError


class AlreadyConnectedToChannel(SlashCommandError, CommandError):
    pass


class NoVoiceChannel(SlashCommandError, CommandError):
    pass


class QueueIsEmpty(SlashCommandError, CommandError):
    pass


class NoTracksFound(SlashCommandError, CommandError):
    pass


class PlayerIsAlreadyPaused(SlashCommandError, CommandError):
    pass


class NoMoreTracks(SlashCommandError, CommandError):
    pass


class NoPreviousTracks(SlashCommandError, CommandError):
    pass


class InvalidRepeatMode(SlashCommandError, CommandError):
    pass


class VolumeTooLow(SlashCommandError, CommandError):
    pass


class VolumeTooHigh(SlashCommandError, CommandError):
    pass


class MaxVolume(SlashCommandError, CommandError):
    pass


class MinVolume(SlashCommandError, CommandError):
    pass


class NoLyricsFound(SlashCommandError, CommandError):
    pass


class InvalidEQPreset(SlashCommandError, CommandError):
    pass


class NonExistentEQBand(SlashCommandError, CommandError):
    pass


class EQGainOutOfBounds(SlashCommandError, CommandError):
    pass


class InvalidTimeString(SlashCommandError, CommandError):
    pass

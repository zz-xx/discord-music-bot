import discord
from discord.ext import commands
from discord_slash import cog_ext, MenuContext
from discord_slash.model import ContextMenuType


class TestCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    async def test(self, ctx):
        embed = discord.Embed(
                title="Test!",
                description="You are testing this command.",
                color=0xE02B2B
            )
        await ctx.send(embed=embed)
    
    @cog_ext.cog_slash(name="test", description="Test command.")
    async def test_slash(self, ctx):
       await self.test(ctx)
    
    @commands.command(name="test", description="Test command.", aliases=["t"])
    async def test_command(self, ctx):
        await self.test(ctx)
    
    @test_slash.error
    async def test_slash_error(self, ctx, exc):
        print("error handler")

    @test_command.error
    async def test_command_error(self, ctx, exc):
        print("error handler")
    

def setup(bot):
    bot.add_cog(TestCog(bot))

import discord
from discord.ext import commands
from discord_slash import cog_ext, MenuContext
from discord_slash.model import ContextMenuType

GUILD_IDS = [435683837641621514]

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
    
    @cog_ext.cog_slash(name="test", description="Test command.", guild_ids=GUILD_IDS)
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
    
    
    '''@cog_ext.cog_context_menu(
        target=ContextMenuType.MESSAGE, name="Example Message Menu", guild_ids=GUILD_IDS
    )
    async def example_message_menu(self, ctx: MenuContext):
        await ctx.send(
            f"This is a test. BTW, I know what you said. :)\n||{ctx.target_message.clean_content}||"
        )'''
    
    '''@cog_ext.cog_context_menu(target=ContextMenuType.USER, name="👻 Example User Menu", guild_ids=GUILD_IDS)
    async def example_user_menu(self, ctx: MenuContext):
        await ctx.send(
            f"{ctx.author.display_name} used the context menu on {ctx.target_author.display_name}!"
        )

        await ctx.send(str(type(ctx.target_author)))
        await ctx.send(str(ctx.target_author.id))

        #doesn't works, returns None
        try:
            await ctx.send(str(ctx.target_author.activity))
        except Exception:
            pass
        
        #workaround, returns  activity
        user = ctx.guild.get_member(ctx.target_author.id)
        await ctx.send(str(user.activity))'''
    

def setup(bot):
    bot.add_cog(TestCog(bot))

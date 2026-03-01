from discord import app_commands, Interaction
from discord.ext.commands import Context, command
import discord.ext.commands as commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def sync(self, ctx: Context) -> None:
        synced = await self.bot.tree.sync()
        await ctx.reply("{} commands synced".format(len(synced)))

    @app_commands.command(name="ping")
    async def ping_method(self, ctx: Interaction):
        await ctx.response.send_message("Pong!")
    
async def setup(bot):
    await bot.add_cog(Misc(bot))
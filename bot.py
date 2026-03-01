# ---------------- IMPORTS ----------------
import os
import discord
import discord.ext.commands as commands

# ---------------- BOT OBJECT ----------------

class Archiver(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.guild_messages = True
        intents.message_content = True
        super().__init__(intents=intents, command_prefix='/')

    async def setup_hook(self):
        for file in os.listdir(f'./cogs'):
            if file.endswith('.py'):
                await self.load_extension(f'cogs.{file[:-3]}')

    #### EVENTS ####
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

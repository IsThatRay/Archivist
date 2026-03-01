from discord import app_commands, Interaction, TextChannel, VoiceChannel, Thread, Colour, Embed, Interaction, File
from discord.ui import View, Button
import discord.ext.commands as commands
from typing import Union, Optional
from functools import partial
import types
import os
import datetime
from util.markdown import message_to_markdown, markdown_to_pdf

def fix_directory_name(path):
    return "".join((c for c in path if not c in "<>:\"/\\|?*"))

def timestamp_to_utc(argument):
    if not argument:
        return None
    if argument.startswith("<t:") and argument.endswith(">") and argument[3:-1].isnumeric():
        return datetime.datetime.fromtimestamp(int(argument[3:-1]), datetime.timezone.utc)
    else:
        print("Invalid arugment:", argument, "ignoring it.")
        return None

class Archiving(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def archive_channel(self, channel: Union[TextChannel, VoiceChannel, Thread], max_msgs: Union[int, None], start_timestamp: datetime.datetime, end_timestamp: datetime.datetime, button: Button, ctx: Interaction):
        await ctx.response.send_message(content="Starting Archive...", ephemeral=True)
        path = f"./archives/{channel.guild.name}/{fix_directory_name(channel.name)}/"
        if not os.path.exists(path):
            os.makedirs(path)

        filename = f"{fix_directory_name(channel.name)}"
        if start_timestamp:
            filename += start_timestamp.astimezone().strftime("_After_%Y-%m-%d-%I-%M%p")
        if end_timestamp:
            filename += end_timestamp.astimezone().strftime("_Before_%Y-%m-%d-%I-%M%p")
        filename += ".md"

        counter = 0

        print("Reading and writing messages...")
        with open(path + filename, "w", encoding="utf-8") as archive:
            last_author = None
            archive.write(f"# {channel.guild.name} - {channel.name} - Archive\n\n")
            async for message in channel.history(limit=max_msgs, after=start_timestamp, before=end_timestamp, oldest_first=True):
                if message.author != self.bot.user:
                    content = await message_to_markdown(message, path, message.author != last_author)
                    last_author = message.author

                    try:
                        archive.write(content + "\n\n")
                    except:
                        print(message.content)

                    counter += 1
                    if counter % 50 == 0:
                        print("Messages Read:", counter, end="\r")        
        
        print("Creating pdf...")
        await markdown_to_pdf(filename, path)
        print("Archive done!")
        await ctx.edit_original_response(content="Archive done!")

    @app_commands.command(name="archive", description="Start archiving the current channel")
    async def archive_method(self, ctx: Interaction, max_msgs: Optional[int] = None, start_timestamp: Optional[int] = None, end_timestamp: Optional[int] = None):
        embed = Embed(
            colour=Colour.dark_blue(),
            title="The Archivist opens their ancient tome...",
            description="Their eyes glistening with a crazed voracity, they gesture forth towards the great archive. She pushes forward a list of settings. \n\n\"Do the terms before you fit your desire?\""
        )

        start_timestamp = timestamp_to_utc(start_timestamp)
        end_timestamp = timestamp_to_utc(end_timestamp)

        embed.add_field(name="Channel", value=ctx.channel.name)
        embed.add_field(name="Message Limit", value=max_msgs if max_msgs else "No Limit")
        if start_timestamp:
            embed.add_field(name="Start Time", value=f"<t:{round(start_timestamp.timestamp())}>", inline=False)
        if end_timestamp:
            embed.add_field(name="End Timestamp", value=f"<t:{round(end_timestamp.timestamp())}>", inline=False)
        image = File("assets/Archivist.png", filename="Archivist.png")
        embed.set_image(url="attachment://Archivist.png")

        view = View()
        confirm_btn = Button(label="Looks Good!")
        confirm_btn.callback = types.MethodType(partial(self.archive_channel, ctx.channel, max_msgs+1 if max_msgs else max_msgs, start_timestamp, end_timestamp), confirm_btn)
        view.add_item(confirm_btn)

        await ctx.response.send_message(file=image, embed=embed, view=view)
    
async def setup(bot):
    await bot.add_cog(Archiving(bot))
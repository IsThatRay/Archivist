# Archivist - A Discord Channel Archive Bot

The Archivist, beckoned forth from a realm not too distance from our own, seeks one thing only: knowledge. They seek to form a symbiotic relationship
with you, offering the ability to archive your messages in trade for it expanding its own libary.

Archivist is a simple Discord tool which allows you to archive discord channels as Markdown or PDF files, useful to archive brainstorms, story writing, roleplay, or even just a particularly funny moment.

## Setup

Clone this repository to some folder.

Make sure you install Python 3.13 and also install the dependencies by running `pip install -U -r "requirements.txt"` inside this folder (or use the setup.bat file).

Create a new bot user through the Discord Developer portal https://discord.com/developers/applications 

Copy your bot application's ID and Secret and paste them in the indicated fields in the `secrets.json` file.

To run the bot, open up a terminal of some kind and run `./start.bat`

On first startup, you will need to sync your commands by typing `/sync` into the server where you added it. You may need to restart discord afterwards to see the commands appear.

## Usage

The bot operates using one slash command

/archive [max_msgs] [start_timestamp] [end_timestamp]

By default, the command will attempt to archive the entire channel defined. You can apply extra options using the command arguments.

max_msgs: Sets a hard limit of messages to archive to. Messages are archived from oldest message to newest message.

start_timestamp: Sets a timestamp where you want archiving to begin.

end_timestamp: Sets a timestamp where you want archiving to stop.

Timestamps are formatted using the discord timestamp notation <t_{unix_timestamp}>

Archives will be saved in the "archives" folder in the running directory.

import os
from os import getenv

import discord
from discord.ext import commands
from dotenv import load_dotenv


def load_cogs(client):
    for cog in [file.split(".")[0] for file in os.listdir("cogs") if file.endswith(".py")]:
        try:
            if cog != "__init__":
                client.load_extension(f"cogs.{cog}")
        except Exception as ex:
            print(ex)


# This is just temporary for testing reasoning
server_prefixes = {
    '535089248785924107': {
        'prefix': '!'
    }
}


def get_prefix(client, message):
    id = message.guild.id
    prefix = server_prefixes[str(id)]['prefix']

    # TODO: Implement database connection and a if the process fails a fallback prefix
    return prefix


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix)

        @self.event
        async def on_ready():
            load_cogs(self)
            await self.change_presence(
                activity=discord.Activity(name="Python code!", type=discord.ActivityType.watching))
            print(f"{self.user} logged in!")


if __name__ == "__main__":
    load_dotenv()

    client = Client()
    client.run(getenv("CLIENT_TOKEN"))

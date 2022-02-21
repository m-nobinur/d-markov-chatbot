"""
Name: d-markov-chatbot
Description: A discord bot that generates and sends messages based on Markov Chain Model.
Author: Mohammad Nobinur
Using https://github.com/DisnakeDev/disnake
API: http://disnake.readthedocs.io/en/latest/api.html
Copyright © m-nobinur 2022 - https://github.com/m-nobinur

"""

import os
from datetime import datetime

import disnake as discord
from disnake.ext import commands

from db import ChatDBManager


# ======= Set up the bot =======
BOT_TOKEN = ""
BOT_PREFIX = ">"
# ==============================


class ChatBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.remove_command("help")

        if not os.path.isdir("./data"):
            os.makedirs("./data")

        self.db = ChatDBManager("./data")

        for cog in ["setup", "info", "message"]:
            self.load_extension(f"cogs.{cog}")

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Game(f"Start with {self.command_prefix}help")
        )
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + f" 🟢 Bot is online.")

    async def on_connect(self):
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " 💬 Connected!")

    async def on_disconnect(self):
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " 🔴 Disconnected!")

    async def on_message(self, message):
        if message.guild is None:
            return
        await self.process_commands(message)


if __name__ == "__main__":

    bot = ChatBot(command_prefix=BOT_PREFIX, reconnect=True)

    bot.run(BOT_TOKEN)

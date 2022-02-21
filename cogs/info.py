import disnake as discord
from disnake.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        prefix = self.bot.command_prefix

        self.help_msg = {
            "chat": f"Usage:\n`{prefix}chat <channel mention>`\n\n*The bot need at least 30 messages to start chatting.*",
            "train": f"Usage:\n`{prefix}train <channel mention>`\n",
            "reset": "Reset the saved messages and the saved channels.",
            "info": "Show bot info.",
            "help": "Show the help message.",
        }

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def info(self, ctx):
        embed = discord.Embed(color=0x00FF00)

        conn, cur = await self.bot.db.create_connection(ctx.guild.id)

        train_channels = await self.bot.db.get_chat_channels(cur)
        chat_channels = await self.bot.db.get_train_channels(cur)
        _, total_messages, _ = await self.bot.db.get_full_text(cur)

        await self.bot.db.close_connection(conn, cur)

        learn, chat = [], []

        for channel_id in train_channels:
            channel = self.bot.get_channel(channel_id)
            learn.append(channel.mention)
        for channel_id in chat_channels:
            channel = self.bot.get_channel(channel_id)
            chat.append(channel.mention)

        learn = "\n".join(learn) if len(learn) > 0 else "None"
        chat = "\n".join(chat) if len(chat) > 0 else "None"

        if total_messages < 30:
            total_messages = (
                f"{total_messages}\n*At least send 30 messages to start chatting.*"
            )

        embed.add_field(
            name="Info",
            value=f"Total messages for this guild: {total_messages}\n\nTraining Channels:\n{learn}\n\nChatting Channels:\n{chat}",
        )
        embed.add_field(
            name="Bot Info",
            value=f"This is a discord bot based on Markov-Chain Model.",
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def help(self, ctx, cmd=None):
        prefix = self.bot.command_prefix

        embed = discord.Embed(color=0x00C8FF)

        for cmd in self.help_msg:
            embed.add_field(name=f"{prefix}{cmd}", value=self.help_msg[cmd])
        else:
            embed.add_field(
                name="Commands:",
                value=f"`chat`, `train`, `reset`, `info`, `help`.",
                inline=False,
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))

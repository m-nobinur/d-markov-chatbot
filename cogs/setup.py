import asyncio

import disnake as discord
from disnake.ext import commands


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.has_permissions(manage_channels=True)
    async def chat(self, ctx):
        if len(ctx.message.channel_mentions) == 0:
            await ctx.send(
                f"Use `{self.bot.command_prefix}chat <channel mention>` to set a chat channel."
            )
            return

        logs = []
        conn, cur = await self.bot.db.create_connection(ctx.guild.id)

        for channel in ctx.message.channel_mentions:
            if not isinstance(channel, discord.channel.TextChannel):
                logs.append(f"- {channel.mention} is not a text channel.")
                continue

            bot_permissions = channel.permissions_for(
                ctx.guild.get_member(self.bot.user.id)
            )
            if not bot_permissions.read_messages:
                logs.append(
                    f"- Bot does not have permission to read messages on {channel.mention}."
                )
                continue
            elif not bot_permissions.send_messages:
                logs.append(
                    f"- Bot does not have permission to send messages on {channel.mention}."
                )
                continue

            r = await self.bot.db.add_chat_channel(conn, cur, channel.id)

            if r == 1:
                logs.append(f"- {channel.mention} was added to the chatting channels.")
            elif r == 2:
                logs.append(f"- {channel.mention} was already saved.")
            else:
                logs.append(f"- You can only add up to 5 talking channels.")

        await self.bot.db.close_connection(conn, cur)

        await ctx.send(
            embed=discord.Embed(
                title="Action completed with the following logs:",
                description="\n".join(logs),
                color=0x00FF00,
            )
        )

    @commands.group(invoke_without_command=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.has_permissions(manage_channels=True)
    async def train(self, ctx):
        if len(ctx.message.channel_mentions) == 0:
            await ctx.send(
                f"Use `{self.bot.command_prefix}train #channel` to set a train channel."
            )
            return

        logs = []

        conn, cur = await self.bot.db.create_connection(ctx.guild.id)

        for channel in ctx.message.channel_mentions:
            if not isinstance(channel, discord.channel.TextChannel):
                logs.append(f"- {channel.mention} is not a text channel.")
                continue

            bot_permissions = channel.permissions_for(
                ctx.guild.get_member(self.bot.user.id)
            )
            if not bot_permissions.read_messages:
                logs.append(
                    f"- Bot does not have permission to read messages on {channel.mention}."
                )
                continue

            r = await self.bot.db.add_train_channel(conn, cur, channel.id)
            if r == 1:
                logs.append(
                    f"- {channel.mention} was added to the train channels list."
                )
            elif r == 2:
                logs.append(
                    f"- {channel.mention} was already in the train channels list."
                )
            else:
                logs.append(f"- You can only add up to 10 talking channels.")

        await self.bot.db.close_connection(conn, cur)

        await ctx.send(
            embed=discord.Embed(
                title="Action completed with the following logss:",
                description="\n".join(logs),
                color=0x00FF00,
            )
        )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @commands.has_permissions(manage_channels=True)
    async def reset(self, ctx):
        def check(message):
            return ctx.author == message.author and ctx.channel == message.channel

        prefix = self.bot.command_prefix

        await ctx.send(
            f"This action will reset all the data! Send `{prefix}yes` to confirm."
        )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await ctx.send("Time is over!")
        else:
            if not msg.content.lower() == f"{prefix}yes":
                await ctx.send("Action canceled!")
            else:
                conn, cur = await self.bot.db.create_connection(ctx.guild.id)
                await self.bot.db.reset_db(conn, cur)
                await self.bot.db.close_connection(conn, cur)

                await ctx.send("Done!")


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Can not execute the command.")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f'Missing permissions: `{", ".join(error.missing_perms)}`')
            return
        if isinstance(error, commands.BotMissingPermissions):
            if ctx.author.dm_channel is None:
                await ctx.author.create_dm()
            await ctx.author.send(
                f'I do not have permission to `{"` and `".join(error.missing_perms)}` in that channel.'
            )
            return
        if isinstance(error, commands.NotOwner):
            return
        raise error


def setup(bot):
    bot.add_cog(Setup(bot))
    bot.add_cog(ErrorHandler(bot))

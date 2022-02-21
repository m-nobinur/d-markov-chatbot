from disnake.ext import commands

from model import MarkovModel


class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.db.remove_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        conn, cur = await self.bot.db.create_connection(channel.guild.id)

        await self.bot.db.remove_talk_channel(conn, cur, channel.id)
        await self.bot.db.remove_learn_channel(conn, cur, channel.id)

        await self.bot.db.close_connection(conn, cur)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.is_system():
            return
        if message.guild is None:
            return
        if message.clean_content.startswith(self.bot.command_prefix): 
            return

        conn, cur = await self.bot.db.create_connection(message.guild.id)

        if await self.bot.db.is_train_channel(cur, message.channel.id):
            await self.bot.db.add_message_to_db(conn, cur, message.clean_content)
            return

        if await self.bot.db.is_chat_channel(cur, message.channel.id):
            async with message.channel.typing():
                text, total, last_msg = await self.bot.db.get_full_text(cur)
                markov_model = MarkovModel(text)
                chain = markov_model.create_markov_chain(markov_model.get_tokens(), 1)
                msg_len = len(last_msg.split())
                if total > 30:
                    if msg_len <= 20:
                        msg = markov_model.generate_text(chain, msg_len + 2)
                    else:
                        msg = markov_model.generate_text(chain, 20)
                else:
                    await message.channel.send("Add more messages to the training channels.")
                    await self.bot.db.close_connection(conn, cur)
                    return

                await message.channel.send(msg)

        await self.bot.db.close_connection(conn, cur)


def setup(bot):
    bot.add_cog(Message(bot))

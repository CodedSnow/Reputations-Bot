import asyncio

from discord import User, Embed, Message
from discord.ext import commands

from structures.MySQL import MySQL


class Rep(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["reputation", "reps"])
    @commands.guild_only()
    async def rep(self, ctx, *args: str):
        await ctx.message.delete()

        if len(args) == 0:
            return

        if args[0].lower() == "info":
            repUser: User = ctx.author

            if len(args) > 1:
                user_id = int(args[1].replace('<@', '').replace('>', '').replace('!', ''))
                repUser = self.client.get_user(user_id)

            mysql = MySQL()

            await mysql.connect(True)

            sql_query = "SELECT type FROM reputations WHERE guild = %s AND receiver = %s"
            sql_value_1 = str(ctx.guild.id)
            sql_value_2 = str(repUser.id)

            mysql.cursor.execute(sql_query, (sql_value_1, sql_value_2,))

            positive_amount = 0
            neutral_amount = 0
            negative_amount = 0

            data = mysql.cursor.fetchall()

            for rep in data:
                if rep[0].decode() == 'positive':
                    positive_amount += 1
                elif rep[0].decode() == 'neutral':
                    neutral_amount += 1
                elif rep[0].decode() == 'negative':
                    negative_amount += 1

            mysql.close()

            desc = "You can find information about " + repUser.display_name + "'s reputation below."
            if ctx.author.id == repUser.id:
                desc = "You can find information about your reputation below."

            await ctx.send(embed=Embed(title="Reputations - Rep", description=desc)
                           .add_field(name="Positive Points", value=positive_amount, inline=True)
                           .add_field(name="Neutral Points", value=neutral_amount, inline=True)
                           .add_field(name="Negative Points", value=negative_amount, inline=True)
                           .add_field(name="Latest Reputations", value="Coming Soon!", inline=False)
                           )

        elif args[0].lower() == "add":

            if len(args) < 2:
                await ctx.send("Please use !rep add <User>")
                return

            reputation_receiver_id = int(args[1].replace('<@', '').replace('>', '').replace('!', ''))
            reputation_receiver = self.client.get_user(reputation_receiver_id)
            if reputation_receiver is None:
                ctx.send('Please fill in a valid user.')
                return

            if reputation_receiver_id == ctx.author.id:
                ctx.send('You cannot give yourself a reputations point.')
                return

            msg: Message = await ctx.send(embed=Embed(
                title='Reputations - Rep',
                description='Which type of reputation would you like to give\n\n🟩 - Positive\n🟨 - Neutral\n🟥 - Negative')
            )

            await msg.add_reaction('🟩')
            await msg.add_reaction('🟨')
            await msg.add_reaction('🟥')

            def check(reaction, user):
                return user == ctx.author and (
                        str(reaction.emoji) == '🟩' or
                        str(reaction.emoji) == '🟨' or
                        str(reaction.emoji) == '🟥'
                )

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return

            await msg.clear_reactions()

            reputation_type = None

            if str(reaction.emoji) == '🟩':
                reputation_type = 'positive'
            elif str(reaction.emoji) == '🟨':
                reputation_type = 'neutral'
            elif str(reaction.emoji) == '🟥':
                reputation_type = 'negative'

            # TODO: Add the message you want to include within the reputation

            await msg.edit(embed=Embed(
                title='Reputations - Rep',
                description='Are you sure you want to give ' + reputation_receiver.display_name + ' a ' + reputation_type + ' reputation point?\n\n🟩 - Yes\n🟥 - No'
            ))

            await msg.add_reaction('🟩')
            await msg.add_reaction('🟥')

            def check(reaction, user):
                return user == ctx.author and (
                        str(reaction.emoji) == '🟩' or
                        str(reaction.emoji) == '🟥'
                )

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return

            await msg.clear_reactions()

            proceed: bool = False

            if str(reaction.emoji) == '🟩':
                proceed = True

            if proceed:
                await msg.edit(embed=Embed(
                    title='Reputations - Rep',
                    description='Success! The reputation was given!'
                ))

                # TODO: Write to the database

                await msg.delete(delay=5.5)
            else:
                await msg.edit(embed=Embed(
                    title='Reputations - Rep',
                    description='Alright! Process cancelled!'
                ))

                await msg.delete(delay=5.5)

                # TODO: Send the reputation receiver a private message


def setup(client):
    client.add_cog(Rep(client))

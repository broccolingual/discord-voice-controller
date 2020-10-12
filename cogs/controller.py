import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# StreamHandler作成
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(name)s:%(lineno)d:%(levelname)s:%(message)s'))
logger.addHandler(handler)

MUTE_EMOJI = '🔇'
UNMUTE_EMOJI = '🔊'
MUTE_IMG = 'https://gyazo.com/7223b5ee4dd77a5fbabc494310637b2a.png'
UNMUTE_IMG = 'https://gyazo.com/59956c195abd5c0e2f8cdd0496b1835c.png'


async def _mute(payload):
    vc = payload.guild.me.voice.channel
    for member in vc.members:
        await member.edit(mute=True)
    return vc


async def _unmute(payload):
    vc = payload.guild.me.voice.channel
    for member in vc.members:
        await member.edit(mute=False)
    return vc


class Controller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def voice_controller(self, ctx):

        if ctx.author.voice is None:
            await ctx.send(f'{ctx.author.mention}あなたはボイスチャンネルに接続していません。')
            logger.warning(f'{ctx.author.display_name} is not connected to a voice channel')
            return

        await ctx.author.voice.channel.connect()

        embed = discord.Embed(description=ctx.author.voice.channel.name, colour=ctx.author.color)
        embed.set_author(name='Voice Controller')
        embed.set_footer(text='リアクションでMute/Unmute切り替え')
        embed.set_thumbnail(url=UNMUTE_IMG)
        embed.add_field(name='Voice Status', value=f'{UNMUTE_EMOJI} unmute')
        panel = await ctx.send(embed=embed)
        await panel.add_reaction(MUTE_EMOJI)
        await panel.add_reaction(UNMUTE_EMOJI)
        logger.info('voice control panel was created')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return

        if before.channel is not None:
            if len(before.channel.members) == 1:
                if before.channel.members[0] == self.bot.user:
                    await before.channel.guild.voice_client.disconnect()
                    logger.info(f'bot was disconnected from {before.channel.name} channel[voice]')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        try:
            if user == self.bot.user:
                return

            if reaction.emoji == MUTE_EMOJI:
                await reaction.clear()
                msg = await reaction.message.channel.fetch_message(int(reaction.message.id))
                await msg.add_reaction(UNMUTE_EMOJI)

                if not msg.embeds:
                    return

                embed_before = msg.embeds[0]

                if embed_before.author.name != 'Voice Controller':
                    return

                embed_after = discord.Embed(
                    description=embed_before.description,
                    colour=embed_before.colour
                )
                embed_after.set_author(name=embed_before.author.name)
                embed_after.set_footer(text=embed_before.footer.text)
                embed_after.set_thumbnail(url=MUTE_IMG)
                embed_after.add_field(name=embed_before.fields[0].name,
                                      value=f'{MUTE_EMOJI} mute')

                vc = await _mute(reaction.message)  # MUTE
                await msg.edit(embed=embed_after)
                logger.info(f'{vc.name} channel[voice] users were muted')

            if reaction.emoji == UNMUTE_EMOJI:
                await reaction.clear()
                msg = await reaction.message.channel.fetch_message(int(reaction.message.id))
                await msg.add_reaction(MUTE_EMOJI)

                if not msg.embeds:
                    return

                embed_before = msg.embeds[0]

                if embed_before.author.name != 'Voice Controller':
                    return

                embed_after = discord.Embed(
                    description=embed_before.description,
                    colour=embed_before.colour
                )
                embed_after.set_author(name=embed_before.author.name)
                embed_after.set_footer(text=embed_before.footer.text)
                embed_after.set_thumbnail(url=UNMUTE_IMG)
                embed_after.add_field(name=embed_before.fields[0].name,
                                      value=f'{UNMUTE_EMOJI} unmute')

                vc = await _unmute(reaction.message)  # UNMUTE
                await msg.edit(embed=embed_after)
                logger.info(f'{vc.name} channel[voice] users were unmuted')

        except Exception as e:
            logger.error(e)
            return 


def setup(bot):
    bot.add_cog(Controller(bot))
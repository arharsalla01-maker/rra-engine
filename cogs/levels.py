import discord
from discord.ext import commands

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_data = {} # Se reinicia al apagar, conectar a DB luego

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        user_id = str(message.author.id)
        self.xp_data[user_id] = self.xp_data.get(user_id, 0) + 5 # 5 XP por mensaje

    @commands.command()
    async def rank(self, ctx):
        xp = self.xp_data.get(str(ctx.author.id), 0)
        await ctx.send(f"⭐ **{ctx.author.name}**, tienes **{xp} XP**.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Cambia el 0 por la ID de tu canal de bienvenida
        channel = member.guild.get_channel(00000000000) 
        if channel:
            embed = discord.Embed(title="👋 Bienvenido a ROLEPLAY RRA", color=discord.Color.gold())
            embed.set_image(url=member.display_avatar.url)
            embed.set_footer(text=f"Miembro #{member.guild.member_count}")
            await channel.send(embed=embed)

async def setup(bot): await bot.add_cog(Levels(bot))

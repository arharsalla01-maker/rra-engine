# XP y niveles
import discord
from discord.ext import commands
import database
import time

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldown = {}
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        # XP Cooldown
        user_id = message.author.id
        current_time = time.time()
        
        if user_id in self.xp_cooldown:
            if current_time - self.xp_cooldown[user_id] < 60:  # 60 segundos de cooldown
                return
        
        self.xp_cooldown[user_id] = current_time
        
        # Añadir XP (10 por mensaje)
        leveled_up = database.add_xp(user_id, 10)
        
        if leveled_up:
            level, xp = database.get_user_level(user_id)
            embed = discord.Embed(
                title='🎉 ¡Subiste de Nivel!',
                description=f'{message.author.mention} ahora está en nivel **{level}**',
                color=discord.Color.gold()
            )
            await message.channel.send(embed=embed)
    
    @commands.command(name='level')
    async def check_level(self, ctx, member: discord.Member = None):
        """Revisa tu nivel"""
        target = member or ctx.author
        level, xp = database.get_user_level(target.id)
        
        embed = discord.Embed(
            title=f'Estadísticas de {target.name}',
            color=discord.Color.blue()
        )
        embed.add_field(name='Nivel', value=level, inline=True)
        embed.add_field(name='XP Total', value=xp, inline=True)
        embed.add_field(name='XP para siguiente nivel', value=f'{(level * 100) - (xp % 100)}/100', inline=True)
        embed.set_thumbnail(url=target.avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx):
        """Muestra el leaderboard"""
        top_users = database.get_leaderboard(ctx.guild.id, 10)
        
        embed = discord.Embed(
            title='🏆 Leaderboard',
            color=discord.Color.gold()
        )
        
        description = ''
        for idx, (user_id, level, xp) in enumerate(top_users, 1):
            user = await self.bot.fetch_user(user_id)
            description += f'{idx}. {user.mention} - Nivel {level} ({xp} XP)\n'
        
        embed.description = description
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Levels(bot))

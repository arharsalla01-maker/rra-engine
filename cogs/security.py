# Anti-raid y Moderación
import discord
from discord.ext import commands
import database
import time

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_tracker = {}
        self.join_tracker = {}
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        
        # Anti-spam
        user_id = message.author.id
        current_time = time.time()
        
        if user_id not in self.spam_tracker:
            self.spam_tracker[user_id] = []
        
        # Limpiar mensajes antiguos (más de 10 segundos)
        self.spam_tracker[user_id] = [t for t in self.spam_tracker[user_id] if current_time - t < 10]
        
        self.spam_tracker[user_id].append(current_time)
        
        # Si hay más de 5 mensajes en 10 segundos
        if len(self.spam_tracker[user_id]) > 5:
            await message.delete()
            
            # Warn automático
            conn = __import__('sqlite3').connect('rra_engine.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO warns (user_id, guild_id, reason, moderator_id, warn_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, message.guild.id, 'Spam detectado', self.bot.user.id, int(current_time)))
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title='⚠️ Advertencia',
                description=f'{message.author.mention} fue advertido por Spam',
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed, delete_after=5)
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Anti-raid por joins
        guild_id = member.guild.id
        current_time = time.time()
        
        if guild_id not in self.join_tracker:
            self.join_tracker[guild_id] = []
        
        # Limpiar joins antiguos (más de 60 segundos)
        self.join_tracker[guild_id] = [t for t in self.join_tracker[guild_id] if current_time - t < 60]
        
        self.join_tracker[guild_id].append(current_time)
        
        # Si hay más de 10 joins en 60 segundos, activar modo lock
        if len(self.join_tracker[guild_id]) > 10:
            for channel in member.guild.text_channels:
                await channel.set_permissions(
                    member.guild.default_role,
                    send_messages=False
                )
            
            embed = discord.Embed(
                title='🚨 RAID DETECTADO',
                description='El servidor ha sido bloqueado temporalmente',
                color=discord.Color.red()
            )
            await member.guild.owner.send(embed=embed)
    
    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason: str = 'Sin razón'):
        """Advierte a un usuario"""
        conn = __import__('sqlite3').connect('rra_engine.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO warns (user_id, guild_id, reason, moderator_id, warn_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (member.id, ctx.guild.id, reason, ctx.author.id, int(time.time())))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title='⚠️ Usuario Advertido',
            description=f'{member.mention} fue advertido',
            color=discord.Color.orange()
        )
        embed.add_field(name='Razón', value=reason)
        await ctx.send(embed=embed)
    
    @commands.command(name='warns')
    async def check_warns(self, ctx, member: discord.Member = None):
        """Revisa las advertencias de un usuario"""
        target = member or ctx.author
        
        conn = __import__('sqlite3').connect('rra_engine.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT reason, moderator_id, warn_date FROM warns
            WHERE user_id = ? AND guild_id = ?
        ''', (target.id, ctx.guild.id))
        warns = cursor.fetchall()
        conn.close()
        
        embed = discord.Embed(
            title=f'Advertencias de {target.name}',
            color=discord.Color.red()
        )
        
        if warns:
            for idx, (reason, mod_id, warn_date) in enumerate(warns, 1):
                embed.add_field(
                    name=f'Advertencia #{idx}',
                    value=f'Razón: {reason}\nPor: <@{mod_id}>',
                    inline=False
                )
        else:
            embed.description = 'Este usuario no tiene advertencias'
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Security(bot))

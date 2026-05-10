# Sorteos y Drops
import discord
from discord.ext import commands, tasks
import database
import time
import random

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()
    
    @commands.command(name='giveaway')
    @commands.has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx, duration: int, winners: int, *, prize: str):
        """Crea un sorteo
        Uso: !giveaway <duración en segundos> <número de ganadores> <premio>
        """
        conn = __import__('sqlite3').connect('rra_engine.db')
        cursor = conn.cursor()
        
        end_time = int(time.time()) + duration
        
        cursor.execute('''
            INSERT INTO giveaways (guild_id, channel_id, prize, winners, end_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (ctx.guild.id, ctx.channel.id, prize, winners, end_time))
        
        conn.commit()
        giveaway_id = cursor.lastrowid
        conn.close()
        
        embed = discord.Embed(
            title='🎉 SORTEO',
            description=f'**Premio:** {prize}\n**Ganadores:** {winners}',
            color=discord.Color.gold()
        )
        embed.add_field(name='Termina en', value=f'<t:{end_time}:R>')
        embed.set_footer(text=f'ID: {giveaway_id}')
        
        message = await ctx.send(embed=embed)
        
        # Guardar message_id
        conn = __import__('sqlite3').connect('rra_engine.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE giveaways SET message_id = ? WHERE giveaway_id = ?', (message.id, giveaway_id))
        conn.commit()
        conn.close()
        
        await message.add_reaction('🎁')
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot or reaction.emoji != '🎁':
            return
        
        # Verificar si es un sorteo
        conn = __import__('sqlite3').connect('rra_engine.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT giveaway_id, participants FROM giveaways
            WHERE message_id = ? AND status = 'active'
        ''', (reaction.message.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            giveaway_id, participants = result
            participant_list = participants.split(',') if participants else []
            
            if str(user.id) not in participant_list:
                participant_list.append(str(user.id))
                
                conn = __import__('sqlite3').connect('rra_engine.db')
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE giveaways SET participants = ? WHERE giveaway_id = ?',
                    (','.join(participant_list), giveaway_id)
                )
                conn.commit()
                conn.close()
    
    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        """Verifica sorteos finalizados"""
        conn = __import__('sqlite3').connect('rra_engine.db')
        cursor = conn.cursor()
        current_time = int(time.time())
        
        cursor.execute('''
            SELECT giveaway_id, message_id, channel_id, guild_id, prize, winners, participants
            FROM giveaways
            WHERE end_time <= ? AND status = 'active'
        ''', (current_time,))
        
        finished_giveaways = cursor.fetchall()
        
        for giveaway_id, message_id, channel_id, guild_id, prize, winners_count, participants in finished_giveaways:
            participant_list = [int(p) for p in participants.split(',') if p]
            
            if participant_list:
                winners = random.sample(participant_list, min(winners_count, len(participant_list)))
            else:
                winners = []
            
            # Actualizar estado
            cursor.execute('UPDATE giveaways SET status = ? WHERE giveaway_id = ?', ('finished', giveaway_id))
            
            # Notificar ganadores
            guild = self.bot.get_guild(guild_id)
            if guild:
                channel = guild.get_channel(channel_id)
                try:
                    message = await channel.fetch_message(message_id)
                    
                    if winners:
                        winners_text = ' '.join([f'<@{w}>' for w in winners])
                        embed = discord.Embed(
                            title='🎉 ¡Sorteo Finalizado!',
                            description=f'**Ganadores:** {winners_text}\n**Premio:** {prize}',
                            color=discord.Color.gold()
                        )
                        await channel.send(embed=embed)
                    else:
                        await channel.send('⚠️ No hay participantes en el sorteo')
                    
                    await message.remove_reaction('🎁', self.bot.user)
                except:
                    pass
        
        conn.commit()
        conn.close()
    
    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Giveaways(bot))

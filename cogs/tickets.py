# Sistema de soporte, botones y modales
import discord
from discord.ext import commands
from discord import ui
import database

class TicketModal(ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(ui.TextInput(label='Describe tu problema', style=discord.TextStyle.paragraph, required=True))
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.value = self.children[0].value

class TicketButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label='Crear Ticket', style=discord.ButtonStyle.green, custom_id='create_ticket')
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        modal = TicketModal(title='Crear Ticket de Soporte')
        await interaction.response.send_modal(modal)
        
        # Esperar a que se envíe el modal
        await modal.wait()
        
        # Crear canal de ticket
        guild = interaction.guild
        ticket_id = database.create_ticket(interaction.user.id, 0)
        
        # Crear canal privado
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(
            f'ticket-{ticket_id}',
            overwrites=overwrites,
            category=interaction.guild.categories[0]
        )
        
        # Guardar channel_id en la DB
        conn = __import__('sqlite3').connect('rra_engine.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE tickets SET channel_id = ? WHERE ticket_id = ?', (channel.id, ticket_id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title=f'Ticket #{ticket_id}',
            description=f'Problema: {modal.value}',
            color=discord.Color.blue()
        )
        embed.add_field(name='Usuario', value=interaction.user.mention)
        
        view = ui.View()
        view.add_item(ui.Button(label='Cerrar Ticket', style=discord.ButtonStyle.red, custom_id=f'close_ticket_{ticket_id}'))
        
        await channel.send(embed=embed, view=view)
        await interaction.followup.send(f'✅ Ticket creado: {channel.mention}', ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx):
        """Configura el sistema de tickets"""
        embed = discord.Embed(
            title='Sistema de Tickets',
            description='Haz click en el botón para crear un ticket de soporte',
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=TicketButton())
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.data and 'custom_id' in interaction.data:
            custom_id = interaction.data['custom_id']
            
            if custom_id.startswith('close_ticket_'):
                ticket_id = int(custom_id.split('_')[2])
                database.close_ticket(ticket_id)
                
                await interaction.response.defer()
                channel = interaction.channel
                await channel.delete(reason='Ticket cerrado')

async def setup(bot):
    await bot.add_cog(Tickets(bot))

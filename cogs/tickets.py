import discord
from discord.ext import commands
from discord import app_commands

# --- MODAL PARA RECOGER DATOS ---
class TicketModal(discord.ui.Modal):
    def __init__(self, categoria, titulos_inputs):
        super().__init__(title=f"Soporte: {categoria}")
        self.categoria = categoria
        self.inputs = []
        
        for label in titulos_inputs:
            text_input = discord.ui.TextInput(
                label=label,
                style=discord.TextStyle.paragraph if len(titulos_inputs) == 1 else discord.TextStyle.short,
                required=True
            )
            self.add_item(text_input)
            self.inputs.append(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        
        # Crear el canal del ticket
        nombre_canal = f"ticket-{user.name}".lower()
        # Aquí definimos que el canal sea privado (solo staff y usuario al inicio, pero bloqueado)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=False), # No puede escribir aún
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(name=nombre_canal, overwrites=overwrites)
        
        await interaction.response.send_message(f"✅ Tu ticket ha sido creado en {channel.mention}", ephemeral=True)

        # Embed de Bienvenida dentro del Ticket
        embed = discord.Embed(
            title="👋 ¡Hola! Bienvenido a tu ticket",
            description=(
                "Gracias por contactar con **ROLEPLAY RRA**.\n\n"
                "Nuestro equipo ha sido notificado. Por favor, mantén la paciencia.\n"
                "━━━━━━━━━━━━━━━\n"
                "**Información proporcionada:**\n" + 
                "\n".join([f"**{i.label}:** {i.value}" for i in self.inputs])
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="RRA Engine • Esperando que un staff reclame...")

        # Botones de gestión
        view = TicketControlView()
        await channel.send(content=f"🔒 **Esperando que un miembro del STAFF reclame este ticket…**\n{user.mention}", embed=embed, view=view)

# --- BOTONES DENTRO DEL TICKET ---
class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="👋 Reclamar Ticket", style=discord.ButtonStyle.gray, custom_id="claim_ticket")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Lógica de reclamar: desbloquear chat para el usuario y el staff que reclama
        # (Aquí podrías añadir roles de staff específicos)
        await interaction.channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        # Desbloquear al usuario creador (buscándolo por el nombre del canal o mención)
        # Por ahora, simplemente activamos el canal:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        
        button.disabled = True
        button.label = f"Reclamado por {interaction.user.name}"
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"✅ El staff {interaction.user.mention} ha reclamado este ticket y ahora puede ayudarte.")

    @discord.ui.button(label="✖ Cerrar Solicitud", style=discord.ButtonStyle.primary, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cerrando ticket en 5 segundos...")
        await interaction.channel.delete() # Simple por ahora, luego añadimos valoración

# --- MENÚ DESPLEGABLE PRINCIPAL ---
class SoporteDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Soporte General", emoji="🎫", description="Dudas generales"),
            discord.SelectOption(label="Compras", emoji="💳", description="Problemas con la tienda"),
            discord.SelectOption(label="Bugs o Problemas", emoji="🐞", description="Reportar errores"),
            discord.SelectOption(label="Apelar Sanción", emoji="⚖️", description="Revisiones de ban/kick")
        ]
        super().__init__(placeholder="📂 Despliega el menú y elige una categoría", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Soporte General":
            await interaction.response.send_modal(TicketModal("Soporte General", ["¿Cuál es tu problema?"]))
        elif self.values[0] == "Compras":
            await interaction.response.send_modal(TicketModal("Compras", ["Nick del juego", "ID Transacción", "Correo", "Detalles"]))
        elif self.values[0] == "Bugs o Problemas":
            await interaction.response.send_modal(TicketModal("Bugs", ["Descripción del error"]))
        elif self.values[0] == "Apelar Sanción":
            await interaction.response.send_modal(TicketModal("Apelaciones", ["¿Qué hiciste?", "¿Quién te sancionó?", "Motivo de retiro"]))

class SoporteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SoporteDropdown())

# --- COMANDO PRINCIPAL ---
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="soporte")
    async def soporte(self, ctx):
        embed = discord.Embed(
            title="🎫 RRA ENGINE • CENTRO DE SOPORTE",
            description=(
                "Bienvenido al sistema oficial de soporte de **ROLEPLAY RRA**.\n\n"
                "• No hagas menciones innecesarias al STAFF\n"
                "• Mantén el respeto en todo momento\n"
                "• Explica tu problema claramente\n\n"
                "Selecciona una categoría en el menú desplegable para continuar."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="ESTE MENÚ ESTÁ EN FASE DE PRUEBA.")
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
            
        await ctx.send(embed=embed, view=SoporteView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))

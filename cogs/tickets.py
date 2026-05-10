 import discord
from discord.ext import commands
from discord import ui

class TicketModal(ui.Modal):
    def __init__(self, categoria, preguntas):
        super().__init__(title=f"RRA • {categoria}")
        self.preguntas = preguntas
        self.inputs = []
        for p in preguntas:
            i = ui.TextInput(label=p, style=discord.TextStyle.paragraph, required=True)
            self.add_item(i)
            self.inputs.append(i)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        
        # Crear canal privado
        channel = await guild.create_text_channel(
            name=f"🎫-{user.name}",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
        )
        
        embed = discord.Embed(title="🎫 RRA ENGINE • NUEVO TICKET", color=discord.Color.blue())
        for i in self.inputs:
            embed.add_field(name=i.label, value=i.value, inline=False)
        
        await channel.send(content=f"🔒 **Esperando que el STAFF reclame...**\n{user.mention}", embed=embed, view=TicketActions())
        await interaction.response.send_message(f"✅ Ticket creado en {channel.mention}", ephemeral=True)

class TicketActions(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="👋 Reclamar", style=discord.ButtonStyle.gray, custom_id="claim")
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.channel.set_permissions(interaction.user, send_messages=True)
        button.disabled = True
        button.label = f"Atendido por {interaction.user.name}"
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"✅ {interaction.user.mention} ha tomado tu caso.")

    @ui.button(label="✖ Cerrar", style=discord.ButtonStyle.danger, custom_id="close")
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        # Aquí se enviaría la transcripción al canal de logs (ID ajustable)
        await interaction.response.send_message("Cerrando ticket...")
        await interaction.channel.delete()

class Tickets(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command()
    async def soporte(self, ctx):
        embed = discord.Embed(title="🎫 RRA ENGINE • CENTRO DE SOPORTE", description="Selecciona una categoría para continuar.", color=discord.Color.blue())
        view = ui.View().add_item(SupportDropdown())
        await ctx.send(embed=embed, view=view)

class SupportDropdown(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Soporte General", emoji="🎫"),
            discord.SelectOption(label="Compras", emoji="💳"),
            discord.SelectOption(label="Bugs", emoji="🐞"),
            discord.SelectOption(label="Apelar Sanción", emoji="⚖️")
        ]
        super().__init__(placeholder="📂 Selecciona categoría...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Compras":
            await interaction.response.send_modal(TicketModal("Compras", ["Nick", "ID Transacción (TBX-ID)", "Detalles"]))
        elif self.values[0] == "Apelar Sanción":
            await interaction.response.send_modal(TicketModal("Apelación", ["¿Qué pasó?", "Staff que sancionó", "¿Por qué retirarla?"]))
        else:
            await interaction.response.send_modal(TicketModal(self.values[0], ["Describe tu problema detalladamente"]))

async def setup(bot): await bot.add_cog(Tickets(bot))

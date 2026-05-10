import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

class RRAEngine(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Cargamos los módulos de la carpeta cogs
        modulos = ['cogs.tickets', 'cogs.levels', 'cogs.security', 'cogs.giveaways']
        for modulo in modulos:
            try:
                await self.load_extension(modulo)
                print(f"✅ Cargado: {modulo}")
            except Exception as e:
                print(f"❌ Error en {modulo}: {e}")

    async def on_ready(self):
        print(f"━━━━━━━━━━━━━━━━━━━━━\n🤖 RRA ENGINE ONLINE\n━━━━━━━━━━━━━━━━━━━━━")
        await self.change_presence(activity=discord.Game(name="ROLEPLAY RRA | !soporte"))

bot = RRAEngine()
bot.run(os.getenv('TOKEN'))

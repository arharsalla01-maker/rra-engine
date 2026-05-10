import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Cargamos variables de entorno (.env)
load_dotenv()

class RRAEngine(commands.Bot):
    def __init__(self):
        # Configuramos intenciones (necesario para ver miembros y mensajes)
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Carga automática de todos los módulos en la carpeta /cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f'✅ Módulo cargado: {filename}')

    async def on_ready(self):
        print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        print(f'🤖 RRA ENGINE ONLINE')
        print(f'👤 Sesión iniciada como: {self.user.name}')
        print(f'🆔 ID: {self.user.id}')
        print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        
        # Estado del bot
        await self.change_presence(activity=discord.Game(name="ROLEPLAY RRA | !soporte"))

bot = RRAEngine()

if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))

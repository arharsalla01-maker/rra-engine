import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- 1. SERVIDOR WEB PARA RENDER (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "RRA Engine está funcionando 24/7"

def run():
    # Render usa el puerto 8080 por defecto para servicios web
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. CONFIGURACIÓN DEL BOT ---
load_dotenv()

class RRAEngine(commands.Bot):
    def __init__(self):
        # Intenciones necesarias para ver miembros, mensajes y reacciones
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Esto cargará automáticamente tus archivos en la carpeta /cogs
        # Asegúrate de que la carpeta existe y tiene los archivos .py
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Módulo cargado: {filename}')
                except Exception as e:
                    print(f'❌ Error al cargar {filename}: {e}')

    async def on_ready(self):
        print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        print(f'🤖 RRA ENGINE ONLINE (Con Web Server)')
        print(f'👤 Sesión: {self.user.name}')
        print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        await self.change_presence(activity=discord.Game(name="ROLEPLAY RRA | !soporte"))

# --- 3. EJECUCIÓN ---
bot = RRAEngine()

if __name__ == "__main__":
    keep_alive() # Esto arranca la "línea web" antes que el bot
    
    # En Render, el TOKEN se saca de las variables de entorno
    token = os.getenv('TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ ERROR: No se encontró el TOKEN en las variables de entorno.")

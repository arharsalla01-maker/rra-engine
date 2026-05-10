# Lógica de detección de texto (IA local)
import discord
from discord.ext import commands
from difflib import SequenceMatcher

class AIBrain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = {
            'hola': '¡Hola! 👋',
            'ayuda': 'Estoy aquí para ayudarte en el servidor',
            'gracias': 'De nada 😊',
            'adiós': 'Hasta luego 👋',
            'ping': 'Pong! 🏓',
            'bot': 'Soy el RRA-Engine, asistente del servidor',
        }
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula la similitud entre dos textos"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def find_best_response(self, user_input: str, threshold: float = 0.6) -> str:
        """Encuentra la mejor respuesta para el input del usuario"""
        user_input = user_input.lower().strip()
        
        best_match = None
        best_score = 0
        
        for keyword, response in self.responses.items():
            similarity = self.calculate_similarity(user_input, keyword)
            
            if similarity > best_score:
                best_score = similarity
                best_match = response
        
        if best_score >= threshold:
            return best_match
        
        return None
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        # Solo responder si menciona al bot
        if self.bot.user.mentioned_in(message):
            response = self.find_best_response(message.content)
            
            if response:
                await message.reply(response)
            else:
                await message.reply('No entiendo muy bien, pero estoy aquí para ayudarte 🤖')
    
    @commands.command(name='train')
    @commands.has_permissions(administrator=True)
    async def train_response(self, ctx, keyword: str, *, response: str):
        """Entrena una nueva respuesta"""
        self.responses[keyword.lower()] = response
        embed = discord.Embed(
            title='✅ Respuesta Añadida',
            description=f'Palabra clave: **{keyword}**\nRespuesta: **{response}**',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='responses')
    async def list_responses(self, ctx):
        """Lista todas las respuestas entrenadas"""
        embed = discord.Embed(
            title='📚 Respuestas Disponibles',
            color=discord.Color.blue()
        )
        
        for keyword, response in self.responses.items():
            embed.add_field(name=keyword, value=response, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AIBrain(bot))

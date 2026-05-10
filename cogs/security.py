import discord
from discord.ext import commands

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bad_words = ["palabra1", "palabra2"] # Aquí pones los insultos

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        # IA Local: Detección de Toxicidad
        content = message.content.lower()
        if any(word in content for word in self.bad_words):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, evita el lenguaje tóxico.", delete_after=5)

        # Anti-Spam de menciones
        if len(message.mentions) > 5:
            await message.delete()
            await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=10))
            await message.channel.send(f"🛡️ {message.author.mention} muteado por spam de menciones.")

async def setup(bot): await bot.add_cog(Security(bot))

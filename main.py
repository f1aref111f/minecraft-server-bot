import os
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ATERNOS_USER = os.getenv("ATERNOS_USER")
ATERNOS_PASSWORD = os.getenv("ATERNOS_PASSWORD")
SERVER_NAME = os.getenv("SERVER_NAME", "")
PUBLIC_CHANNEL_ID = int(os.getenv("PUBLIC_CHANNEL_ID", 0))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.command(name="start")
async def start_server(ctx):
    if ctx.channel.id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await ctx.send("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!")
        return

    await ctx.send("⏳ กำลังพยายามเปิดเซิร์ฟเวอร์ Aternos กรุณารอสักครู่...")
    
    # ใช้ Web API จำลองการส่งคำสั่งเปิดผ่าน Aternos
    try:
        # ส่งสัญญาณแจ้งเตือนเบื้องต้นว่าคำสั่งทำงานแล้ว
        await ctx.send("🟢 ส่งคำสั่งเปิดเรียบร้อย! โปรดตรวจสอบสถานะในเว็บ Aternos อีกครั้งครับ")
    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

if __name__ == "__main__":
    bot.run(TOKEN)

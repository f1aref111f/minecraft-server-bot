import os
import discord
from discord.ext import commands
from pyaternos import AternosAccount

# ดึงค่าจาก Environment Variables บน Render
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ATERNOS_USER = os.getenv("ATERNOS_USER")
ATERNOS_PASSWORD = os.getenv("ATERNOS_PASSWORD")
SERVER_NAME = os.getenv("SERVER_NAME")
PUBLIC_CHANNEL_ID = int(os.getenv("PUBLIC_CHANNEL_ID", 0))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 0))

# ตั้งค่าบอท Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ฟังก์ชันเชื่อมต่อ Aternos
def get_server():
    account = AternosAccount.from_credentials(ATERNOS_USER, Aternos_PASSWORD)
    servers = account.servers
    for s in servers:
        if SERVER_NAME.lower() in s.domain.lower() or SERVER_NAME.lower() in s.name.lower():
            return s
    return servers[0] # ถ้าไม่เจอชื่อ ให้เลือกเซิร์ฟเวอร์แรกสุด

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.command(name="start")
async def start_server(ctx):
    # เช็คว่ากดในห้องสาธารณะหรือห้องแอดมินไหม
    if ctx.channel.id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await ctx.send("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!")
        return

    await ctx.send("⏳ กำลังส่งคำสั่งเปิดเซิร์ฟเวอร์ Aternos กรุณารอสักครู่...")
    
    try:
        server = get_server()
        if server.status == "online":
            await ctx.send("⚠️ เซิร์ฟเวอร์เปิดทำงานอยู่แล้วครับ!")
        else:
            server.start()
            await ctx.send("🟢 กำลังเปิดเซิร์ฟเวอร์แล้ว! รอสักครู่สามารถกดเข้าเกมได้เลย")
    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

@bot.command(name="status")
async def server_status(ctx):
    if ctx.channel.id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        return

    try:
        server = get_server()
        status_text = f"สถานะเซิร์ฟเวอร์: **{server.status.upper()}** (ผู้เล่น: {server.players.current}/{server.players.max})"
        await ctx.send(status_text)
    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาดในการเช็คสถานะ: {str(e)}")

# รันบอท
if __name__ == "__main__":
    bot.run(TOKEN)

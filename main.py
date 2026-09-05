import os
import discord
from discord.ext import commands
from py_aternos import Client as AternosClient

# ตั้งค่า Discord Bot Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ตั้งค่าบัญชี Aternos ของคุณ (ดึงจาก Environment Variables ตอนเอาไปรันบน Render)
ATERNOS_USER = os.getenv("ATERNOS_USER")
ATERNOS_PASSWORD = os.getenv("ATERNOS_PASSWORD")
SERVER_NAME = os.getenv("SERVER_NAME") # ชื่อหรือ URL ของเซิร์ฟเวอร์ Aternos

# ตั้งค่า ID ของช่องดิสคอร์ด (นำไอดีมาใส่แทนที่เลข 0 ด้านล่าง)
PUBLIC_CHANNEL_ID = int(os.getenv("PUBLIC_CHANNEL_ID", "0"))  # ช่องสำหรับทุกคนกด Start
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", "0"))    # ช่องสำหรับแอดมิน (Start/Stop)

def get_server():
    aternos = AternosClient.from_credentials(ATERNOS_USER, AternosPASSWORD)
    servers = aternos.servers()
    for s in servers:
        if s.domain == SERVER_NAME or s.name.lower() == SERVER_NAME.lower():
            return s
    if servers:
        return servers[0]
    return None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready and connected to Discord!")

@bot.command(name="start")
async def start_server(ctx):
    # อนุญาตให้ใช้คำสั่ง Start ได้ทั้งช่อง Public และ Admin
    if ctx.channel.id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await ctx.send("❌ คุณไม่สามารถใช้คำสั่งนี้ในช่องนี้ได้ครับ!")
        return

    await ctx.send("⏳ กำลังส่งคำสั่งเปิดเซิร์ฟเวอร์ Aternos รอสักครู่นะครับ...")
    
    try:
        server = get_server()
        if server:
            server.start()
            await ctx.send("✅ ระบบได้ทำการสั่งเปิดเซิร์ฟเวอร์ Aternos เรียบร้อยแล้ว! (รอสักครู่เพื่อให้เซิร์ฟเวอร์บูทติด)")
        else:
            await ctx.send("❌ ไม่พบเซิร์ฟเวอร์ Aternos ที่ตั้งค่าไว้ กรุณาตรวจสอบชื่อเซิร์ฟเวอร์อีกครั้ง")
    except Exception as e:
        await ctx.send(f"⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อ Aternos: {str(e)}")

@bot.command(name="stop")
async def stop_server(ctx):
    # คำสั่ง Stop ต้องใช้ในช่อง Admin เท่านั้นเพื่อความปลอดภัย
    if ctx.channel.id != ADMIN_CHANNEL_ID:
        await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในช่องแอดมินเท่านั้น!")
        return

    await ctx.send("⏳ กำลังส่งคำสั่งปิดเซิร์ฟเวอร์...")
    
    try:
        server = get_server()
        if server:
            server.stop()
            await ctx.send("🛑 สั่งปิดเซิร์ฟเวอร์ Aternos เรียบร้อยแล้วครับ")
        else:
            await ctx.send("❌ ไม่พบเซิร์ฟเวอร์ Aternos")
    except Exception as e:
        await ctx.send(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")

# ดึง Token ของบอทจาก Environment Variables ของ Render
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: ไม่พบ DISCORD_BOT_TOKEN กรุณาตั้งค่าใน Environment Variables")
  

import os
import discord
from discord.ext import commands
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. ส่วนจำลองเว็บเซิร์ฟเวอร์เพื่อให้ Render ตรวจพบพอร์ต ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# รันเว็บเซิร์ฟเวอร์เบื้องหลัง
threading.Thread(target=run_web, daemon=True).start()

# --- 2. ส่วนตั้งค่าบอท Discord ---
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
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

    await ctx.send("⏳ กำลังส่งคำสั่งเปิดเซิร์ฟเวอร์ กรุณารอสักครู่...")
    try:
        await ctx.send("🟢 ส่งคำสั่งทำงานสำเร็จ! โปรดตรวจสอบสถานะในดิสคอร์ดหรือหน้าเว็บ Aternos อีกครั้งครับ")
    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

@bot.command(name="status")
async def server_status(ctx):
    if ctx.channel.id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        return
    await ctx.send("📊 สถานะบอทออนไลน์และพร้อมทำงานปกติครับ!")

# รันบอท
if __name__ == "__main__":
    bot.run(TOKEN)

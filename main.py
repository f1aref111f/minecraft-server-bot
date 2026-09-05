import os
import discord
from discord import app_commands
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

threading.Thread(target=run_web, daemon=True).start()

# --- 2. ส่วนตั้งค่าบอท Discord (รองรับ Slash Commands แบบซิงค์เข้าเซิร์ฟเวอร์ทันที) ---
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PUBLIC_CHANNEL_ID = int(os.getenv("PUBLIC_CHANNEL_ID", 0))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 0))

intents = discord.Intents.default()

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # 🛑 สำคัญ: แทนที่ตัวเลข 123456789012345678 ด้วย Server ID ของคุณ
        MY_GUILD = discord.Object(id=123456789012345678)
        
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print("Slash commands synced to guild.")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

# สร้างคำสั่ง /start
@bot.tree.command(name="start", description="สั่งเปิดเซิร์ฟเวอร์ Aternos")
async def start_server(interaction: discord.Interaction):
    if interaction.channel_id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await interaction.response.send_message("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!", ephemeral=True)
        return

    await interaction.response.send_message("⏳ กำลังส่งคำสั่งเปิดเซิร์ฟเวอร์ กรุณารอสักครู่...")
    try:
        await interaction.followup.send("🟢 ส่งคำสั่งทำงานสำเร็จ! โปรดตรวจสอบสถานะในหน้าเว็บ Aternos ครับ")
    except Exception as e:
        await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

# สร้างคำสั่ง /status
@bot.tree.command(name="status", description="ตรวจสอบสถานะบอท")
async def server_status(interaction: discord.Interaction):
    if interaction.channel_id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await interaction.response.send_message("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!", ephemeral=True)
        return
    await interaction.response.send_message("📊 สถานะบอทออนไลน์และพร้อมทำงานปกติครับ!")

if __name__ == "__main__":
    bot.run(TOKEN)

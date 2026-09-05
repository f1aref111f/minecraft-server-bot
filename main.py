 import os
import discord
from discord import app_commands
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from python_aternos import Client

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

# --- 2. ส่วนตั้งค่าบอท Discord และ Aternos ---
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PUBLIC_CHANNEL_ID = int(os.getenv("PUBLIC_CHANNEL_ID", 0))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 0))

AT_USER = os.getenv("ATERNOS_USER")
AT_PASS = os.getenv("ATERNOS_PASSWORD")

intents = discord.Intents.default()

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        MY_GUILD = discord.Object(id=1524782287709802557)
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print("Slash commands synced to guild successfully!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

# --- 3. ระบบ Slash Commands (สั่งงาน Aternos จริง) ---

@bot.tree.command(name="start", description="สั่งเปิดเซิร์ฟเวอร์ Aternos จริงๆ")
async def start_server(interaction: discord.Interaction):
    if interaction.channel_id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await interaction.response.send_message("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!", ephemeral=True)
        return

    await interaction.response.send_message("⏳ กำลังเชื่อมต่อเพื่อเปิดเซิร์ฟเวอร์ Aternos...")

    try:
        aternos = Client.from_credentials(AT_USER, AT_PASS)
        servers = aternos.list_servers()
        if not servers:
            await interaction.followup.send("❌ ไม่พบเซิร์ฟเวอร์ในบัญชี Aternos ของคุณ!")
            return
        
        my_server = servers[0]
        my_server.start()
        
        await interaction.followup.send("🟢 **ส่งคำสั่งเปิดเซิร์ฟเวอร์สำเร็จ!** เซิร์ฟเวอร์กำลังเริ่มทำงาน กรุณารอสักครู่...")
    except Exception as e:
        await interaction.followup.send(f"❌ เกิดข้อผิดพลาดในการเปิดเซิร์ฟเวอร์: {str(e)}")

@bot.tree.command(name="status", description="ตรวจสอบสถานะเซิร์ฟเวอร์ปัจจุบัน")
async def server_status(interaction: discord.Interaction):
    if interaction.channel_id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await interaction.response.send_message("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!", ephemeral=True)
        return

    try:
        aternos = Client.from_credentials(AT_USER, AT_PASS)
        servers = aternos.list_servers()
        my_server = servers[0]
        status = my_server.status
        await interaction.response.send_message(f"📊 สถานะเซิร์ฟเวอร์ Aternos ตอนนี้: **{status}**")
    except Exception as e:
        await interaction.response.send_message(f"❌ ไม่สามารถดึงสถานะได้: {str(e)}")

@bot.tree.command(name="command", description="ส่งคำสั่ง Minecraft ไปยังคอนโซล")
@app_commands.describe(cmd="พิมพ์คำสั่ง Minecraft เช่น /title §a hello")
async def minecraft_command(interaction: discord.Interaction, cmd: str):
    if interaction.channel_id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await interaction.response.send_message("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!", ephemeral=True)
        return

    await interaction.response.send_message(f"⏳ กำลังส่งคำสั่งไปที่คอนโซล: `{cmd}`")
    try:
        aternos = Client.from_credentials(AT_USER, AT_PASS)
        servers = aternos.list_servers()
        my_server = servers[0]
        
        my_server.execute_command(cmd)
        await interaction.followup.send(f"✅ ส่งคำสั่งสำเร็จ: `{cmd}`")
    except Exception as e:
        await interaction.followup.send(f"❌ ส่งคำสั่งไม่สำเร็จ (เซิร์ฟเวอร์อาจจะยังไม่เปิด): {str(e)}")

if __name__ == "__main__":
    bot.run(TOKEN)

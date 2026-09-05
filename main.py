import os
import discord
from discord import app_commands
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. ส่วนเว็บเซิร์ฟเวอร์สำหรับ Render ---
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

# --- 2. ตั้งค่าบอท Discord ---
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PUBLIC_CHANNEL_ID = int(os.getenv("PUBLIC_CHANNEL_ID", 0))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 0))

intents = discord.Intents.default()

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        MY_GUILD = discord.Object(id=1524782287709802557)
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print("Slash commands synced successfully!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

# --- 3. คำสั่งต่างๆ ---

@bot.tree.command(name="start", description="แจ้งเตือนการเปิดเซิร์ฟเวอร์")
async def start_server(interaction: discord.Interaction):
    if interaction.channel_id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await interaction.response.send_message("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!", ephemeral=True)
        return
    await interaction.response.send_message("🟢 กรุณากดปุ่มเปิดเซิร์ฟเวอร์ที่เว็บ Aternos ของคุณได้เลยครับ!")

@bot.tree.command(name="status", description="ตรวจสอบสถานะบอท")
async def server_status(interaction: discord.Interaction):
    if interaction.channel_id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await interaction.response.send_message("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!", ephemeral=True)
        return
    await interaction.response.send_message("📊 บอทออนไลน์และพร้อมทำงานปกติครับ!")

@bot.tree.command(name="command", description="ส่งคำสั่ง Minecraft เช่น /title §a hello")
@app_commands.describe(cmd="พิมพ์คำสั่ง Minecraft ที่ต้องการ")
async def minecraft_command(interaction: discord.Interaction, cmd: str):
    if interaction.channel_id not in [PUBLIC_CHANNEL_ID, ADMIN_CHANNEL_ID]:
        await interaction.response.send_message("❌ คุณไม่สามารถใช้คำสั่งนี้ในห้องนี้ได้!", ephemeral=True)
        return

    # บันทึกคำสั่งเพื่อนำไปใช้ในคอนโซลเกม
    await interaction.response.send_message(f"✅ บันทึกคำสั่งสำเร็จ: `{cmd}`\n*(คุณสามารถนำคำสั่งนี้ไปรันในคอนโซลหรือในเกมได้ทันที)*")

if __name__ == "__main__":
    bot.run(TOKEN)

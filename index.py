import discord
from discord.ext import commands
from discord.utils import get
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import io

# Setup the bot with command prefix '-'
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.guilds = True
intents.messages = True
bot = commands.Bot(command_prefix='-', intents=intents)

# IDs for channels and roles
WELCOME_CHANNEL_ID = 1256531648120492032
CONFESSION_CHANNEL_ID = 1256581166161592330
MOD_LOG_CHANNEL_ID = 971355896917659658
VERIFICATION_CHANNEL_ID = 971345144236363816
RULES_CHANNEL_ID = 971347449614569502
VERIFICATION_MESSAGE_ID = None 
MODERATOR_ROLE_ID = [748841518240104450, 781136798155145218] 
VERIFIED_ROLE_ID = 971355969818882078

# Check if the user has any of the moderator roles
def is_moderator():
    def predicate(ctx):
        return any(role.id in MODERATOR_ROLE_ID for role in ctx.author.roles)
    return commands.check(predicate)

# Send welcome GIF
async def send_welcome_gif(channel):
    with open("img/welcome.gif", "rb") as gif_file:
        await channel.send(file=discord.File(gif_file, 'welcome.gif'))

# Send welcome message
async def send_welcome_message(channel, member):
    verification_channel = bot.get_channel(VERIFICATION_CHANNEL_ID)
    rules_channel = bot.get_channel(RULES_CHANNEL_ID)
    message = (f"Welcome to sick's lair {member.name}!\n"
               f"Please read {verification_channel.mention} for verification and "
               f"{rules_channel.mention} for server's rules.\n"
               "Thank you and enjoy in our server!")
    await channel.send(message)

# Send verification message
@bot.event
async def on_ready():
    global VERIFICATION_MESSAGE_ID
    verification_channel = bot.get_channel(VERIFICATION_CHANNEL_ID)
    if verification_channel:
        message = await verification_channel.send(
            "React to this message to verify and gain access to the rest of the server!"
        )
        VERIFICATION_MESSAGE_ID = message.id
        await message.add_reaction("✅")
    print(f'Logged in as {bot.user}')

# New member join
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await send_welcome_gif(channel)
        await send_welcome_message(channel, member)

# Reactions for verification
@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == VERIFICATION_MESSAGE_ID and str(payload.emoji) == "✅":
        if payload.user_id == bot.user.id:
            return  # Ignore reactions from the bot itself
        
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            try:
                member = await guild.fetch_member(payload.user_id)
            except discord.NotFound:
                print(f"Member with ID {payload.user_id} not found.")
                return
        
        verified_role = guild.get_role(VERIFIED_ROLE_ID)
        if verified_role:
            await member.add_roles(verified_role)
            try:
                dm_channel = await member.create_dm()  # Corrected line
                await dm_channel.send("You have been verified and given access to the server!")
            except discord.Forbidden:
                pass  
            except AttributeError as e:
                print(f"AttributeError: {e}")

# Kick command
@bot.command()
@is_moderator()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked for: {reason}')

# Ban command
@bot.command()
@is_moderator()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned for: {reason}')

# Add role command
@bot.command()
@is_moderator()
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f'Role {role} has been added to {member}')

# Remove role command
@bot.command()
@is_moderator()
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f'Role {role} has been removed from {member}')

# Confession command
@bot.command()
async def confess(ctx, *, confession):
    confession_channel = bot.get_channel(CONFESSION_CHANNEL_ID)
    mod_log_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)

    if confession_channel and mod_log_channel:
        await confession_channel.send(f'Anonymous confession: {confession}')
        await mod_log_channel.send(f'Confession by {ctx.author}: {confession}')

    await ctx.send('Your confession has been sent.')

# Error handler for missing permissions
@kick.error
@ban.error
@addrole.error
@removerole.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have permission to use this command.")
    else:
        await ctx.send("An error occurred while processing the command.")

bot.run('MTI1NjU3OTQ1MTU0Njc2NzQ5MA.GfHPHu.-ct_6NyPE3N-JClHgdvaQw_cpHAnkhN7pn1dvE')

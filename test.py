import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import requests
import youtube_dl

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.command(name="play", help="Play audio from a SoundCloud link. YouTube has most videos blocked from streaming.")
async def play(bot, url):
    if bot.voice_client is None:
        await ctx.send("I'm not in a voice channel. Use /join to make me join a channel.")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        url2 = info_dict['formats'][0]['url']
        bot.voice_client.stop()
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        bot.voice_client.play(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS))

@bot.command(name="stop", help="Stop playing audio.")
async def stop(bot):
    voice_channel = bot.message.guild.voice_client
    if voice_channel.is_playing():
        voice_channel.stop()
    await voice_channel.disconnect()

@bot.command(name="joinvc")
async def join_vc(bot):
    channel = bot.author.voice.channel
    await channel.connect()
    await bot.send(f"Joined {channel.name}!")

@bot.command(name="leavevc")
async def leave_vc(bot):
    voice_channel = discord.utils.get(bot.voice_clients, guild=bot.guild)
    if voice_channel:
        await voice_channel.disconnect()
        await bot.send("Left voice channel.")
    else:
        await bot.send("Not in a voice channel.")

@bot.event
async def on_message(message):
    if message.channel.name == "bot-commands" and message.content.lower().startswith("hi boombapbot"):
        await message.channel.send("Hello! I'm BoombapBot. How can I help you?")
    await bot.process_commands(message)

def print_roles():
    for guild in bot.guilds:
            homies_role = discord.utils.get(guild.roles, name="homies")
            if homies_role:
                print(f"  Users in the 'homies' role:")
                for member in guild.members:
                    if homies_role in member.roles:
                        print(f"    {member.name}")

def main():
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name}")
        print_roles()

    bot.run(token)
        
if __name__ == '__main__':
    with open("./twitchclient.secret", "r") as twitch_file, open("./auth-token.secret", "r") as token_file:
        twitch_client_id = twitch_file.read().strip()
        token = token_file.read().strip()
    main()


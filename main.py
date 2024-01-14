import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import requests
import youtube_dl
import asyncio

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

queue = []

@bot.command(name="play", help="Play audio from a SoundCloud link.")
async def play(bot, url):
    if bot.voice_client is None or not bot.voice_client.is_connected():
        await join_vc(bot)

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

        if 'entries' in info_dict:  # Check if it's a playlist
            entries = info_dict['entries']
            print(entries)
            queue.extend(entries)
            await play_next(bot)
        else:  # It's a single track
            url2 = info_dict['formats'][0]['url']
            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }
            bot.voice_client.play(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS))

async def play_next(bot):
    if len(queue) > 1:
        entry = queue[0]
        url = entry['formats'][0]['url']
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        queue.pop(0)
        # Use after parameter to recursively call the play_next method for each track
        bot.voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: asyncio.run(play_next(bot)))  
    else:
        entry = queue[0]
        url2 = entry['formats'][0]['url']
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        bot.voice_client.play(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS))

@bot.command(name="pause")
async def pause(bot):
    voice_channel = bot.guild.voice_client
    if voice_channel.is_playing():
        voice_channel.pause()
    else:
        await bot.send("No audio is playing.")

@bot.command(name="resume")
async def resume(bot):
    voice_channel = bot.guild.voice_client
    voice_channel.resume()

@bot.command(name="joinvc")
async def join_vc(bot):
    channel = bot.author.voice.channel
    await channel.connect()

@bot.command(name="leavevc")
async def leave_vc(bot):
    if bot.voice_client is not None and bot.voice_client.is_connected():
        await bot.voice_client.disconnect()
    else:
        await bot.send("Im am not connected to a voice channel.")

def main():
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name}")    

    bot.run(token)
        
if __name__ == '__main__':
    with open("./twitchclient.secret", "r") as twitch_file, open("./auth-token.secret", "r") as token_file:
        twitch_client_id = twitch_file.read().strip()
        token = token_file.read().strip()
    main()

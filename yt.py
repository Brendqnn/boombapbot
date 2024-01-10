@bot.command(name="play")
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

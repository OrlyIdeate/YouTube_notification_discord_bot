import discord
import os
import requests
from googleapiclient.discovery import build
from discord.ext import tasks
from dotenv import load_dotenv

# .envファイルから環境変数をロード
load_dotenv()

# 環境変数の取得
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
DISCORD_USER_IDS = os.getenv('DISCORD_USER_IDS').split(',')

# YouTube APIクライアントの設定
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Discordクライアントの設定
client = discord.Client(intents=discord.Intents.default())

# 最新の動画IDを保存する変数
latest_video_id = None


@tasks.loop(minutes=30)
async def check_new_video():
	global latest_video_id
	request = youtube.search().list(
		part='snippet',
		channelId=CHANNEL_ID,
		order='date',
		maxResults=1
	)
	response = request.execute()
	video_id = response['items'][0]['id']['videoId']

	if video_id != latest_video_id:
		latest_video_id = video_id
		video_title = response['items'][0]['snippet']['title']
		video_url = f'https://www.youtube.com/watch?v={video_id}'

		for user_id in DISCORD_USER_IDS:
			user = await client.fetch_user(int(user_id))
			if user is not None:
				await user.send(f'新しい動画がアップされました: {video_title}\n{video_url}')
			else:
				print(f'ユーザーが見つかりません: {user_id}')



@client.event
async def on_ready():
	print(f'Logged in as {client.user}')
	check_new_video.start()

client.run(DISCORD_BOT_TOKEN)

import discord, os, sys
from discord.ext import commands, tasks
from itertools import cycle

import requests
import random

# 명령어 설정
bot = commands.Bot(command_prefix = '복실아 ') 

# 유튜브 API키 설정
yt_api_key = os.environ['yt_api_key']

# 상태 메시지 리스트
playing = cycle(['남자친구랑 BL 감상', '여자친구랑 공부', '유튜브 시청', '여자친구랑 데이트', '여자친구랑 디씨', '여자친구랑 트위터'])

# 금지어
bad_word = ['씨발', '시발', '개새끼', '병신', '느금']

# 젠더 혐오발언
gender_hate = ['한남', '소추', '한녀', '김치녀']

# 노래추천 플레이리스트
pl_ids = {
'ff' : {
  '칼바람곡' : 'PLvQ2Ez_GF9ibjUabkEvFE1JPANErbsEj5',
  '롤곡' : 'PLvQ2Ez_GF9iZI_wXMLU0GZ6cisl5lM8b3',
  '오타쿠감성' : 'PLvQ2Ez_GF9ibBCPBxCzriMM6c5b6Pznc4'
},
'dm' : {
  '씹덕' : 'PLfjCwAm4j422tRqJ7SIeKP5MGmWqV-CaR'
},
'jm' : {
  '띵곡' : 'PLwctH09-BYf1zsD8FPeDVm6xjEKS9zkAn'
}}

# 현재 상태
doing_now = ''

# 1시간마다 상태 변경
@tasks.loop(hours=1)
async def change_status():  
  doing_now = next(playing)
  await bot.change_presence(activity=discord.Game(doing_now))

@bot.event
async def on_ready():
  change_status.start() 
  print(f'--- 연결 성공 ---')
  print(f'봇 이름: {bot.user.name}')

# 인사
@bot.command(name='안녕')
async def hello(ctx):
  await ctx.send('안녕')

# 머해
@bot.command(name='뭐해')
async def doing(ctx):
  await ctx.send(doing_now + '하고 있어')

# 금지어들 알려주기
@bot.command(name='금지어')
async def ban_word(ctx):
  notice = '금지어는 '
  for word in bad_word:
    notice += '\"'
    notice += word
    notice += '\", '
  for word in gender_hate:
    notice += '\"'
    notice += word
    notice += '\", '
  notice = notice[:-2]
  notice += ' 이상이야'
  await ctx.send(notice)

# 노래 추천
def song_recmd(name, name_initial, pl_title):  
  if pl_title in pl_ids[name_initial].keys():
    pl_id = pl_ids[name_initial][pl_title]
  else:
    notice = name + '의 재생목록은'
    for word in pl_ids[name_initial].keys():
      notice += '\n * '
      notice += word
    notice += '\n이상이야' 
    return notice   
  get_pl_url = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=' + pl_id + '&maxResults=50&key=' + yt_api_key
  pl_items = requests.get(get_pl_url).json()['items']
  item_vids = []
  for item in pl_items:
      item_vids.append('https://www.youtube.com/watch?v=' + item['snippet']['resourceId']['videoId'] + '&list=' + pl_id)
  return item_vids[random.randint(0, len(pl_items) - 1)]

@bot.command(name='복실추천곡')
async def ff_song_recmd(ctx, pl_title = ''):
  await ctx.send(song_recmd('복실이', 'ff', pl_title))  
  await ctx.send('이 노래는 어때?')

@bot.command(name='돌몽추천곡')
async def dm_song_recmd(ctx, pl_title = ''):
  await ctx.send(song_recmd('돌몽이', 'dm', pl_title))  
  await ctx.send('돌몽 : (대충 란 내 노래를 들어 콘)')

@bot.command(name='진목추천곡')
async def jm_song_recmd(ctx, pl_title = ''):
  await ctx.send(song_recmd('진목이', 'jm', pl_title))  
  await ctx.send('진목 : 띵곡이다 들어라')

# 글삭튀 검거
@bot.event
async def on_message_delete(message):
  bad = False
  ban_word = bad_word + gender_hate
  for word in ban_word:
    if word in message.content:
      bad = True    
  if not bad:
    await message.channel.send('내가 봤는데 ' + str(message.author) + ' 얘가 \"' + message.content + '\" 쓰고 글삭튀 했어')

# 환영 인사
@bot.event
async def on_member_join(member):  
  channel = discord.utils.get(member.guild.text_channels, name='welcome')
  await channel.send('어서 와, 난 복실 개구리야.')

# 검열
@bot.event
async def on_message(message):
  message_content = message.content
  bad = False
  warning = ''

  for word in bad_word:
    if word in message_content and str(message.author) != '복실 개구리#0898':
      bad = True
      warning = '나쁜 말 하지마!'

  for word in gender_hate:
    if word in message_content and str(message.author) != '복실 개구리#0898':
      bad = True
      warning = '젠더 혐오발언 금지!'  

  if bad:
    await message.channel.send(warning)
    await message.delete()

  await bot.process_commands(message)



bot.run(os.environ['token'])

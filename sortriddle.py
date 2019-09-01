import discord
from discord.ext import commands
import queue
import regex 
import bs4
import lxml
import urllib.request, urllib.error
import linecache
import random

# サーバのトークン公開しないこと
TOKEN = '自分用のトークンを貼り付ける'

# コマンドプレフィックスの指定　書き換えるとコマンドの最初の記号が変わる
bot = commands.Bot(command_prefix='/')

# 答えを格納するキューと、現在の答えと問題を格納する変数を生成
answer_set = queue.Queue(maxsize=30)
current_ans =''
current_ques = ''

# 起動時に動作する処理
@bot.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました\n')
    pass

# botのコマンド
# /neko と発言したらにゃーんが返る処理
@bot.command()
async def neko(ctx):
    await ctx.send(f'{ctx.author.mention} にゃーん')

# /question または /q とDMで発言したら出題する処理
@bot.command(aliases=['q'])
@commands.dm_only()# DM以外でこのコマンドを入力するとエラーを吐く
async def question(ctx,arg):
    global current_ans
    if answer_set.full():
        await ctx.send('キューがいっぱいだにゃ')
    else:
        answer_set.put(arg.replace(' ','_'))
        if current_ans == '':
            current_ans = answer_set.get()
        await ctx.send('問題を受け付けたにゃ')
    
@question.error
async def question_error(ctx,error):
    if isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.send(f'{ctx.author.mention} `/q`はDM限定だにゃー')

# /answer または /a と発言したら正誤判定する処理 
@bot.command(aliases=['a'])
async def answer(ctx,arg):
    global current_ans
    global current_ques
    listed_arg = list(arg)
    if current_ans == '':
        await ctx.send('DMに`/q`で問題を送るにゃ')
    elif arg == current_ans:
        current_ans = ''
        current_ques = ''
        if not answer_set.empty():
            current_ans = answer_set.get()
        await ctx.send(f'{ctx.author.mention} 正解だにゃ')
    elif len(current_ans) != len(listed_arg):
        await ctx.send(f'{ctx.author.mention} ぶっぶー！長さが違うにゃ')
    else:
        cnt = 0
        for i in range(len(current_ans)):
            if current_ans[i] == listed_arg[i]:
                cnt+=1
        await ctx.send(f'{ctx.author.mention} ぶっぶー！ **'+ str(cnt) +'** 文字あってるにゃ')

# /start または /s と発言したらスタートする処理
@bot.command(aliases=['s'])
async def start(ctx):
    global current_ans
    global current_ques
    if current_ans =='':
        await ctx.send('DMに`/q`で問題を送るにゃ')
    else:
        text = sorted(current_ans)
        if current_ques == '':
            for i in range(len(text)):
                current_ques += text[i]
        await ctx.send('問題は **'+ current_ques +'** だにゃ')

# /giveup と発言したら解答を表示して次の問題をセットする処理
@bot.command()
async def giveup(ctx):
    global current_ans
    global current_ques
    if current_ans =='':
        await ctx.send('DMに`/q`で問題を送るにゃ')
    else:
        msg = 'わからないのかにゃ？答えは **' + current_ans + '** だにゃ'
        current_ans = ''
        current_ques = ''
        if not answer_set.empty():
            current_ans = answer_set.get()
        await ctx.send(msg)
        
# /clear と発言したら変数とキューを初期化する処理
@bot.command()
async def clear(ctx):
    global current_ans
    global current_ques
    current_ans = ''
    current_ques = ''
    while not answer_set.empty:
        answer_set.get()
    await ctx.send('全消しにゃー')

# /hint と発言したら答えの１文字目を返す処理
@bot.command(aliases=['h'])
async def hint(ctx):
    global current_ans
    if current_ans =='':
        await ctx.send('DMに`/q`で問題を送るにゃ')
    else:
        await ctx.send('１文字目は **'+ current_ans[0:1] + '** だにゃ')

# /wiki と発言したらWikipediaからランダムに出題する処理
@bot.command(aliases=['w'])
async def wiki(ctx):
    global current_ans
    global current_ques
    try:
        while True:
            url = urllib.request.urlopen('https://ja.m.wikipedia.org/wiki/%E7%89%B9%E5%88%A5:Random')
            soup = bs4.BeautifulSoup(url,'lxml')
            elems = soup.select('#section_0')
            arg = elems[0].getText().replace(' ','_')
            if regex.search(r'\p{Han}',arg):#elems に漢字が含まれていたら最初に戻る
                continue
            else:
                break
        if answer_set.full():
            await ctx.send('キューがいっぱいだにゃ')
        else:
            answer_set.put(arg)
            if current_ans == '':
                current_ans = answer_set.get()
            sorted_text = sorted(arg)
            if current_ques == '':
                for i in range(len(sorted_text)):
                    current_ques += sorted_text[i]
            await ctx.send('問題は **'+ current_ques +'** だにゃ')
    except Exception as e:
        print (e)
        await ctx.send('サイトにつながらないにゃ')

# /eng または /e と発言したら英単語リストからランダムに出題する
@bot.command(aliases=['e'])
async def eng(ctx):
    global current_ans
    global current_ques
    if answer_set.full():
        await ctx.send('キューがいっぱいだにゃ')
    else:
        num = random.randint(1,10000)
        target_line = linecache.getline('wordlist.txt',num).strip('\n')
        answer_set.put(target_line)
        if current_ans == '':
            current_ans = answer_set.get()
        text = sorted(target_line)
        if current_ques == '':
            for i in range(len(text)):
                current_ques += text[i]
        current_ques = current_ques.lstrip('\n')
        await ctx.send('問題は **'+ current_ques + '** だにゃ')

# ステータスに表示するメッセージを管理
@bot.event
async def on_message(message):
    global current_ans
    if message.author.bot:
        pass 
    elif current_ans == '':
        await bot.change_presence(activity=discord.Game("問題受付"))
    else:
        await bot.change_presence(activity=discord.Game("出題中"))
    await bot.process_commands(message)

# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)
# -- coding: utf-8 --
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
import sqlite3
import time


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect("data.db")
        self.c = self.conn.cursor()
        try:
            self.c.execute("CREATE TABLE blocked (word TEXT)")
            self.c.execute("CREATE TABLE logs (time TEXT, user TEXT, word TEXT, id INTEGER)")
        except sqlite3.OperationalError:
            pass

    def add_log(self, user, word):
        self.c.execute(f"INSERT INTO logs VALUES(datetime('now', 'localtime'), ?,?,?)", (user.name, word, user.id))
        self.conn.commit()

    def get_blocked(self):
        self.c.execute("SELECT * FROM blocked")
        tuple_ = self.c.fetchall()
        list_ = []
        for name in tuple_:
            list_.append(name[0])
        return list_

    def add_blocked(self, word):
        self.c.execute("INSERT INTO blocked VALUES(?)", (word,))
        self.conn.commit()


prefix = "block "
bot = commands.Bot(command_prefix=prefix)
database = DataBase()
block_list = []


@bot.event
async def on_ready():
    global block_list
    global database
    list_ = database.get_blocked()
    block_list += list_
    print("Logged in")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # delete the quotation marks below if you want administrators
    # to be able to freely send messages with forbidden words
    """if message.author.guild_permissions.administrator:
        return """

    global database
    global block_list
    for word in block_list:
        if word in message.content.lower():
            word = word.lower()
            message1 = await message.channel.send(f"<@{message.author.id}>, вы использовали в сообщениии запрещенное слово '{word}'. ")
            print(message.author, word)
            database.add_log(message.author, word)
            await message.delete()
            await asyncio.sleep(3)  # Тут время сна
            await message1.delete()
            return
    await bot.process_commands(message)


@bot.check(has_permissions(administrator=True))
@bot.command()
async def add(ctx, word):
    global block_list
    global database
    word = word.lower()
    block_list.append(word)
    database.add_blocked(word)
    await ctx.send(f"added")


bot.run('token')

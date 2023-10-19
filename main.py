import random
import asyncio
import discord
import requests
from py_cord_components import PycordComponents, Button, ButtonStyle

client = discord.Client()

token = ""

GIT_KEY = "Eo4g0uN9HE0CtvcoXGqlARNW0og9ZZ4S"


async def get_gifs(search):
    params = {
        'api_key': GIT_KEY,
        'q': search,  # вот здесь наш запрос для поиска
        'limit': 5,
        'rating': 'g',
        'lang': 'ru'
    }
    response = requests.get(f"https://api.giphy.com/v1/gifs/search", params=params)
    j_data = response.json().get('data')
    result = []
    for gif in j_data:
        result.append(gif["url"])
    return result


@client.event
async def on_ready():
    PycordComponents(client)
    print(f'Залогинился под именем {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:  # Чтобы не реагировать на сообщения бота
        return  # Ничего не делаем

    if message.content == 'ping':
        await message.channel.send('pong')

    if message.content.startswith('$Привет'):
        await message.channel.send('Привет, друг!')

    if message.content == '!hello':
        await message.channel.send(f'Приветствую тебя, {message.author.name}!')

    if message.content.startswith("!gif"):
        req = message.content[4:]
        gifs = await get_gifs(req)
        await message.channel.send(random.choice(gifs))

    if message.content == "!button":
        await pressbutton(message.channel)  # Вызываем функцию для обработки
        await message.channel.purge(limit=1)  # Удаляем сообщение с кнопками

    if message.content == "!game":
        await play_game(message.channel)  # Вызываем функцию для обработки

    if message.content == '!help':
        await message.channel.send('Я знаю команды - !hello, !gif')

    if check_caps(message.content):
        reason = 'Злоупотребление CAPS LOCK'
        await message.channel.purge(limit=1)  # Удаляем последнее сообщение
        await message.author.send(f'Вы были выгнаны по причине: {reason}')
        await message.author.ban(reason='reason')  # Баним пользователя
        emb = make_ban_embed(message.author, reason)  # Получаем рамку
        await message.channel.send(embed=emb)  # Выводим на экран рамку


async def pressbutton(channel):
    emb = discord.Embed(title='Проверка кнопок')
    await channel.send(embed=emb, components=[
        Button(style=ButtonStyle.green, label='Привет', emoji='👋'),
        Button(style=ButtonStyle.red, label='Пока', emoji='😡'),
        Button(style=ButtonStyle.URL, url='https://gb.ru/', label='GeekBrains', emoji='🧠')
    ])
    while True:
        response = await client.wait_for('button_click')
        answer = response.component.label
        if answer == 'Привет':
            await response.send('Привет)')
        elif answer == 'Пока':
            await response.send('Ну и ладно, пока(')


async def play_game(channel):
    pc = ''
    user = ''
    pc_count = 0
    user_count = 0
    while user_count < 3 and pc_count < 3:
        emb = discord.Embed(title='Играем в камень-ножницы-бумага')
        emb.add_field(name='Счет:', value=f'🧍‍{user_count} - 💻{pc_count}')
        emb.add_field(name='Последний ход:', value=f'🧍‍{user} - 💻{pc}')
        await channel.send(embed=emb, components=[
            Button(style=ButtonStyle.gray, label='Камень', emoji='🪨'),
            Button(style=ButtonStyle.gray, label='Ножницы', emoji='✂️'),
            Button(style=ButtonStyle.gray, label='Бумага', emoji='📃'),
            Button(style=ButtonStyle.gray, label='Выход')
        ])
        response = await client.wait_for('button_click')
        user = response.component.label
        if user == 'Выход':
            break
        pc = random.choice(['Камень', 'Ножницы', 'Бумага'])
        if user == pc:
            continue
        elif user == 'Камень' and pc == 'Ножницы':
            user_count += 1
        elif user == 'Камень' and pc == 'Бумага':
            pc_count += 1
        elif user == 'Ножницы' and pc == 'Бумага':
            user_count += 1
        elif user == 'Ножницы' and pc == 'Камень':
            pc_count += 1
        elif user == 'Бумага' and pc == 'Камень':
            user_count += 1
        elif user == 'Бумага' and pc == 'Ножницы':
            pc_count += 1
        await channel.purge(limit=2)
    emb = discord.Embed(title=f'Игра окончена. Счет: 🧍‍{user_count} - 💻{pc_count}')
    await channel.send(embed=emb)
    await asyncio.sleep(5)


def check_caps(text):  # Функция определения CAPS LOCK
    if len(text) < 6:  # Если длина текста меньше 6 символов
        return False  # то ничего не делаем.
    count = 0  # Счетчик количества больших букв
    for i in text:  # Цикл перебора букв в сообщении
        if i.isupper():  # Если найдена большая буква
            count += 1  # Увеличиваем счетчик на 1
    return count > len(text) // 4 * 3  # Если букв больше, чем 75% текста


def make_ban_embed(author, reason):
    emb = discord.Embed(title='Нарушение правил чата', colour=discord.Color.red())
    emb.set_author(name=author.name, icon_url=author.avatar_url)
    emb.add_field(name='Бан пользователя', value=f'Пользователь {author.mention} был забанен')
    emb.set_footer(text=f'Причина бана: {reason}')
    return emb


client.run(token)

import asyncio
import typing

import aiohttp
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import json
import os


APP_NAME = 'tttgbottt'
__tmdb_api_key = '200274d3065345401cde5322003c6a9a'
__BOT_TOKEN = '1731601685:AAH0eWs7pZw1N-ChRRVcpIRUlwzLyVelZHo'

bot = Bot(token=__BOT_TOKEN)
dp = Dispatcher(bot)

WEBHOOK_HOST = f'https://tttgbottt.herokuapp.com'
WEBHOOK_PATH = f'/webhook/1731601685:AAH0eWs7pZw1N-ChRRVcpIRUlwzLyVelZHo'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', default=19749))


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        await message.answer("Greetings!\nI'm OMEGA_400_SDA_Bot!\nMy creator is Aleksandr Dubeykovsky")
    except Exception as e:
        pass


def info_adder(text: str, key: str, sep: str, data_parsed: typing.Any) -> str:
    if key in data_parsed['results'][0]:
        text += key + ":\n" + data_parsed['results'][0][key] + '\n'
    else:
        text += key + ":\n" + "no " + key + " found" + '\n'
    text += sep
    return text


async def async_fetch(message: types.Message, session: aiohttp.ClientSession, url: str, query: str, obj="movie"):
    # TO DO - make photo and text appear together
    # SOLVED
    separator = "----------------------------------"
    try:
        async with session.get(url) as resp:
            data = await resp.read()
            data_parsed = json.loads(data)
            if 'results' in data_parsed:
                # TO DO - check for dict keys if they are exist
                # SOLVED
                text = ""
                real_title = query
                if 'title' in data_parsed['results'][0]:
                    real_title = data_parsed['results'][0]['title']
                elif 'name' in data_parsed['results'][0]:
                    real_title = data_parsed['results'][0]['name']
                elif 'original_title' in data_parsed['results'][0]:
                    real_title = data_parsed['results'][0]['original_title']
                elif 'original_name' in data_parsed['results'][0]:
                    real_title = data_parsed['results'][0]['original_name']

                if obj == "movie":
                    text = info_adder(text, "title", separator, data_parsed)
                    text = info_adder(text, "release_date", separator, data_parsed)
                    text = info_adder(text, "overview", separator, data_parsed)
                elif obj == "serial":
                    text = info_adder(text, "name", separator, data_parsed)
                    text = info_adder(text, "first_air_date", separator, data_parsed)
                    text = info_adder(text, "overview", separator, data_parsed)

                google_url = "https://www.google.com/search?q=watch%20online%20" + \
                             real_title.replace(' ', "%20") + "&num=10"
                async with session.get(google_url, headers={"User-Agent": 'Mozilla'}) as response:
                    t = await response.read()
                    # TO DO add more web-sites to check
                    ss = t.find(b'amazon')
                    if ss == -1:
                        amazon_url = "no url on amazon is found, i would suggest you to google search:\n" + \
                                     google_url[:-7]
                    else:
                        amazon_url = t[ss:]
                        amazon_url = amazon_url[:amazon_url.find(b'&')]
                        amazon_url = amazon_url.decode('utf-8')

                text += "Where to watch:\n" + amazon_url

                if data_parsed['results'][0]['poster_path']:
                    await message.answer_photo("http://image.tmdb.org/t/p/w185" +
                                               data_parsed['results'][0]['poster_path'], caption=text)
                else:
                    await message.answer("no poster available + \n" + text)
            else:
                await message.answer("On query = " + query + " nothing is found")
    except Exception as e:
        pass


async def header(message: types.Message):
    request_text = message.text[message.text.find(' ') + 1:]
    parsed_request_text = request_text.split(sep="#")
    try:
        await message.answer("Your search request is: \n" + str([str(i + 1) + " " + parsed_request_text[i]
                                                                 for i in range(len(parsed_request_text))]))
    except Exception as e:
        pass
    return parsed_request_text


@dp.message_handler(commands=['get_movies_info'])
async def get_movies_info(message: types.Message):
    # current - # is a delimiter
    # TO DO - smarter parsing
    try:
        parsed_request_text = await header(message)
    except Exception as e:
        parsed_request_text = ""

    # TO DO - process moments, when just one task is not working, but show other queries
    # SOLVED 99%
    urls = ["https://api.themoviedb.org/3/search/movie?" + "api_key=" + "200274d3065345401cde5322003c6a9a" +
            "&query=" + que for que in parsed_request_text]
    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                tasks.append(asyncio.ensure_future(async_fetch(message, session, url,
                                                                     url[url.find("query=") + 6:])))
            await asyncio.gather(*tasks)
    except Exception as e:
        pass


@dp.message_handler(commands=['get_serial_info'])
async def get_serial_info(message: types.Message):
    # current - # is a delimiter
    # TO DO - smarter parsing
    try:
        parsed_request_text = await header(message)
    except Exception as e:
        parsed_request_text = ""
    # TO DO - process moments, when just one task is not working, but show other queries
    # SOLVED 99%
    urls = ["https://api.themoviedb.org/3/search/tv?" + "api_key=" + "200274d3065345401cde5322003c6a9a" +
            "&query=" + que for que in parsed_request_text]
    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                tasks.append(asyncio.ensure_future(async_fetch(message, session, url,
                                                                     url[url.find("query=") + 6:], obj="serial")))
            await asyncio.gather(*tasks)
    except Exception as e:
        pass


@dp.message_handler(commands=['popular'])
async def get_popular(message: types.Message):
    separator = "\n----------------------------------\n"
    request_text = message.text[message.text.find(' ') + 1:]
    parsed_request_text = request_text.split(sep="#")
    try:
        await message.answer("Your 'popular' request is: \n" + str([parsed_request_text[i]
                                                                    for i in range(len(parsed_request_text))]))
    except Exception as e:
        pass
    # 0 - movie/tv
    if len(parsed_request_text) <= 0:
        media_type = "movie"
    else:
        media_type = parsed_request_text[0]
        if media_type not in ["movie", "tv"]:
            media_type = "movie"
    # 1 - day/week
    if len(parsed_request_text) <= 1:
        time_window = "day"
    else:
        time_window = parsed_request_text[1]
        if time_window not in ["day", "week"]:
            time_window = "day"
    # 2 - number of posters
    if len(parsed_request_text) <= 2:
        number_of_top = 3
    else:
        try:
            number_of_top = int(parsed_request_text[2])
        except Exception as e:
            number_of_top = 3
    url = f"https://api.themoviedb.org/3/trending/{media_type}/{time_window}?" + \
          "api_key=" + "200274d3065345401cde5322003c6a9a"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.read()
                data_parsed = json.loads(data)
                # await message.answer(str(data_parsed)[:1000])
                if 'results' in data_parsed:
                    tasks = []
                    for i in range(number_of_top):
                        tasks.append(await message.answer_photo(
                            "http://image.tmdb.org/t/p/w185" + data_parsed['results'][i]['poster_path'],
                            caption=((data_parsed['results'][i]['title'] if media_type == "movie" else
                                      data_parsed['results'][i]['name']) + separator +
                                      data_parsed['results'][i]['overview'])))
                    await asyncio.gather(*tasks)
    except Exception as e:
        pass


@dp.message_handler(commands=['help'])
async def echo(message: types.Message):
    separator = "*******************************************************"
    await message.answer("/help - список всех команд и их описание\n" + separator +
                         "/start - приветствие\n" + separator +
                         "/get_movies_info - \nввод: любое количество поисковых запросов через #\n\n" +
                         "пример: [/get_movies_info Venom#   Transformers  #Гриндевальд# магия лунного света # " +
                         "Мстители: война бесконечности # город в котором меня нет]\n\n" +
                         "вывод: для каждого запроса осуществится поиск по базе фильмов и при удачном " +
                         "запросе будет выведена следующая информация: название, дата релиза, овервью, " +
                         "ссылка на просмотр\n" + separator +
                         "/get_serial_info - \nввод: запрос для поиска сериала\n\n" +
                         "пример: [/get_serial_info Lucifer]\n\n" +
                         "вывод: для запроса осуществится поиск по базе сериалов и при удачном " +
                         "запросе будет выведена следующая информация: название, дата выхода первой серии," +
                         " овервью, ссылка на просмотр\n" + separator +
                         "/popular - \nввод вида: {media_type}#{time_window}#{top_k}\n" +
                         "где media_type = movie/tv\n" + "где time_window = day/week\n" + "где top_k = int(>0)\n" +
                         "default = movie#day#3\n\n" +
                         "пример: [/popular tv#week#4]\n\n" +
                         "вывод: top_k фильмов/сериалов по популярности за последний день/неделю\n")


# Run after startup
async def on_startup(dispatcher: Dispatcher):
    # await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)


# Run before shutdown
async def on_shutdown(dispatcher: Dispatcher):
    await bot.delete_webhook()


if __name__ == "__main__":
    # if "HEROKU" in list(os.environ.keys()):
    
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=False,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
    # else:
    #     executor.start_polling(dp)

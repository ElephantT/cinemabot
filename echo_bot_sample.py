import aiohttp
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import os


class MyBot:
    __BOT_TOKEN = '1819386454:AAH4xTOjXc3_PsxNbGm2U-COYyg22w10UGI'
    bot = Bot(token=__BOT_TOKEN)
    dp = Dispatcher(bot)

    def get_dp(self):
        return self.dp

    @dp.message_handler(commands=['start', 'help'])
    async def send_welcome(message: types.Message):
        await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

    @dp.message_handler()
    async def echo(message: types.Message):
        await message.reply(message.text)


if __name__ == '__main__':
    bot = MyBot()
    executor.start_polling(bot.get_dp())

import re
import asyncio
import peewee as pw

from config import *
from telethon import TelegramClient, events, sync, functions
from telethon.tl.functions.messages import ImportChatInviteRequest


# Создаем объект TelegramClient
client = TelegramClient(session_name, api_id, api_hash)

# Подключаемся к БД
db = pw.SqliteDatabase('DB/bots.db')


class Bot(pw.Model):
    # Модель Таблицы
    id = pw.IntegerField(primary_key=True)
    username = pw.CharField(unique=True)

    class Meta:
        database = db


class BotHandler:
    def __init__(self):
        self.client = client

        # Создаем таблицу в базе данных
        db.connect()
        db.create_tables([Bot], safe=True)

    async def main(self):
        await self.start()

    async def join_group(self, group_invite):
        # Присоединяемся к группе
        match = re.search(r'https://t.me/(\w+)', group_invite)
        if match:
            # Присоединяемся к группе по публичной ссылке
            group_id = match.group(1)
            try:
                # Выполняем запрос на вступление в группу
                result = await self.client(functions.channels.JoinChannelRequest(channel=group_id))
                print(f"Подключение к группе успешно: {result}")
            except Exception as e:
                print(f"Произошла ошибка при вступлении в группу: {e}")
        else:
            # Присоединяемся к группе по приватной ссылке
            try:
                await self.client(ImportChatInviteRequest(group_invite))
            except Exception as e:
                print(f"Произошла ошибка при вступлении в группу {group_invite}: {e}")


    async def handle_known_bot(self, event, bot_username):

        # Проверка на нахождение проверочных слов в тексте кнопки
        async def check_word_in_string(word_list, input_string):
            pattern = r'\b(?:' + '|'.join(re.escape(word) for word in word_list) + r')\b'
            return bool(re.search(pattern, input_string, re.IGNORECASE | re.UNICODE))

        # Список слов для проверки текста кнопки
        word_list = ["bot", "BOT", "Bot", "бот", "Бот", "БОТ", "human", "HUMAN", "человек", "ЧЕЛОВЕК"]

        # Обработка заданий от известных ботов
        # Обработка капчи от бота 'MissRose_bot'
        if bot_username == 'MissRose_bot':

            # Получаем текст кнопки, на которую нужно ответить
            for buttons in event.message.buttons:
                for button in buttons:
                    button_text = button.text
                    print(button_text)
                    result = await check_word_in_string(word_list, button_text)
                    print(result)
                    # Если текст кнопки соответствует списку проверочных слов, то происходит нажатие кнопки
                    if result:
                        await button.click()

        # Обработка капчи от бота 'shieldy_bot'
        if bot_username == 'shieldy_bot':
            message_text = event.message.text
            print(f"Received message from shieldy_bot: {message_text}")

            # Поиск математической операции вида (x+y) в сообщении
            pattern = r'\(\s*(\d+)\s*\+\s*(\d+)\s*\)'
            match = re.search(pattern, message_text)
            if match:
                # Получение значения x и y из математической операции
                x = int(match.group(1))
                y = int(match.group(2))

                result = x + y
                print(f"Evaluated result: {result}")

                # Задержка перед отправкой ответа (2-4 секунды)
                await asyncio.sleep(3)

                # Отправка результата обратно боту shieldy_bot
                await event.respond(str(result))
                print("Response sent.")
            else:
                print("Math operation not found in the message.")

    async def handle_unknown_bot(self, event, bot_username):
        # Обработка заданий от неизвестных ботов
        # Запись информации о боте в базу данных, если её там нет
        Bot.get_or_create(username=bot_username)
        pass

    async def on_bot_message(self, event):
        # Проверка отправителя, является ли он ботом и получаем его username
        if (await event.get_sender()).bot and event.sender.username:
            bot_username = event.sender.username

            # Получаем соответствующий метод обработки бота
            bot_method = self.handle_known_bot if Bot.select().where(Bot.username == bot_username).exists() else self.handle_unknown_bot

            # Вызов метода для обработки бота
            await bot_method(event, bot_username)

    async def start(self):
        await self.client.start()

        # Список инвайтов в группу (для примера взял ссылку на публ. группу, но можно поместить и ссылку приватную группу)
        group_invites = ["https://t.me/pogromista"]

        # Присоединение к группам по списку ссылок
        for group_invite in group_invites:
            await self.join_group(group_invite)

        me = await self.client.get_me()

        # Получаем ник текущего пользователя
        if not me.username:
            us_name = me.first_name
        else:
            us_name = me.username

        # Проверка на возможность писать сообщения в группе
        # await client.send_message(id_group, "Всем привет")

        # Обработчик событий на входящие сообщения
        self.client.add_event_handler(callback=self.on_bot_message,
                                      event=events.NewMessage(pattern=f"(?i).*{us_name}.*"))

        await self.client.run_until_disconnected()


if __name__ == '__main__':
    bot_handler = BotHandler()
    asyncio.run(bot_handler.main())
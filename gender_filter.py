import os
import json
import requests

from config import *
from telethon.sync import TelegramClient


# Создаем объект TelegramClient
client = TelegramClient(session_name, api_id, api_hash)
client.start()

# Замените 'LampMining' на любую другую группу, эта группа для примера
target_group = 'LampMining'

# Получение информации об участниках группы
participants = client.get_participants(target_group)

# Создание папок для хранения файлов, если их нет
if not os.path.exists("group_data"):
    os.makedirs("group_data")
if not os.path.exists("genders"):
    os.makedirs("genders")

# Формирование словаря с информацией об участниках
group_data = {}
for user in participants:
    if user.username:
        group_data[user.username] = {
            "name": user.first_name,
            "last_name": user.last_name if user.last_name else "",
        }

# Запись информации в формате JSON в файл
file_name = target_group.replace("@", "").replace("-", "_").replace(".", "_")
with open(f"group_data/{file_name}_users.json", 'w', encoding='utf-8') as file:
    json.dump(group_data, file, indent=4, ensure_ascii=False)


# Функция для определения пола по имени с использованием Gender API
def get_gender_from_name(name):
    url = f'https://gender-api.com/get?name={name}&key={GENDER_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data.get('gender', 'unknown')


# Создаем два списка для хранения имен мужчин и женщин
male_users = []
female_users = []

# Пробегаемся по словарю group_data и определяем пол участников по их именам
for username, user_info in group_data.items():
    name = user_info.get('name', '')
    if name:
        gender = get_gender_from_name(name)
        if gender.lower() == 'female':
            female_users.append(username)
        else:
            male_users.append(username)

# Записываем имена мужчин в файл male_users.txt
with open('genders/male_users.txt', 'w', encoding='utf-8') as file:
    for username in male_users:
        file.write(username + '\n')

# Записываем имена женщин в файл female_users.txt
with open('genders/female_users.txt', 'w', encoding='utf-8') as file:
    for username in female_users:
        file.write(username + '\n')

# Завершение сессии
client.disconnect()
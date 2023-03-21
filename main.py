import asyncio
import random
import time
import json
import datetime
import config
from telebot.async_telebot import AsyncTeleBot

from config import token, db
from operator import itemgetter
from telebot import types

bot = AsyncTeleBot(token)


@bot.message_handler(commands=['start', 'help'])
async def handle_start_help(message):
    await bot.send_message(
        message.chat.id,
        'Добро пожаловать! Данный бот - викторина по истории.\n' +
        'Для получения информации по системе оценивания введите /info\n'
        'Для того, чтобы приступить к написанию тестов или просмотра баллов, введите /button \n' +
        'Хорошего и продуктивного Вам времяпрепровождения!:)'
    )


@bot.message_handler(commands=['button'])
async def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Начать тест!")
    markup.add(item1)
    item2 = types.KeyboardButton("Посмотреть свои баллы")
    item3 = types.KeyboardButton("Посмотреть статистику")
    markup.add(item2, item3)
    await bot.send_message(message.from_user.id, "Выберите, что вам нужно\n", reply_markup=markup)


@bot.message_handler(commands=['info'])
async def button_info(message):
    text = """
В данном боте в каждом тесте дается по *10* вопросов, и каждый из них стоит *1* балл. 
В каждом тесте Вам дается *4* возможных варианта ответа, и только один верный.
После каждого вопроса дается *историческая справка* для изучения или повторения.
Вы можете досрочно завершить тест, написав *"Завершить"* или *"Сдаться"*
Также Вы можете узнать свои баллы за *все даты попыток*, когда Вы решали тест.
"""
    await bot.send_message(message.chat.id, text, parse_mode="Markdown")


def upload_questions_for_user():
    with open(config.path_to_questions, "r", encoding='utf-8') as file_open:
        all_questions = file_open.readlines()
    start_index = 0
    start_indexes_indentation = 11
    questions_count = 38
    indexes_of_questions = range(start_index, start_indexes_indentation * questions_count - 3, start_indexes_indentation)
    lst_of_used_indexes = []
    while len(lst_of_used_indexes) < 10:
        need_start_index = random.choice(indexes_of_questions)
        if need_start_index in lst_of_used_indexes:
            continue
        lst_of_used_indexes.append(need_start_index)

    questions_for_user = []
    for i in range(len(lst_of_used_indexes)):
        start_index = lst_of_used_indexes[i]
        questions_for_user.append(all_questions[start_index:start_index + 7])
    return questions_for_user


async def end_of_quiz(message):
    if db.all_points_exist(message.from_user.id):
        all_points = json.loads(db.get_all_points(message.from_user.id)[0][0])
    else:
        all_points = []
    current_date = datetime.datetime.now().strftime("%d.%m.%Y %T")
    current_points = db.get_current_point(message.from_user.id)[0][0]

    all_points.append([current_date, current_points])
    db.update_all_points(message.from_user.id, json.dumps(all_points))
    db.update_user_questions(message.from_user.id, "")
    db.update_current_questions_number(message.from_user.id, 10)
    db.update_current_point(message.from_user.id, 0)
    await button_message(message)


async def bar(message):
    current_questions_number = db.get_current_questions_number(message.from_user.id)[0][0]
    questions_for_user = json.loads(db.get_user_questions(message.from_user.id)[0][0])
    current_points = db.get_current_point(message.from_user.id)[0][0]
    if current_questions_number <= 0:
        await end_of_quiz(message)
        await bot.send_message(message.from_user.id,
                               text=f"Поздравляю, Вы завершили тест! Ваши текущие баллы - *{str(current_points)}*",
                               parse_mode="Markdown")
        return

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_first = types.InlineKeyboardButton(text=questions_for_user[current_questions_number - 1][1], callback_data='1')
    key_second = types.InlineKeyboardButton(text=questions_for_user[current_questions_number - 1][2], callback_data='2')
    key_third = types.InlineKeyboardButton(text=questions_for_user[current_questions_number - 1][3], callback_data='3')
    key_fourth = types.InlineKeyboardButton(text=questions_for_user[current_questions_number - 1][4], callback_data='4')
    keyboard.add(key_first)
    keyboard.add(key_second)
    keyboard.add(key_third)
    keyboard.add(key_fourth)

    question = questions_for_user[current_questions_number - 1][0]
    time.sleep(1)
    await bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


async def start_work_with_db(message):
    current_questions_number = 10
    state = db.get_current_state(message.chat.id)
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
        if message.from_user.username is None and message.from_user.first_name is not None:
            db.update_username(message.from_user.id, message.from_user.first_name)
            db.update_state(message.chat.id, config.States.S_HAVE_NAME.value)
        elif message.from_user.username is not None:
            db.update_username(message.from_user.id, message.from_user.username)
            db.update_state(message.chat.id, config.States.S_HAVE_NAME.value)
        else:
            await bot.send_message(message.chat.id, "Привет! Как я могу к тебе обращаться?")
            db.update_state(message.chat.id, config.States.S_DO_NOT_HAVE_NAME.value)

    db.update_current_questions_number(message.from_user.id, current_questions_number)
    str_questions = json.dumps(upload_questions_for_user())
    db.update_user_questions(message.from_user.id, str_questions)
    db.update_current_point(message.from_user.id, 0)


@bot.message_handler(func=lambda message: db.get_current_state(message.chat.id) == config.States.S_DO_NOT_HAVE_NAME.value)
def user_entering_name(message):
    bot.send_message(message.chat.id, "Отличное имя, запомню!")
    db.update_username(message.from_user.id, message.text)
    db.update_state(message.chat.id, config.States.S_HAVE_NAME.value)


@bot.message_handler(content_types=['text'])
async def message_reply(message):
    if message.text == "Начать тест!":
        await start_work_with_db(message)
        await bot.send_message(message.from_user.id, 'Удачи)', reply_markup=types.ReplyKeyboardRemove())
        await bar(message)
    elif message.text.lower() in ["сдаться", "завершить", "помогите", "сдаюсь", "сложно"]:
        current_user_question = db.get_current_questions_number(message.from_user.id)[0][0]
        current_points = db.get_current_point(message.from_user.id)[0][0]
        if 0 < current_user_question <= 10:
            await end_of_quiz(message)
            await bot.reply_to(message, f"К сожалению, вы не завершили тест. Ваши текущие баллы - *{current_points}*",
                               parse_mode="Markdown")
        return
    elif message.text == "Посмотреть свои баллы":
        await button_points(message)
    elif message.text == "Посмотреть статистику":
        await button_statistics(message)


@bot.callback_query_handler(func=lambda call: call.data)
async def callback_worker(call):
    current_questions_number = db.get_current_questions_number(call.from_user.id)[0][0]
    questions_for_user = json.loads(db.get_user_questions(call.from_user.id)[0][0])
    current_points = db.get_current_point(call.from_user.id)[0][0]
    current_answer = int(call.data)
    historical_info = questions_for_user[current_questions_number - 1][6]
    right_answer_number = int(questions_for_user[current_questions_number - 1][5])
    right_answer = questions_for_user[current_questions_number - 1][right_answer_number]

    if current_answer == right_answer_number:
        db.update_current_point(call.from_user.id, current_points + 1)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text="*Верно!*\n\n " + historical_info, parse_mode="Markdown")
    else:
        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=f"Упс! Кажется, Вы ошиблись. Правильный ответ - *{right_answer}*\n\n" + historical_info,
            parse_mode="Markdown"
        )
    db.update_current_questions_number(call.from_user.id, current_questions_number - 1)
    await bar(call)


async def button_points(message):
    if not db.user_exists(message.from_user.id) or not db.all_points_exist(message.from_user.id):
        await bot.send_message(message.chat.id, "К сожалению, вы не сыграли ни одной игры")
        return
    all_points = json.loads(db.get_all_points(message.from_user.id)[0][0])
    info = ""
    for i in range(len(all_points)):
        info += f"*{i + 1}.* Дата игры: {all_points[i][0]}, баллы: {all_points[i][1]}\n"
    await bot.send_message(message.chat.id, f"Статистика по вашим играм:\n{info}", parse_mode="Markdown")


async def button_statistics(message):
    all_points_of_all_users = db.get_all_points_of_all_users()
    flag = False
    for points in all_points_of_all_users:
        if points[1] is not None:
            flag = True
    if not flag or len(all_points_of_all_users) == 0:
        await bot.send_message(message.chat.id, f"Рейтинг игроков пуст!")
        return
    rating_lst = []
    info = ""
    for i in range(len(all_points_of_all_users)):
        username = all_points_of_all_users[i][0]
        points = all_points_of_all_users[i][1]
        if points is None or len(points) < 6:
            continue
        all_points = sorted(json.loads(points), key=itemgetter(1), reverse=True)
        rating_lst.append([username, all_points[0][1]])

    rating_lst.sort(key=itemgetter(1), reverse=True)
    for i in range(len(rating_lst)):
        info += f"{i + 1}. Пользователь: *{rating_lst[i][0]}*, максимальный балл: *{rating_lst[i][1]}*\n"
    await bot.send_message(message.chat.id, f"Рейтинг игроков:\n{info}", parse_mode="Markdown")


asyncio.run(bot.infinity_polling())

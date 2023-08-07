import json
import asyncio
from aiogram import Router
from aiogram import types
from aiogram import F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from core.utils import set_users_into_gsh, save_data_to_google_sheets
from create_bot import bot
from core import main_chatgpt
from dbase.dbworker import add_user, get_user_entry, update_last_interaction, update_last_dialog, get_user, \
    update_dialog_state, update_dialog_score, add_history, get_dialog_state, update_last_num_token, update_qa, \
    update_last_time_duration, get_num_queries, update_num_queries, update_last_chunks
from keyboards.user_keyboard import drating_inline_buttons_keyboard
from bot import logger
from handlers.admin_handler import ADMIN_CHAT_ID

router = Router()  # [2]

welcome_message = "<b>Добро пожаловать!</b> 🙌🏻 \n\nЯ - полезный помощник, на основе ChatGPT.\nПрофессионал в " \
                  "области Data Science и разработке искусственного интеллекта.\nЯ работаю в демонстрационном режиме " \
                  "поэтому у вас есть 10 запросов ко мне.\nСоветую прочитать рекомендации " \
                  "прежде чем начать общаться со мной ➡️ /recommendations.\n\n " \
                  "Мы подготовили несколько примеров вопросов, которые можно задать боту (просто нажми на команду с " \
                  "нужным вопросом):\n" \
                  "/Example1(Привет! Расскажи про обучение с подкреплением. Что это?)\n" \
                  "/Example2(Что такое свёрточный слой?)\n" \
                  "/Example3(Как обучаются нейронки?)"


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    if not get_user_entry(message.from_user.id):
        user_data = (
            message.from_user.id,
            None,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            None,
            None,
            None,
            None,
            0,
            "finish",
            0,
            0,
            0
        )
        add_user(user_data)
        try:
            set_users_into_gsh()
            logger.info(
                f"Добавили нового user в Google-таблицу!")
        except Exception as error:
            logger.warning(
                f"Ошибка добавления записи Пользователи: {error}")
        await message.reply(welcome_message + "\n\nЗадайте свой вопрос...", parse_mode='HTML')
        update_dialog_state(message.from_user.id, 'start')
    else:
        if get_dialog_state(message.from_user.id) == 'close':
            await bot.send_message(message.from_user.id, "Оцените предыдущий ответ чтобы продолжить использование "
                                                         "помощника.")
        else:
            await message.reply(welcome_message + "\n\nЗадайте свой вопрос...", parse_mode='HTML')
            update_dialog_state(message.from_user.id, 'start')
    dialog_status = get_dialog_state(message.from_user.id)
    #print(f'user_handler: cmd_start: {dialog_status = }')
    await asyncio.sleep(1)


@router.message(lambda message: get_dialog_state(message.from_user.id) == 'close')
async def any_action(message: types.Message):
    await bot.send_message(message.from_user.id, "Оцените предыдущий ответ чтобы продолжить использование помощника.")
    await asyncio.sleep(1)


@router.message(Command(commands=['recommendations']))
async def send_recommendations(message: types.Message):
    """
    This handler will be called when user sends `/recommendations` command
    """
    recommendations_student = '''
    Я - полезный помощник, на основе ChatGPT.
    Профессионал в области Data Science и разработке искусственного интеллекта.
    Советую прочитать полностью прежде чем начать общаться со мной.

    1. Сложные вопросы я рекомендую задавать мне на английском языке, так же на английском языке я работаю быстрее.

    2. Будьте конкретны и ясны: задавая вопрос, предоставьте как можно больше релевантной информации, чтобы помочь 
    мне лучше понять, что вам нужно. 

    3. Используйте правильную грамматику и орфографию: так мне будет легче понять ваше сообщение и ответить на него.

    4. Будьте вежливы и корректны в высказываниях: использование вежливых выражений и проявление уважения могут иметь 
    большое значение для обеспечения позитивного взаимодействия. 

    5. Избегайте использования аббревиатур или текстовой речи: это может затруднить мне понимание того, 
    что вы пытаетесь донести. 

    6. Задавайте по одному вопросу за раз: Если у вас есть несколько вопросов, лучше задавать их по одному, 
    чтобы помочь мне дать четкий и целенаправленный ответ. 

    7. Укажите контекст: Если ваш вопрос связан с определенной темой, предоставьте некоторую справочную информацию, 
    которая поможет мне понять, о чем вы спрашиваете. 

    8. Избегайте использования всех заглавных букв: ввод текста всеми заглавными буквами часто воспринимается как 
    крик и может затруднить продуктивную беседу. 

    9. Будьте терпеливы: я являюсь языковой моделью искусственного интеллекта, и мне может понадобиться некоторое 
    время, чтобы обработать ваш запрос. Ответы на некоторые вопросы могут длиться до 2 минут. 

    Готов общаться в чате.
    '''

    await message.reply(recommendations_student, parse_mode='HTML')
    await asyncio.sleep(1)


@router.message(Command(commands=['Example1']))
async def send_question_example1(message: types.Message):
    """
    This handler will be called when user sends `/recommendations` command
    """
    question_example1 = '''
    <b>Вопрос1</b>
    
    Привет!
    Расскажи про обучение с подкреплением. Что это?
    
    <b>Ответ ChatGPT:</b> 
    Привет! Обучение с подкреплением - это один из методов обучения нейронных сетей, 
    который используется для обучения агентов, способных принимать решения в динамической среде. В этом методе агент 
    взаимодействует с окружающей средой и получает обратную связь в виде награды или штрафа за свои действия. Цель 
    агента - максимизировать суммарную награду, которую он получает от среды. 
    
    Обучение с подкреплением основано на концепции марковских процессов принятия решений (MDP), где состояние среды 
    изменяется во времени и зависит только от предыдущего состояния и действия агента. Агент принимает решения на 
    основе текущего состояния среды и выбирает действие, которое максимизирует ожидаемую награду. 
    
    Основным алгоритмом обучения с подкреплением является алгоритм Q-обучения. Он основан на оценке функции ценности 
    действий (Q-функции), которая показывает ожидаемую награду, которую агент получит, выбрав определенное действие в 
    определенном состоянии. Алгоритм Q-обучения обновляет значения Q-функции на основе полученной награды и оценки 
    будущих наград. 
    
    Обучение с подкреплением широко применяется в таких областях, как робототехника, игровая индустрия, финансовые 
    рынки и автономные системы. Этот метод позволяет агентам самостоятельно изучать оптимальные стратегии поведения в 
    сложных и динамических средах. 
    '''

    await asyncio.sleep(2)
    await message.reply(question_example1, parse_mode='HTML')


@router.message(Command(commands=['Example2']))
async def send_question_example2(message: types.Message):
    """
    This handler will be called when user sends `/recommendations` command
    """
    question_example2 = '''
    <b>Вопрос2</b>

    Что такое свёрточный слой?

    <b>Ответ ChatGPT:</b> 
    Свёрточный слой - это основной компонент свёрточной нейронной сети, который используется 
    для извлечения признаков из входных данных, таких как изображения или тексты. Он состоит из набора свёрточных 
    ядер (фильтров), которые применяются к входным данным для выделения наиболее значимых фрагментов. Каждое 
    свёрточное ядро скользит по входным данным, перемножая значения пикселей с соответствующими весами ядра и 
    суммируя результаты. Это позволяет выделить различные признаки, такие как границы, текстуры или формы, 
    в зависимости от настроек ядра. Результатом работы свёрточного слоя является активационная карта (feature map), 
    которая представляет собой тензор с выделенными признаками. 

    Свёрточные слои обычно используются вместе с другими слоями, такими как пулинг слои и полносвязные слои, 
    для создания полноценной свёрточной нейронной сети. '''

    await asyncio.sleep(2)
    await message.reply(question_example2, parse_mode='HTML')


@router.message(Command(commands=['Example3']))
async def send_question_example1(message: types.Message):
    """
    This handler will be called when user sends `/recommendations` command
    """
    question_example3 = '''
    <b>Вопрос3</b>

    Как обучаются нейронки?
    
    <b>Ответ ChatGPT:</b> Нейронные сети обучаются путем настройки своих весов. Процесс обучения можно представить на 
    примере простой задачи классификации, где нейронная сеть должна определить, является ли животное на фотографии 
    кошкой или собакой. На первом этапе веса нейронной сети устанавливаются случайным образом. Каждый нейрон отвечает 
    за свой признак (например, длина хвоста, высота плеча) и, найдя свой признак, передает информацию дальше. На 
    основе всех вычислений нейронная сеть дает результат, например, с вероятностью 91% определяет, что это кошка. 
    Чтобы нейронная сеть научилась, ей предоставляется набор данных для обучения - обучающая выборка. 
    
    Это похоже на учебник с множеством примеров. В процессе обучения нейронная сеть корректирует свои веса, 
    чтобы улучшить свои предсказания и приблизиться к правильным ответам. Таким образом, нейронные сети обучаются 
    путем анализа большого количества данных и постепенной корректировки своих весов для достижения наилучших 
    результатов. '''

    await asyncio.sleep(2)
    await message.reply(question_example3, parse_mode='HTML')


@router.message(Command(commands=['balance']))
async def send_balance(message: types.Message):
    await asyncio.sleep(1)


@router.message(Command(commands=['context']))
async def reset_context(message: types.Message):
    await asyncio.sleep(1)


@router.callback_query(lambda c: c.data.startswith("drate_"))
async def process_callback_qrating(callback_query: types.CallbackQuery):
    if get_dialog_state(callback_query.from_user.id) == 'close':
        user_data = get_user(callback_query.from_user.id)   # получим из БД информацию о пользователе
        #print(f'process_callback_qrating: {user_data = }')
        score_chuncks = user_data[9]
        print(f'process_callback_qrating: {score_chuncks = }')
        rating = int(callback_query.data[6:])
        #print(f'process_callback_qrating: {type(rating)}, {rating = }')
        await bot.answer_callback_query(callback_query.id, text=f"Спасибо за вашу оценку: {rating}!", show_alert=True)
        if callback_query.from_user.id in ADMIN_CHAT_ID:
            await bot.send_message(callback_query.from_user.id, f"Спасибо за вашу оценку: {rating}! Можете задать "
                                                                f"следующий вопрос")
        else:
            await bot.send_message(callback_query.from_user.id, f"Спасибо за вашу оценку: {rating}! Можете задать "
                                                                f"следующий вопрос (осталось "
                                                                f"{int(10 - get_num_queries(callback_query.from_user.id))} запрос(ов).")
        update_dialog_state(callback_query.from_user.id, 'finish')
        # Здесь сохраняется оценка пользователя для дальнейшего анализа или использования
        update_dialog_score(callback_query.from_user.id, rating)

        # переда записью истории проверим содержимое user_data:
        for i, item in enumerate(user_data):
            print(f'User_data[{i}]. {item}')

        # Запись истории
        history_data = (
            callback_query.from_user.id,
            "question",
            "\n".join([f'Пользователь: {user_data[7]}', f'Ассистент: {user_data[8]}']),
            score_chuncks,
            rating,
            user_data[10],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_data[13]
        )

        # переда записью истории проверим содержимое history_data:
        for i, item in enumerate(history_data):
            print(f'history_data[{i}]. {item}')

        add_history(history_data)
        try:
            logger.info(
                f"Оценка вопроса! Добаление записи в таблицу Оценка")
            save_data_to_google_sheets('Оценки', history_data)
        except Exception as error:
            logger.warning(
                f"Ошибка добавления записи Оценки: {error}")
    await bot.answer_callback_query(callback_query.id)
    await asyncio.sleep(1)


@router.message(lambda message: get_dialog_state(message.from_user.id) in ['start', 'finish'])
async def generate_answer(message: types.Message):
    #print(f'generate_answer: starting...')
    update_last_interaction(message.from_user.id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    num_queries = get_num_queries(message.from_user.id)
    #print(f'generate_answer: {num_queries = }')
    if num_queries < 10 or message.from_user.id in ADMIN_CHAT_ID:       # ограничение по ответам: менее 10 ответов или админ - неограничено
        try:
            msg = await message.answer("Идет подготовка ответа. Ждите...⏳")  # msg["message_id"]
            time1 = datetime.now()
            logger.info(f"Запрос пошел: {message.text}")
            completion, dialog, chunks = main_chatgpt.WorkerOpenAI().get_chatgpt_answer(message.text)
            #logger.info(f"Запрос вернулся: {completion}")
            logger.info(f"Запрос вернулся: [completion]")
            #content_to_print = dialog[1]['content']
            #print(f'user_handler: generate_answer: {content_to_print = }')
            #print(f'user_handler: generate_answer: {chunks = }')
            time2 = datetime.now()
            duration = time2 - time1
            await msg.edit_text(completion.choices[0].message.content)
            #logger.info(f"ЦЕНА запроса: {0.0002 * (completion['usage']['total_tokens'] / 1000)}$\n {completion['usage']}")
            logger.info(f"ЦЕНА запроса: {0.004 * (completion['usage']['total_tokens'] / 1000)}$")
            update_last_chunks(message.from_user.id, chunks)
            update_last_dialog(message.from_user.id, json.dumps(dialog))
            update_last_time_duration(message.from_user.id, int(duration.total_seconds()))
            update_qa(message.from_user.id, (message.text, completion.choices[0].message.content))
            update_dialog_state(message.from_user.id, 'close')
            update_last_num_token(message.from_user.id, completion['usage']['total_tokens'])
            update_num_queries(message.from_user.id, num_queries + 1)
            await asyncio.sleep(1)
            await message.answer("Пожалуйста, оцените качество консультации от -2 до 2:",
                                 reply_markup=drating_inline_buttons_keyboard())
        except Exception as error:
            logger.warning(
                f"Ошибка генерации: {error}")
            await bot.send_message(message.from_user.id, f"ОШИБКА: {error}")
            await bot.send_message(message.from_user.id, "Модель в настоящее время перегружена. Попробуйте позже.")
    else:
        await bot.send_message(message.from_user.id, "Вы исчерпали всё количество запросов (10) демонстрационного "
                                                     "режима.\nСпасибо что воспользовались нашим Помощником! 🤝")
    await asyncio.sleep(1)


async def generate_algorithm_error(message: types.Message):
    logger.warning(f"Ошибка алгоритма бота. Сообщение пользователя не обработано")
    await message.answer("Извините, сбой в алгоритме Бота: ваше сообщение не обработано")
    await asyncio.sleep(1)

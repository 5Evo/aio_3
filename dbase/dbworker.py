import psycopg2
import sqlite3
import pandas as pd

from config import DB_TYPE
from create_bot import POSTGRE_HOST, POSTGRE_DB, POSTGRE_USER, POSTGRE_PASSW


def connect_db(db_type):
    """
    выбираем подключение в SQLite или PostgreSQL
    :param db_type:
    :return:
    """
    if db_type == 'POSTGRE':
        connection = psycopg2.connect(
            host=POSTGRE_HOST,
            database=POSTGRE_DB,
            user=POSTGRE_USER,
            password=POSTGRE_PASSW)
    elif db_type == 'SQLite3':
        db_path = 'db_agent_501.db'
        connection = sqlite3.connect(db_path)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    return connection


def create_db():
    """
        Создаем 2 таблицы в PostgreSQL: users и history
        :return:
        """

    try:
        connection = connect_db(DB_TYPE)
        cursor = connection.cursor()
        print(f'Успешно подключились к {DB_TYPE}')

        # создаем таблицу users в Posgres
        # в SQLite первая строка доджна быть: "user_id INTEGER PRIMARY KEY,"
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                e_mail TEXT,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                last_interaction TEXT,
                last_dialog TEXT,
                last_question TEXT,
                last_answer TEXT,
                last_num_token REAL, 
                dialog_state TEXT DEFAULT 'finish',
                dialog_score REAL DEFAULT 0,
                last_time_duration REAL,
                num_queries REAL DEFAULT 0
            )
            '''
        )

        # создаем таблицу history
        # в SQLite первая строка должна быть: "id INTEGER PRIMARY KEY,"
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                score_name TEXT,
                score_text TEXT,
                score INTEGER,
                num_token INTEGER,
                date_estimate TEXT,
                time_duration REAL
            )
            '''
        )
        connection.commit()
        cursor.close()          # добавил при переходе на PostgreSQL
        connection.close()
    except Exception as e:
        print(f'Ошибка подключения к {DB_TYPE} {e}')

def create_db_old():
    """
    Создаем 2 таблицы: users и history
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    # создаем таблицу users (Скрипт для SQLite, не Postgres)
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            e_mail TEXT,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            last_interaction TEXT,
            last_dialog TEXT,
            last_question TEXT,
            last_answer TEXT,
            last_num_token REAL, 
            dialog_state TEXT DEFAULT 'finish',
            dialog_score REAL DEFAULT 0,
            last_time_duration REAL,
            num_queries REAL DEFAULT 0
        )
        '''
    )

    # создаем таблицу history
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            score_name TEXT,
            score_text TEXT,
            score INTEGER,
            num_token INTEGER,
            date_estimate TEXT,
            time_duration REAL
        )
        '''
    )

    connection.commit()
    cursor.close()  # добавил при переходе на PostgreSQL
    connection.close()


def add_user(user_data):
    """
    Создаем нового пользователя в таблице, если такого еще нет. Иначе Игнорируем
    :param user_data:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, e_mail, first_name, last_name, username, last_interaction, "
            "last_dialog, last_question, last_answer, last_num_token, dialog_state, dialog_score, last_time_duration, "
            "num_queries) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            user_data,)

    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "INSERT INTO users (user_id, e_mail, first_name, last_name, username, last_interaction,  "
            "last_dialog, last_question, last_answer, last_num_token, dialog_state, dialog_score, last_time_duration, "
            "num_queries) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            user_data,)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()  # добавил при переходе на PostgreSQL
    connection.close()


def add_history(history_data):
    """
    Добавляем запись в таблицу history, если такой еще нет. Иначе - Игнорируем
    :param history_data:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "INSERT OR IGNORE INTO history (user_id , score_name, score_text, score, num_token, date_estimate, "
            "time_duration) VALUES (?, ?, ?, ?, ?, ?, ?)",
            history_data,
        )
    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "INSERT INTO history (user_id , score_name, score_text, score, num_token, date_estimate, time_duration) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            history_data,
        )
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()  # добавил при переходе на PostgreSQL
    connection.close()


def get_user_entry(user_id):
    """
    Проверка наличия записи в БД для пользователя user_id
    :param user_id:
    :return: True или False
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    elif DB_TYPE == 'POSTGRE':
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    result = cursor.fetchone()
    cursor.close()  # добавил при переходе на PostgreSQL
    connection.close()

    return True if result else False


def get_user(user_id):
    """
    Получаем из БД данные пользователя user_id
    :param user_id:
    :return: данные пользователя
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()
    if DB_TYPE == 'SQLite3':
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    elif DB_TYPE == 'POSTGRE':
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    result = cursor.fetchone()
    cursor.close()  # добавил при переходе на PostgreSQL
    connection.close()

    return result


def update_last_interaction(user_id, last_interaction):
    """
    Обновляем в БД last_interaction
    :param user_id:
    :param last_interaction:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "UPDATE users SET last_interaction = ? WHERE user_id = ?",
            (last_interaction, user_id),)
    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "UPDATE users SET last_interaction = %s WHERE user_id = %s",
            (last_interaction, user_id),)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()  # добавил при переходе на PostgreSQL
    connection.close()


def update_last_dialog(user_id, last_dialog):
    """
    Обновляем last_dialog для пользователя user_id
    :param user_id:
    :param last_dialog:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "UPDATE users SET last_dialog = ? WHERE user_id = ?",
            (last_dialog, user_id),)
    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "UPDATE users SET last_dialog = %s WHERE user_id = %s",
            (last_dialog, user_id),)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()


def update_qa(user_id, last_qa):
    """
    Обновляем последний вопрос/ответ
    last_qa[0] - последний вопрос
    last_qa[1] - последний ответ
    :param user_id:
    :param last_qa:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "UPDATE users SET last_question= ?, last_answer = ? WHERE user_id = ?",
            (last_qa[0], last_qa[1], user_id),)
    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "UPDATE users SET last_question= %s, last_answer = %s WHERE user_id = %s",
            (last_qa[0], last_qa[1], user_id),)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()


def update_dialog_score(user_id, dialog_score):
    """
    Обновляем оценку диалога
    :param user_id:
    :param dialog_score:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "UPDATE users SET dialog_score = ? WHERE user_id = ?",
            (dialog_score, user_id),)
    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "UPDATE users SET dialog_score = %s WHERE user_id = %s",
            (dialog_score, user_id),)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()


def update_dialog_state(user_id, dialog_state):
    """
    Обновляем состояние диалога. 3 Состояния:
    finish - после получения оценки диалога, а также начальное состояние при создании пользователя
    start - пригласили пользователя задать вопрос
    close - После получения ответа ChatGPT
    :param user_id:
    :param dialog_state:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "UPDATE users SET dialog_state = ? WHERE user_id = ?",
            (dialog_state, user_id),)
    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "UPDATE users SET dialog_state = %s WHERE user_id = %s",
            (dialog_state, user_id),)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()


def update_last_num_token(user_id, num_token):
    """
    Обновляем количество токенов у user за последний запрос
    TODO: Подумай, может лучше хранить не последнее кол-во токенов в заросе пользователя, а сумму токенов за все запросы пользователя?
    :param user_id:
    :param num_token:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "UPDATE users SET last_num_token = ? WHERE user_id = ?",
            (num_token, user_id),)
    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "UPDATE users SET last_num_token = %s WHERE user_id = %s",
            (num_token, user_id),)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()


def update_num_queries(user_id, num_queries):
    """
    Обновляем кол-во запросов пользователя, чтобы можно было ограничить тестовый период
    В метод подается кол-во предыдущих запросов, увеличенное на 1
    :param user_id:
    :param num_queries:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "UPDATE users SET num_queries = ? WHERE user_id = ?",
            (num_queries, user_id),)
    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "UPDATE users SET num_queries = %s WHERE user_id = %s",
            (num_queries, user_id),)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()


def update_last_time_duration(user_id, time_duration):
    """
    Сохраняем время обраюотки последнего зароса у пользователя
    :param user_id:
    :param time_duration:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute(
            "UPDATE users SET last_time_duration = ? WHERE user_id = ?",
            (time_duration, user_id),)
    elif DB_TYPE == 'POSTGRE':
        cursor.execute(
            "UPDATE users SET last_time_duration = %s WHERE user_id = %s",
            (time_duration, user_id),)
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    connection.commit()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()


def get_dialog_state(user_id):
    """
    Получаем состояние диалога для пользователя
    :param user_id:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    elif DB_TYPE == 'POSTGRE':
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    result = cursor.fetchone()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()

    return result[10] if result else None


def get_num_queries(user_id):
    """
    Получаем количество выполненных запросов пользователя
    :param user_id:
    :return:
    """
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    if DB_TYPE == 'SQLite3':
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    elif DB_TYPE == 'POSTGRE':
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    else:
        raise Exception("connect_db(): Не установленный тип БД")
        sys.exit(1)

    result = cursor.fetchone()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()

    return result[13] if result else None


def get_all_users():
    """
    Получаем список всех записей о пользователях для отчета
    :return:
    """
    # Connect to the SQLite database
    connection = connect_db(DB_TYPE)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users")

    # Query all records from the users table
    result = cursor.fetchall()
    cursor.close()          # добавил при переходе на PostgreSQL
    connection.close()

    return result


def get_df_users():
    """
    Получаем список всех записей о пользователях в формате Pandas для отчета
    :return:
    """
    # Connect to the SQLite database
    connection = connect_db(DB_TYPE)

    # Query all records from the users table
    result = pd.read_sql_query("SELECT * FROM users", connection)

    connection.close()

    return result


def get_df_history():
    """
    Получаем всю историю в формате Pandas для отчета
    :return:
    """
    # Connect to the SQLite/PostgreSQL database
    connection = connect_db(DB_TYPE)

    # Query all records from the users table
    result = pd.read_sql_query("SELECT * FROM history", connection)
    connection.close()

    return result

if __name__ == '__main__':
    # db_path = '../database.db'
    # df = get_df_users()
    # df.to_csv("users.csv")
    # df.to_excel("users.xlsx", index=False)

    create_db()
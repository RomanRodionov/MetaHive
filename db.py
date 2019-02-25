import sqlite3
import datetime

class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()

class UsersModel():
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash=False):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

class NewsModel():
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             title VARCHAR(100),
                             content VARCHAR(1000),
                             user_id INTEGER,
                             datetime DATETIME
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                          (title, content, user_id, datetime) 
                          VALUES (?,?,?,?)''', (title, content, str(user_id), datetime.datetime.now()))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ? ORDER BY datetime, title", (str(news_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM news WHERE user_id = ? ORDER BY datetime, title",
                           (str(user_id)))
        else:
            cursor.execute("SELECT * FROM news ORDER by datetime, title")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ?''', (str(news_id)))
        cursor.close()
        self.connection.commit()


class MessagesModel():
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             id_from INTEGER,
                             id_to INTEGER,
                             content VARCHAR(1000),
                             datetime DATETIME
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, id_from, id_to, content):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO messages
                          (id_from, id_to, content, datetime) 
                          VALUES (?,?,?,?)''', (str(id_from), str(id_to), content, datetime.datetime.now()))
        cursor.close()
        self.connection.commit()

    def get(self, message_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM messages WHERE id = ? ORDER BY datetime DESC", (str(message_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, id_from=None, id_to=None):
        cursor = self.connection.cursor()
        if id_from and not id_to:
            cursor.execute("SELECT * FROM messages WHERE id_from = ? ORDER BY datetime DESC",
                           (str(id_from)))
        elif id_to and not id_from:
            cursor.execute("SELECT * FROM messages WHERE id_to = ? ORDER BY datetime DESC",
                           (str(id_to)))
        elif id_to and id_from:
            cursor.execute("SELECT * FROM messages WHERE id_from = ? AND id_to = ? OR id_to = ? AND id_from = ? ORDER BY datetime DESC",
                           (str(id_from), str(id_to), str(id_from), str(id_to)))
        else:
            cursor.execute("SELECT * FROM messages ORDER by datetime DESC")
        rows = cursor.fetchall()
        return rows

    def delete(self, id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM messages WHERE id = ?''', (str(id)))
        cursor.close()
        self.connection.commit()

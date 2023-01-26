from requests import delete
import sqlite3


class FDataBase:
    def __init__(self, db_):
        self.__db = db_
        self.__cur = db_.cursor()
        self.__userID = None

    def checkin(self, login):
        self.__cur.execute(f"SELECT COUNT() as `n` FROM users WHERE name_ like '{login}'")
        res = self.__cur.fetchone()
        if res['n'] > 0:
            return True  # если пользователь уже зарегистрирован
        return False

    def newUser(self, psw, login):
        try:
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?)", (login, psw))
            self.__db.commit()
            return 200

        except sqlite3.Error as error:
            print('Ошибка ', error)
            return 400

    def getAll(self, id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id like '{id}' LIMIT 1")
            self.id_ = self.__cur.fetchone()
            return self
        except Exception as error:
            print('Была обнаружена ошибка ', error)

    def getUserId(self, name):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE name_ like '{name}'")
            id_ = self.__cur.fetchone()
            return id_[0], id_[1]
        except Exception as error:
            print('Была обнаружена ошибка ', error)

    def returnHsh(self, login):
        self.__cur.execute(f"SELECT pass from users WHERE name_ like '{login}';")
        return self.__cur.fetchone()[0]

    def getMenu(self, authour_id=None):
        try:
            if authour_id:
                self.__cur.execute(f"SELECT * FROM posts WHERE authour_id = {authour_id}")
            else:
                self.__cur.execute(f"SELECT * FROM posts")
            res = self.__cur.fetchall()
            if not all(res):
                return ['', '', '']
            return res
        except BaseException as exp:
            print("Not found table posts or else error", exp)
        return []

    def getContent(self, id_):
        try:
            self.__cur.execute(f"SELECT * FROM posts WHERE id = {id_}")
            res = self.__cur.fetchall()
            return res
        except BaseException as exp:
            print("Not found table posts or else error", exp)
        return []

    def edit_post(self, new_content, id_):
        text = new_content.replace("\n", "<br>")
        text = text.replace("'", "0b100111")
        text = text.replace('"', "0b100010")
        self.__cur.execute(f"""UPDATE posts SET content = "{text}" WHERE id = {id_}""")
        self.__db.commit()
        return 200

    def addContent(self, content, author_id):
        try:
            text = content["content"].replace("\n", "<br>")
            text = text.replace("'", "0b100111").replace('"', "0b100010")
            title = content["title"].replace("\n", "<br>")
            title = title.replace("'", "0b100111").replace('"', "0b100010")
            if not all([content['authour'], content["title"], text]):
                return 400
            self.__cur.executescript(f"""
                INSERT INTO posts VALUES(
                NULL, "{content['authour']}",
                "{title}", "{text}", "{author_id}")""")
            return 200
        except BaseException as error:
            print("catched error", error)

    def getPost(self, post_id):
        try:
            self.__cur.execute(f"SELECT * FROM posts WHERE id = {post_id}")
            if self.__cur.fetchone():
                self.__cur.execute(f"SELECT * FROM posts WHERE id = {post_id}")
                return self.__cur.fetchone()
        except:
            print("Error with getPost method")

    def deletePost(self, post_id):
        self.__cur.execute(f"DELETE FROM posts WHERE id = {post_id}")
        self.__db.commit()
    
    @staticmethod
    def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
        bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    @staticmethod
    def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
        n = int(bits, 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'

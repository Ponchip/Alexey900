class UserInfo:
    def __init__(self, name, db):
        self.__user = db.getUserId(name)
        self.__db = db
        self.name = self.__user[1]

    def is_authenticated(self):
        if self.__user:
            return True
        else:
            return False

    def is_active(self):
        return True

    def get_id(self):
        return str(self.__user[1])

    def is_anonymous(self):
        return False

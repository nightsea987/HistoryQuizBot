import sqlite3


class database:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def select_user(self, chat_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `userchat` WHERE `chat_id` = ?", (chat_id,)).fetchmany(1)

    def get_all_points_of_all_users(self):
        with self.connection:
            return self.cursor.execute("SELECT username, all_points FROM `userchat`").fetchall()

    def remove_user(self, chat_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM `userchat` WHERE `chat_id` = ? AND `username` = ?",
                                       (chat_id,)).fetchmany(1)

    def user_exists(self, chat_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `userchat` WHERE `chat_id` = ?",
                                         (chat_id,)).fetchmany(1)
            return bool(len(result))

    def all_points_exist(self, chat_id):
        with self.connection:
            result = self.cursor.execute("SELECT all_points FROM `userchat` WHERE `chat_id` = ?",
                                         (chat_id,)).fetchmany(1)
            return result[0][0] != ""

    def add_user(self, chat_id, username):
        with self.connection:
            if not self.user_exists(chat_id,):
                return self.cursor.execute("INSERT INTO `userchat` (`chat_id`, `username`) VALUES (?,?)",
                                           (chat_id, username,))

    def get_all_points(self, chat_id):
        with self.connection:
            return self.cursor.execute("SELECT all_points FROM `userchat` WHERE `chat_id` = ?",
                                       (chat_id,)).fetchmany(1)

    def get_current_point(self, chat_id):
        with self.connection:
            return self.cursor.execute("SELECT current_point FROM `userchat` WHERE `chat_id` = ?",
                                       (chat_id,)).fetchmany(1)

    def get_user_questions(self, chat_id):
        with self.connection:
            return self.cursor.execute("SELECT user_questions FROM `userchat` WHERE `chat_id` = ?",
                                       (chat_id,)).fetchmany(1)

    def get_current_questions_number(self, chat_id):
        with self.connection:
            return self.cursor.execute("SELECT current_question_number FROM `userchat` WHERE `chat_id` = ?",
                                       (chat_id,)).fetchmany(1)

    def update_all_points(self, chat_id, all_points):
        with self.connection:
            self.cursor.execute(f"""UPDATE `userchat`
                                    SET all_points='{all_points}'
                                    WHERE chat_id='{chat_id}'""")

    def update_current_point(self, chat_id, current_point):
        with self.connection:
            self.cursor.execute(f"""UPDATE `userchat`
                                    SET current_point='{current_point}'
                                    WHERE chat_id='{chat_id}'""")

    def update_user_questions(self, chat_id, user_questions):
        with self.connection:
            self.cursor.execute(f"""UPDATE `userchat`
                                    SET user_questions='{user_questions}'
                                    WHERE chat_id='{chat_id}'""")

    def update_current_questions_number(self, chat_id, current_questions_number):
        with self.connection:
            return self.cursor.execute(f"""UPDATE `userchat`
                                    SET current_question_number='{current_questions_number}'
                                    WHERE chat_id='{chat_id}'""")
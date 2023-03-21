from enum import Enum
from database2 import database

token = "5696857702:AAGKgI9-kvL-axWfKDQ-WuiCN4bmpEbGT28"
db = database('Database/users2.db')
path_to_questions = "QuestionsForTheTests/ConfigForHistoryBot2.txt"


class States(Enum):
    S_DO_NOT_HAVE_NAME = "0"  # Начало нового диалога
    S_HAVE_NAME = "1"

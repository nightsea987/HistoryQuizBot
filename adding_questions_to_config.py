questions_count = int(input("Введите количество вопросов, которые Вы хотели бы добавить в config-файл: "))

print("Введите Ваш вопрос по следующей схеме:")
print("\t1)Сам вопрос\n\t2)На каждой отдельной строке введите 4 ответа")
print("\t3)Номер правильного ответа\n\t4)Историческую справку")

string_count = 7
separating_line = "*************************************************************************************"
path_to_file = "QuestionsForTheTests//NewQuestions.txt"

with open(path_to_file, "a", encoding='utf-8') as file_open:
    for i in range(questions_count):
        for j in range(string_count):
            file_open.write(input() + "\n")
        file_open.write(separating_line + "\n")
        file_open.write("\n" * 3)

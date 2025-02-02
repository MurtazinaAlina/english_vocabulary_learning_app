

class WordNavigation:
    """ Класс для оперативного сохранения истории попыток и навигации вперёд-назад по генерируемым словам """

    # Структура данных для хранения истории попыток, где key - индекс попытки, value - сгенерированная строка.
    # Записываются не только варианты ДА/НЕТ, но и пролистывания ДАЛЕЕ
    def __init__(self):
        self.history = {}           # Словарь с историей
        self.current_index = 0      # Стартовый индекс при запуске программы

    def add_in_history(self, row) -> None:
        """
        Добавление новой записи в историю, если для текущего индекса нет соответствующей записи в словаре.

        :param row: список с данными сгенерированной строки:
                    [3, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
        :return: None
        """
        if self.current_index not in self.history.keys():   # Если ключа с таким индексом нет:
            self.history[self.current_index] = row          # Добавь в историю запись для этого индекса

    def next_word(self) -> list | None:
        """
        Обработка кнопок ДА/НЕТ/ДАЛЕЕ. Увеличение индекса текущей попытки.
        Функция проверяет, есть ли за следующим индексом попытки запись в истории, если да, возвращает эту запись.

        :return: None или список с данными строки из истории:
                [3, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
        """
        self.current_index += 1
        if self.current_index in self.history.keys():
            return self.history[self.current_index]             # Если запись есть, возвращает запись
        return None                                             # Если записи нет, None

    def previous_word(self) -> list:
        """
        Получение данных из истории попыток по уменьшившемуся индексу

        :return: список с данными строки из истории по уменьшившемуся индексу попытки:
                [3, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
        """
        if self.current_index > 0:
            self.current_index -= 1                             # Уменьшение индекса попытки, если он не минимальный
        return self.history[self.current_index]                 # Запись по уменьшившемуся индексу

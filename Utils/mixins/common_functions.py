import tkinter as tk
from tkinter import messagebox as mbox


class CommonFunctionsMixin:
    """ Общие функции """

    def __init__(self):
        pass

    def check_if_not_db(self, widget: tk.Frame) -> bool:
        """
        Проверка если не выбран тип базы или файл с базой.
        Устанавливает пустые данные-заглушку для отображения визуала контейнеров.
        self.db.engine - db инициализируется внутри класса-родителя.

        :param widget: окно, в котором вызывается сборка (EnRuWindow, EnRuAudioWindow ...)
        :return: True если НЕ выбрана ни одна база с данными. False если есть подключение к любому виду базы.
        """
        if (self.data_type == 'Excel' and self.excel_path is None) or (self.data_type is None) or (
                self.data_type == 'База' and self.db.engine is None):
            widget.data = widget.mock_data
            mbox.showwarning('', 'Необходимо выбрать базу данных')
            return True
        return False

    def get_word_data(self, widget: tk.Frame) -> None:
        """
        Формирование данных data для вывода. Получение сохранённого или нового слова + запись в self.data + запись в
        историю для навигации.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        """

        # Проверяем - возможно запрос на сохранённые данные
        if widget.check_if_show_answer():                           # Если это запрос проверки ответа, то:
            return                                                # Данные из .parent.work_row уже записаны в data

        if widget.parent.work_row:                                  # Если что-то записано в work_row, выводим эти данные
            widget.data = widget.parent.work_row
            widget.parent.work_row = None                           # И сбрасываем сохранение
            return

        # Если нет, генерируем новое случайное слово/фразу
        else:

            # Из Excel
            if widget.parent.choosen_excel_list:                                          # Если выбран лист
                is_empty = widget.parent.excel_is_empty_sheet(widget.parent.choosen_excel_list)
                if is_empty:                                                            # Если выбран пустой лист
                    widget.data = widget.mock_data                                          # Заглушка для вывода данных
                    mbox.showwarning('', 'Выбран пустой лист')
                else:                                                                   # Формирование data
                    widget.data = widget.parent.excel_get_random_row(widget.parent.choosen_excel_list)
            else:
                if widget.parent.data_type == 'Excel':
                    widget.data = widget.parent.excel_get_random_row(widget.parent.choosen_excel_list)

                # Из БД
                elif widget.parent.data_type == 'База':
                    widget.data = widget.parent.db.random_word_from_theme(widget.parent.choosen_db_theme)

        # Запись нового сгенерированного слова в историю попыток
        widget.navigation.add_in_history(widget.data)

    def get_attempts_stat_data_to_show(self, widget: tk.Frame) -> tuple[int, int, int]:
        """
        Получить данные попыток для отображения статистики виджета.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :return: tuple(right, wrong, attempts)
        """

        if not widget.parent.wb and not widget.parent.db.engine:                # Обработка исключения, если нет базы
            return 0, 0, 0

        # Забор данных из Excel
        if widget.parent.data_type == 'Excel':
            if not widget.parent.wb:                                            # Если книги не существует, заглушка
                return 0, 0, 0
            try:
                right, wrong, attempts = widget.parent.excel_get_current_attempts_info(widget.test_type)
                return right, wrong, attempts
            except KeyError:                                        # Если листа не существует, заглушка
                return 0, 0, 0

        # Забор данных из БД
        elif widget.parent.data_type == 'База':
            try:
                right, wrong, attempts = widget.parent.db.get_statistic_data_by_test_type(widget.test_type)
                return right, wrong, attempts
            except KeyError:                                                    # Если листа не существует, заглушка
                return 0, 0, 0

    def check_if_show_answer(self, widget: tk.Frame) -> bool:
        """
        Проверяем на запрос проверки ответа.
        Если требуется ответ, записываем в data данные сохранённой рабочей строки.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        """
        if widget.parent.work_row:                                       # Если запрос ответа, оставляем те же данные
            widget.data = widget.parent.work_row
            widget.parent.work_row = None
            return True
        return False

    def sort_sheet_list(self, data: list) -> list:
        """
        Сортировка списка листов по выбранному пользователем принципу. Возвращает отсортированный список.

        Атрибуты .sorted и .sorting_choose инициализированы в миксине CommonHandlersMixin, при использовании функции
        обращается к ним через Tk, так что проблемы не возникает.

        :param data: list список листов/тем.
        :return: list отсортированный в соответствии с пользовательским выбором
        """

        if self.sorted == self.sorting_choose[1]:
            return sorted(data)
        elif self.sorted == self.sorting_choose[2]:
            return sorted(data, reverse=True)

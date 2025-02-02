"""
Общие обработчики команд для окон приложения.
"""
import datetime
import tkinter as tk
from tkinter import messagebox as mbox

import settings
from Utils import auxiliary_tools as tls
from Utils.auxiliary_tools import replace_none_to_empty_str_in_list


class CommonHandlersMixin:
    """ Общие обработчики. """

    def __init__(self):
        self.sorted = False
        self.sorting_choose = list(settings.SORTING_SHEETS.keys())          # Варианты сортировки

    def handler_excel_save_as(self) -> None:
        """ Обработчик для меню СОХРАНИТЬ КАК книгу Excel. """

        filename = self.excel_save_file_as()
        if filename:
            mbox.showinfo('Сохранение', f"Файл сохранен как:\n{filename}")

    def handler_create_new_excel_structure(self) -> None:
        """
        Обработчик для меню СОЗДАТЬ новую книгу Excel с готовой структурой базы.
        Создаёт и сохраняет по выбранному в диалоговом окне пути готовый к использованию файл с парой тестовых данных.
        """

        # Создаём, настраиваем и сохраняем книгу
        name = self.excel_create_new_workbook_db()
        if name:
            mbox.showinfo('Создание файла', f'Вы создали новую книгу Excel!\n\n{name}')

            # При успешном создании проставляем настройки приложения для Excel
            self.data_type = 'Excel'
            self.excel_path = name
            self.refresh()

    def handler_select_data_type(self, var: str) -> None:
        """
        Обработчик ИЗМЕНИТЬ ТИП БД для меню.
        Фиксирует в родителе выбранный тип БД и запускает функции подключения к выбранному типу.
        Методы .refresh(), .db.disconnect_db() определены в наследующем классе.

        :param var: str обозначение типа базы с данными
        """
        self.data_type = var                                                # Фиксируем тип базы

        # Запуск подключения к выбранной базе
        if var == 'Excel':
            self.handler_select_file_wb()
            self.refresh()

        elif var == 'База':
            self.handler_select_file_sql_db()

    def handler_select_file_wb(self, popup_dialog: tk.Toplevel = None, force_close: bool = False) -> None:
        """
        Обработчик для кнопки / меню ВЫБОР ФАЙЛА Excel.
        Методы .excel_open_file(), .refresh(), .db определены в наследующем классе.

        :param popup_dialog: объект всплывающего окна
        :param force_close: флаг принудительного закрытия всплывающего окна после срабатывания обработчика - если True.
        """

        # Выбор книги Excel и её загрузка
        self.excel_path = self.excel_open_file()
        self.data_type = 'Excel'

        # Сброс настроек и отключение от БД
        self.choosen_db_theme = None
        self.choosen_excel_list = None
        self.db.disconnect_db()
        self.stat_data = None
        self.data_pagi_page = 1
        self.search_data = None
        self.search_key = None

        self.refresh()
        if force_close:                             # Если вызов был из Popup, принудительно закрываем всплывающее окно
            popup_dialog.destroy()

    def handler_select_sheet(self, var: str, cmbbx_list: list[str]) -> None:
        """
        Обработчик кнопки ВЫБРАТЬ ЛИСТ. Фиксирует в родителе str название выбранного листа/темы.
        Метод .refresh() определён в наследующем классе.

        :param var: str данные ввода из Combobox
        :param cmbbx_list: список допустимых названий листа/темы
        """

        # Определяем и валидируем название выбранного листа
        if var:
            if var not in cmbbx_list:                                   # Обработка некорректно введённого значения
                return
            value = None if var == '-' else var

            # Фиксируем в родителе значение выбранного листа/темы
            if self.data_type == 'Excel':
                self.choosen_excel_list = value
            elif self.data_type == 'База':
                self.choosen_db_theme = value
            self.refresh()

    def handler_select_file_sql_db(self) -> None:
        """
        Обработчик для пункта меню ПОДКЛЮЧИТЬСЯ К БД.
        .db, .engine_speech, .choose_color_theme, .refresh должны быть определены внутри наследующего класса.
        """

        # Выбор файла БД и подключение
        self.db.connect_db()
        self.data_type = 'База'

        # Сбросить настройки Excel
        self.excel_path = None
        self.wb = None
        self.choosen_excel_list = None
        self.stat_data = None
        self.data_pagi_page = 1
        self.search_data = None
        self.search_key = None

        # Установка пользовательских настроек приложения
        db_settings = self.db.get_app_settings()                # Забираем все пользовательские настройки БД

        if db_settings:                                         # Если база не новая и настройки существуют:
            speech_voice = db_settings.speech_voice             # Настройка выбора голоса
            if speech_voice:
                self.engine_speech.set_voice(speech_voice)

            speech_volume = db_settings.speech_volume           # Настройка громкости речи
            if speech_volume:
                self.engine_speech.speech_volume = speech_volume
                self.engine_speech.engine.setProperty('volume', speech_volume / 100)

            speech_rate = db_settings.speech_rate               # Настройка скорости речи
            if speech_rate:
                self.engine_speech.speech_rate = speech_rate
                self.engine_speech.engine.setProperty('rate', speech_rate)

            color_theme_db = db_settings.color_theme            # Настройка цветовой темы
            if color_theme_db:
                self.choose_color_theme(color_theme_db)
            else:
                self.refresh()
        else:
            self.refresh()

    def handler_select_sort_type(self, widget: tk.Tk, container: tk.Frame, func: str, in_frame: tk.Frame) -> None:
        """
        Обработчик кнопки сортировки - переключение [False, 'Ascending', 'Descending'].
        Фиксирует в родительской переменной выбранное пользователем значение сортировки и обновляет окно.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :param container: Контейнер Frame для размещения кнопки
        :param func: str название метода сборки контейнера с кнопкой
        :param in_frame: родительский контейнер для container с кнопкой, если он требуется при сборке container
        :return: Функция ничего не возвращает. После обновления окна, благодаря изменению переменной сортировки,
                список листов/тем будет отсортирован автоматически при сборке виджета.
        """

        # Определяем и фиксируем пользовательскую сортировку
        for index, var in enumerate(self.sorting_choose):
            if self.sorted == var:
                try:
                    self.sorted = self.sorting_choose[index + 1]
                except IndexError:
                    self.sorted = self.sorting_choose[0]
                break
            else:
                continue

        # Автоматическое обновление виджета после сортировки
        try:
            widget.parent.refresh(widget, container, func, in_frame)
        except AttributeError:                                                          # Для Popup
            widget.master.refresh(widget, container, func, in_frame)

    def handler_refresh(self, widget: tk.Tk) -> None:
        """ Обработчик иконки ОБНОВИТЬ """
        widget.parent.refresh()

    def handler_previous_word(self, widget: tk.Frame) -> None:
        """
        Обработчик иконки ПРЕДЫДУЩЕЕ СЛОВО. Возвращает к предыдущей записи, обрабатывает историю навигации.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        """
        data = widget.navigation.previous_word()                    # Получаем данные по уменьшившемуся индексу попытки
        widget.parent.work_row = data                               # Записываем их в work_row для отображения
        widget.parent.refresh()

    def handler_next_button(self, widget: tk.Frame) -> None:
        """
        Обработчик кнопки ДАЛЕЕ. Выводит следующее слово/фразу, обрабатывает историю навигации, записывает попытку.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        """

        # Проверка, есть ли за следующим индексом попытки запись в истории попыток
        is_data = widget.navigation.next_word()
        if is_data:
            widget.parent.work_row = is_data                      # Если есть, записываем её в work_row для отображения

        elif widget.parent.data_type == 'База':
            widget.parent.db.create_test_attempt(widget.data[0], 'PASS', widget.test_type)

        widget.set_ch_box()
        widget.parent.refresh()

    def handler_yes_button(self, widget: tk.Frame) -> None:
        """
        Обработчик кнопки ДА. Фиксирует попытку, генерирует следующее слово/фразу.

        :param widget:
        """

        # Проверка, есть ли за следующим индексом попытки запись в истории попыток
        is_data = widget.navigation.next_word()
        if is_data:
            widget.parent.work_row = is_data                      # Если есть, записываем её в work_row для отображения

        widget.set_ch_box()

        # Запись попытки теста
        if widget.parent.data_type == 'Excel':
            widget.parent.excel_write_attempt(widget.parent.excel_path, widget.data[1], 'Верно', widget.test_type)
        if widget.parent.data_type == 'База':
            widget.parent.db.create_test_attempt(widget.data[0], 'YES', widget.test_type)

        widget.parent.refresh()

    def handler_no_button(self, widget) -> None:
        """ Обработчик кнопки НЕТ. Фиксирует попытку, генерирует следующее слово/фразу. """

        # Проверка, есть ли за следующим индексом попытки запись в истории попыток
        is_data = widget.navigation.next_word()
        if is_data:
            widget.parent.work_row = is_data                      # Если есть, записываем её в work_row для отображения

        widget.set_ch_box()

        # Записываем попытку
        if widget.parent.data_type == 'Excel':
            widget.parent.excel_write_attempt(widget.parent.excel_path, widget.data[1], 'Неверно', widget.test_type)
        if widget.parent.data_type == 'База':
            widget.parent.db.create_test_attempt(widget.data[0], 'NO', widget.test_type)

        widget.parent.refresh()

    def handler_write_statistic_button(self, widget: tk.Frame) -> None:
        """
        Обработчик кнопки ЗАПИСАТЬ. Создаёт новый отчёт статистики.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        """

        # Получаем информацию о попытках
        stat_data = widget.get_statistic_data_to_show()
        right, wrong, attempts = stat_data
        if attempts == 0:                                                   # Если не было попыток, обработка
            mbox.showwarning('Ошибка', 'Нет данных для записи')
            return

        # Создаём новый отчёт статистики
        if widget.parent.data_type == 'Excel':                                # Запись в Excel
            topic = widget.parent.choosen_excel_list if widget.parent.choosen_excel_list else '-'
            if widget.parent.excel_write_row_statistic(stat_data, topic, widget.parent.excel_path, widget.test_type):
                mbox.showinfo('Сообщение', f'Создана новая запись от {datetime.datetime.now().date()}')

        elif widget.parent.data_type == 'База':                               # Запись в БД
            if widget.parent.db.create_statistic_report(widget.test_type):
                mbox.showinfo('Сообщение', f'Создан новый отчёт от {datetime.datetime.now().date()}')

        # Сброс записи отчётов статистики в переменной + обновление окна
        widget.parent.refresh(object=widget, container=widget.inner_frame_right,
                              build_function='put_container_statistic', in_frame=widget.wrapper_word_stat)
        widget.parent.stat_data = None

    def handler_show_answer_button(self, widget: tk.Frame) -> None:
        """
        Обработчик кнопки ПОКАЗАТЬ ОТВЕТ. Фиксирует отметку чек-бокса в родителе, сохраняет текущую запись и
        обновляет окно для показа ответа.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        """

        widget.set_ch_box()                                             # Зафиксировать в родителе запрос ответа
        widget.parent.work_row = widget.data                            # Записать данные текущей записи
        widget.parent.refresh()

    def handler_icon_reverso(self, widget: tk.Frame) -> None:
        """
        Обработчик иконки Reverso. Открывает Reverso Context на странице с текущим словом/фразой.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk.
        """

        # Форматируем слово/фразу и преобразуем её к URL-формату
        result = tls.process_string(widget.data[1])
        result = result.strip().replace(' ', '+')

        # Формируем итоговый URL и открываем его
        reverso_url = f'{settings.REVERSO_CONTEXT_BASE_URL_RU}{result}'
        tls.open_url(reverso_url)

    def handler_icon_edit_data(self, widget: tk.Frame) -> None:
        """
        Обработчик иконки перехода к редактированию записи.
        Открывает окно редактирования, после закрытия отображает изменённые данные.

        self.data - список с исходными данными строки:
        [3, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk.
        """
        reset_worklist = False                            # Флаг сброса выбранного листа в родителе - по умолчанию НЕТ

        if widget.parent.data_type == 'Excel':
            if widget.parent.choosen_excel_list is None:  # Если лист не был выбран до обработчика - то флаг сброса True
                reset_worklist = True
        elif widget.parent.data_type == 'База':
            if widget.parent.choosen_db_theme is None:
                reset_worklist = True

        row = widget.data
        row = replace_none_to_empty_str_in_list(row)        # Форматирование данных для исключения ошибок обработки
        widget.parent.popup.edit_row_popup(row)             # Вызов окна редактирования записи

        if reset_worklist:
            widget.parent.choosen_excel_list = None         # Сброс выбранного в Popup листа, если флаг сброса True
            widget.parent.choosen_db_theme = None

        # Достаём изменённые данные строки и записываем её в work_row, чтобы отобразить изменения
        if widget.parent.data_type == 'Excel':
            widget.parent.work_row = widget.parent.excel_get_row_by_id_and_sheet(row)
        if widget.parent.data_type == 'База':
            result = widget.parent.db.get_word_by_id(row[0])
            if result:
                widget.parent.work_row = result

        widget.parent.refresh()                             # Обновляем окно с данными

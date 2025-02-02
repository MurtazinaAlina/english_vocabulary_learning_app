"""
Окно приложения с тестированием перевода с русского языка на английский.
"""
import argostranslate.translate
import tkinter as tk
from tkinter import ttk

import settings
import styles
from Utils.auxiliary_tools import replace_none_to_empty_str_in_list
from Utils.custom_widgets.tooltips import TooltipCursorOnHover


class RuEnWindow(ttk.Frame):
    """ Окно для отображения тестирования ru-en.  """

    def __init__(self, parent):

        super().__init__(parent)
        self.parent = parent

        self.bg = styles.STYLE_COLORS[self.parent.current_color_style]['background']

        self.mock_data = ['' for i in range(0, 5)]                      # Заглушка для данных с пустым выводом
        self.current_say = None                                         # Последний озвучивавшийся контекст
        self.index_context = 0                                          # Индекс примера контекста к озвучке
        self.test_type = settings.TEST_TYPES[1]                         # Тип тестирования для фиксации статистики
        self.navigation = self.parent.navigation_ru_en                  # Тип навигации из родителя

        self.put_widgets()

    def put_widgets(self):
        """ Сборка основного окна страницы """

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        if not self.check_if_not_db():                      # Проверка на подключение к какой-либо базе + заглушка data
            self.get_data()                                 # Формирование self.data для вывода

        self.wrapper_word_stat = ttk.Frame(self)            # обёртка для div со словом (слева) и статистикой (справа)
        self.wrapper_word_stat.grid(row=1, column=0, columnspan=2, sticky='nswe')

        # Сборка основных контейнеров с данными
        self.put_container_choose_sheet()                           # Сборка контейнера выбора листа
        self.put_container_random_word(self.wrapper_word_stat)      # Сборка контейнера с рандомным словом - слева
        self.put_container_statistic(self.wrapper_word_stat)        # Сборка контейнера со статистикой - справа
        self.put_container_check_if_answer()                        # Сборка контейнера с чек-боксом просмотра ответа
        self.put_container_show_answer()                            # Сборка контейнера с ответами

    def put_container_choose_sheet(self) -> None:
        """ Сборка контейнера с выбором листа """

        # Собираем контейнер из родительского метода
        container_choose_sheet = self.parent.put_container_choose_sheet(self, self)
        container_choose_sheet.grid_columnconfigure(0, minsize=143)
        container_choose_sheet.grid(row=0, column=0, sticky='wesn')

    def put_container_random_word(self, wrapper_word_stat) -> None:
        """ Сборка контейнера с рандомным словом """

        # Внутренний контейнер с рандомным словом, перелистыванием, контекстом (слева на странице)
        self.inner_frame_left = tk.Frame(wrapper_word_stat, background=self.bg)
        self.inner_frame_left.grid_columnconfigure(0, minsize=175)
        self.inner_frame_left.grid_columnconfigure(1, minsize=400)
        self.inner_frame_left.grid(row=0, column=0, columnspan=3, sticky='nswe')

        # Контейнер с лейблом и навигацией
        container_lbl_n_navi = tk.Frame(self.inner_frame_left, background=self.bg, width=500)
        container_lbl_n_navi.grid(row=0, column=0, sticky='w')
        container_lbl_n_navi.columnconfigure(0, minsize=480)

        label = ttk.Label(container_lbl_n_navi, text='Слово/Фраза + переведённые примеры: ', style='BlItGrey.TLabel')
        label.grid(row=0, column=0, sticky='w')

        # Иконка перехода к редактированию записи (Если есть данные) - из родительского метода
        if self.data[0]:
            icon_edit = self.parent.put_icon_edit_data(self, container_lbl_n_navi, tltp_x_y=(360, 220))
            icon_edit.grid(row=0, column=1, sticky='e', padx=(0, 15))

        # Контейнер с кнопками навигации - сборка из родителя
        btns_navi_cont = self.parent.put_btns_navi_container(self, container_lbl_n_navi)
        btns_navi_cont.grid(row=0, column=2, sticky='e')

        # Перевод + примеры для вывода в Canvas
        text = ''
        if self.data[1]:
            replace_none_to_empty_str_in_list(self.data)                                # Обработка None
            self.data[3] = self.data[3].strip() if self.data[3] else ''                 # Форматирование
            if self.data[3]:
                self.data[3] = self.data[3][0].capitalize() + self.data[3][1:]

            # Переводим примеры из контекста с английского на русский
            context_to_ru = self.translate_context(self.data[4])

            # Итоговый отформатированный лейбл
            text = (' ' * 50) + 'Слово/Фраза, ПЕРЕВОД:  ' + '\n\n' + self.data[3] + '\n\n' + \
                   (' ' * 60) + 'ПРИМЕРЫ: ' + '\n\n' + context_to_ru

        # Контейнер с Canvas со словом/фразой и переводом примеров
        container_canvas = self.parent.put_container_with_canvas_n_label(
            widget=self, parent_container=self.inner_frame_left, text=text,
            height=160, width=632, wraplength=600, pady=(0, 0))
        container_canvas.grid(row=1, column=0, columnspan=3, rowspan=4, sticky='nsew', pady=(0, 0))

        # Сборка контейнера с кнопками "Да"/"Нет" из родителя
        btn_wrapper = self.parent.put_container_btns_yes_no(self, self.inner_frame_left)
        btn_wrapper.columnconfigure(0, minsize=250)
        btn_wrapper.grid(row=6, column=0, columnspan=2, sticky='w', pady=10)

    def put_container_statistic(self, wrapper_word_stat) -> None:
        """ Сборка контейнера со статистикой ответов"""

        # Собираем контейнер из родительского метода
        self.inner_frame_right = self.parent.put_container_with_stat(self, wrapper_word_stat)
        self.inner_frame_right.grid(row=0, column=3, sticky='n')
        self.inner_frame_right.grid_columnconfigure(0, minsize=50)                              # Отступ слева

    def put_container_check_if_answer(self) -> None:
        """ Контейнер с чек-боксом ПОКАЗЫВАТЬ ОТВЕТЫ и кнопкой сборки контейнера с ответами """

        # Сборка контейнера с содержимым из родителя
        answer_frame = self.parent.put_container_check_if_answer(widget=self, parent_container=self)
        answer_frame.grid(row=2, column=0, sticky='wn')

    def put_container_show_answer(self) -> None:
        """ Сборка контейнера с ответами """

        if not self.parent.show_answer:                                 # Отображение только при включенном чек-боксе
            return

        # Внутренний контейнер с ответами
        self.inner_frame_bottom = tk.Frame(self, background=self.bg)
        self.inner_frame_bottom.grid(row=5, column=0, sticky='w', pady=(0, 0))

        # Слово/Фраза - контейнер со словом и озвучкой
        word_answer_container = tk.Frame(self.inner_frame_bottom, background=self.bg)
        word_answer_container.grid(row=0, column=0, pady=(0, 0))

        label_word = ttk.Label(word_answer_container, text='Слово/Фраза:', style='BlItGrey.TLabel',
                               padding=(20, 10, 20, 0))
        label_word.grid(row=0, column=0, sticky='w')                                   # Лейбл Слово/Фраза

        # Сборка иконки проговаривания Слова/фразы из родителя (при наличии данных)
        if self.data[0]:
            self.parent.put_icon_say_aloud(widget=self, container=word_answer_container)
            TooltipCursorOnHover(self.parent.icon_say_aloud, text='Произнести слово/фразу', x=50, y=554,
                                 hand_cursor=True)
            self.parent.icon_say_aloud.grid(row=0, column=1, sticky='w', padx=(20, 0), pady=(13, 0))

        label_word_answer = ttk.Label(word_answer_container, text=self.data[1], style='Answers.TLabel',
                                      padding=(20, 20, 20, 10))
        label_word_answer.grid(row=0, column=2, sticky='w')                            # Слово/Фраза - ОТВЕТ

        # Транскрипция
        trnscr_answer_container = tk.Frame(self.inner_frame_bottom, background=self.bg)
        trnscr_answer_container.grid(row=1, column=0, columnspan=3, sticky='wn', pady=(0, 0))

        label_trnscr = ttk.Label(trnscr_answer_container, text='Транскрипция:', style='BlItGrey.TLabel',
                                 padding=(20, 5, 20, 10))
        label_trnscr.grid(row=0, column=0, sticky='w')                                 # Лейбл Транскрипция

        label_trnscr_answer = ttk.Label(trnscr_answer_container, text=self.data[2], style='Answers.TLabel',
                                        padding=(56, 5, 20, 10))
        label_trnscr_answer.grid(row=0, column=1, sticky='w')                           # Транскрипция - ОТВЕТ

        # Контекст
        context_answer_container = tk.Frame(self, background=self.bg)                   # Контейнеры для контекста
        context_answer_container.grid(row=7, column=0, columnspan=3, sticky='wn', pady=(0, 0))
        inner_cont = tk.Frame(self, background=self.bg)
        inner_cont.grid(row=7, column=0, columnspan=3, sticky='wn', pady=(0, 0))

        lbl = ttk.Label(inner_cont, text='Контекст:', style='BlItGrey.TLabel', padding=(20, 10, 0, 0))
        lbl.grid(row=0, column=0, sticky='wn')                                          # Лейбл Контекст

        # Сборка иконки озвучки из родителя, если есть примеры
        if self.data[4]:
            self.parent.put_icon_say_aloud(widget=self, container=inner_cont)

            # Переопределяем command=
            self.parent.icon_say_aloud.config(command=self.handler_say_context_partial)
            TooltipCursorOnHover(self.parent.icon_say_aloud, x=50, y=619, hand_cursor=True,
                                 text='Произнести пример.\nЧтобы озвучить следующий,\n нажмите повторно')
            self.parent.icon_say_aloud.grid(row=0, column=1, sticky='wn', padx=(62, 0), pady=(13, 0))

            # Контекст - ОТВЕТ в Canvas. Сборка из родительского метода
            canvas_frame = tk.Frame(inner_cont, background=self.bg)
            canvas_frame.grid(row=0, column=5, sticky='wn', pady=(0, 0))

            container_canvas = self.parent.put_container_with_canvas_n_label(
                widget=self, parent_container=canvas_frame, text=self.data[4],
                height=130, width=430, wraplength=400
            )
            container_canvas.grid(row=0, column=5, sticky='wn', pady=(0, 0))

    def handler_icon_reverso(self):
        """ Обработчик иконки Reverso. Открывает Reverso Context на странице с текущим словом/фразой. """
        self.parent.handler_icon_reverso(self)                                                  # Метод из родителя

    def handler_icon_edit_data(self) -> None:
        """
        Обработчик иконки перехода к редактированию записи.
        Открывает окно редактирования, после закрытия отображает изменённые данные.

        self.data - список с исходными данными строки:
        [3, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
        """
        self.parent.handler_icon_edit_data(self)                                                # Метод из родителя

    def handler_next_button(self) -> None:
        """ Обработчик кнопки ДАЛЕЕ. Выводит следующее слово/фразу. """
        self.parent.handler_next_button(self)                                                   # Метод из родителя

    def handler_icon_previous_word(self) -> None:
        """ Обработчик иконки ПРЕДЫДУЩЕЕ СЛОВО. Возвращает к предыдущей записи """
        self.parent.handler_previous_word(self)                                                 # Метод из родителя

    def handler_yes_button(self) -> None:
        """ Обработчик кнопки ДА. Фиксирует попытку, генерирует следующее слово/фразу. """
        self.parent.handler_yes_button(self)                                                    # Метод из родителя

    def handler_no_button(self) -> None:
        """ Обработчик кнопки НЕТ. Фиксирует попытку, генерирует следующее слово/фразу. """
        self.parent.handler_no_button(self)                                                     # Метод из родителя

    def handler_show_answer_button(self) -> None:
        """ Обработчик кнопки ПОКАЗАТЬ ОТВЕТ. Фиксирует отметку чек-бокса. """
        self.parent.handler_show_answer_button(self)                                            # Метод из родителя

    def handler_write_statistic_button(self) -> None:
        """ Обработчик кнопки ЗАПИСАТЬ. Создаёт новый отчёт статистики. """
        self.parent.handler_write_statistic_button(self)                                        # Метод из родителя

    def handler_say_word(self) -> None:
        """ Обработчик иконки ОЗВУЧИТЬ в транскрипции """
        self.parent.engine_speech.say_out(self.data[1])                                         # Метод из родителя

    def handler_say_context_partial(self) -> None:
        """ Обработчик иконки ОЗВУЧИТЬ в контексте. Озвучивает примеры по одному за каждое нажатие"""

        self.current_say, self.index_context = self.parent.engine_speech.say_out_partial(
            data_list=self.data, current_say=self.current_say, index_context=self.index_context)

    def set_ch_box(self) -> None:
        """ Фиксация в переменных основного окна приложения отметки чек-бокса """
        self.parent.show_answer = self.feature_var.get()

    def translate_context(self, sentence: str) -> str:
        """
        Перевести строку с примерами на русский.

        :param sentence: str с предложениями на английском.
        :return: str с переводом на русский.
        """
        return argostranslate.translate.translate(sentence, "en", "ru")

    def check_if_not_db(self) -> bool:
        """
        Проверка если не выбран тип базы или файл с базой.
        Устанавливает пустые данные-заглушку для отображения визуала контейнеров
        """
        return self.parent.check_if_not_db(self)                                                # Метод из родителя

    def check_if_show_answer(self) -> bool:
        """
        Проверяем на запрос проверки ответа.
        Если требуется ответ, записываем в data данные сохранённой рабочей строки.
        """
        return self.parent.check_if_show_answer(self)                                           # Метод из родителя

    def get_data(self) -> None:
        """ Формирование данных data для вывода. Запись в self.data """
        self.parent.get_word_data(self)                                                         # Метод из родителя

    def get_statistic_data_to_show(self) -> tuple[int, int, int]:
        """ Получить данные для отображения статистики ru-en.

        :return: tuple(right, wrong, attempts)
        """
        return self.parent.get_attempts_stat_data_to_show(self)                                 # Метод из родителя

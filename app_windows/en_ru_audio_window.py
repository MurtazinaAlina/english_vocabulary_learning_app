"""
Окно приложения с тестированием перевода с английского языка на русский по аудио произношения слова.
"""
import tkinter as tk
from tkinter import ttk

import settings
import styles
from Utils.custom_widgets.tooltips import TooltipCursorOnHover


class EnRuAudioWindow(ttk.Frame):
    """ Окно для отображения тестирования en-ru audio. """

    def __init__(self, parent):

        super().__init__(parent)
        self.parent = parent
        self.bg = styles.STYLE_COLORS[self.parent.current_color_style]['background']

        self.mock_data = ['' for i in range(0, 5)]                  # Заглушка для данных с пустым выводом
        self.current_say = None                                     # Последний озвучивавшийся контекст
        self.index_context = 0                                      # Индекс примера контекста к озвучке
        self.test_type = settings.TEST_TYPES[2]                     # Тип тестирования для фиксации статистики
        self.navigation = self.parent.navigation_audio              # Тип навигации из родителя

        self.put_widgets()

    def put_widgets(self) -> None:
        """ Сборка основного окна страницы. """

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
        """ Сборка контейнера с выбором листа. """

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

        # Контейнер с лейблом и иконкой озвучки
        container_lbl_n_say = tk.Frame(self.inner_frame_left, background=self.bg)
        container_lbl_n_say.grid(row=0, column=0, sticky='w')
        container_lbl_n_say.columnconfigure(1, minsize=263)

        label_word = ttk.Label(container_lbl_n_say, text='Прослушать слово/фразу: ', style='BlItGrey.TLabel')
        label_word.grid(row=0, column=0, sticky='w')

        # Сборка иконки проговаривания из родителя common_handlers.py если не заглушка
        if self.data[1]:
            self.parent.put_icon_say_aloud(widget=self, container=container_lbl_n_say)
            TooltipCursorOnHover(self.parent.icon_say_aloud, text='Произнести слово/фразу', x=135, y=222,
                                 hand_cursor=True)
            self.parent.icon_say_aloud.grid(row=0, column=1, sticky='w', padx=(0, 0), pady=(5, 0))

        # Контейнер с кнопками навигации - сборка из родителя
        btns_navi_cont = self.parent.put_btns_navi_container(widget=self, parent_container=container_lbl_n_say)
        btns_navi_cont.grid(row=0, column=3)

        # Контейнер с лейблом и озвучкой контекста
        context_container = tk.Frame(self.inner_frame_left, background=self.bg)
        context_container.grid(row=3, column=0, columnspan=2, sticky='w')

        label_context = ttk.Label(context_container, text='Прослушать в контексте: ', style='BlItGrey.TLabel',
                                  padding=(20, 5, 10, 10))
        label_context.grid(row=0, column=0, sticky='w')                         # Лейбл контекста

        # Сборка иконки озвучки из родителя common_handlers.py, если есть примеры
        if self.data[4]:
            self.parent.put_icon_say_aloud(widget=self, container=context_container)

            # Переопределяем command=
            self.parent.icon_say_aloud.config(command=self.handler_say_context_partial)
            TooltipCursorOnHover(self.parent.icon_say_aloud, x=135, y=256, hand_cursor=True,
                                 text='Произнести пример.\nЧтобы озвучить следующий,\n нажмите повторно')
            self.parent.icon_say_aloud.grid(row=0, column=1, sticky='w', padx=(8, 0), pady=(0, 0))

        # Иконка перехода к редактированию записи (Если есть данные) - из родительского метода
        if self.data[0]:
            icon_edit = self.parent.put_icon_edit_data(self, context_container, tltp_x_y=(530, 270))
            context_container.columnconfigure(1, minsize=410)
            icon_edit.grid(row=0, column=12, sticky='e', padx=(0, 0))

        # Контейнер с кнопками "Да"/"Нет" - сборка из родителя
        btn_wrapper = self.parent.put_container_btns_yes_no(self, self.inner_frame_left)
        btn_wrapper.columnconfigure(0, minsize=320)
        btn_wrapper.grid(row=4, column=0, columnspan=2, sticky='w')

    def put_container_statistic(self, wrapper_word_stat) -> None:
        """ Сборка контейнера со статистикой ответов на тестирование. """

        # Собираем контейнер из родительского метода
        self.inner_frame_right = self.parent.put_container_with_stat(self, wrapper_word_stat)
        self.inner_frame_right.grid(row=0, column=3, sticky='n')
        self.inner_frame_right.grid_columnconfigure(0, minsize=50)                  # Отступ слева

    def put_container_check_if_answer(self) -> None:
        """ Контейнер с чек-боксом ПОКАЗЫВАТЬ ОТВЕТЫ и кнопкой сборки контейнера с ответами. """

        # Сборка контейнера с содержимым из родителя
        answer_frame = self.parent.put_container_check_if_answer(widget=self, parent_container=self.inner_frame_left)
        answer_frame.grid(row=8, column=0, sticky='wse', pady=(95, 0))

    def put_container_show_answer(self) -> None:
        """ Сборка контейнера с ответами. """

        if self.parent.show_answer:                                     # Отображение только при включенном чек-боксе

            # Внутренний контейнер с ответами
            self.inner_frame_bottom = tk.Frame(self, background=self.bg, )
            self.inner_frame_bottom.grid(row=5, column=0, sticky='wesn', pady=(0, 0))

            # Слово/Фраза
            lbl = ttk.Label(self.inner_frame_bottom, text='Слово/Фраза:', style='BlItGrey.TLabel',
                            padding=(20, 0, 20, 0))
            lbl.grid(row=0, column=0, sticky='w')                       # Лейбл Слово/Фраза

            word_answer_container = tk.Frame(self.inner_frame_bottom, background=self.bg)
            word_answer_container.grid(row=0, column=1, sticky='wn')

            label_word_answer = ttk.Label(word_answer_container, text=self.data[1], style='Answers.TLabel')
            label_word_answer.grid(row=0, column=1, sticky='wn')        # ОТВЕТ - Слово/Фраза

            # Транскрипция
            lbl = ttk.Label(self.inner_frame_bottom, text='Транскрипция:', style='BlItGrey.TLabel',
                            padding=(20, 0, 20, 10))
            lbl.grid(row=1, column=0, sticky='wn')                      # Лейбл Транскрипция

            lbl = ttk.Label(self.inner_frame_bottom, text=self.data[2], style='Answers.TLabel', padding=(20, 0, 20, 10))
            lbl.grid(row=1, column=1, sticky='wn')                      # ОТВЕТ - Транскрипция

            # Перевод
            self.inner_frame_bottom.rowconfigure(2, minsize=60)
            lbl = ttk.Label(self.inner_frame_bottom, text='Перевод:', style='BlItGrey.TLabel', padding=(20, 5, 20, 0))
            lbl.grid(row=2, column=0, sticky='wn')                      # Лейбл Перевод

            self.data[3] = self.data[3].strip() if self.data[3] else ''                 # Форматирование для вывода
            if self.data[3]:
                self.data[3] = self.data[3][0].capitalize() + self.data[3][1:]

            label_trnslt_answer = ttk.Label(self.inner_frame_bottom, text=self.data[3], style='Answers.TLabel',
                                            padding=(20, 5, 20, 0))
            label_trnslt_answer.grid(row=2, column=1, sticky='wn')      # ОТВЕТ Перевод

            # Лейбл Контекст
            lbl = ttk.Label(self.inner_frame_bottom, text='Контекст:', style='BlItGrey.TLabel', padding=(20, 40, 0, 0))
            lbl.grid(row=3, column=0, sticky='wn')

            # Контекст - ОТВЕТ в Canvas. Сборка из родительского метода
            container_canvas = self.parent.put_container_with_canvas_n_label(
                widget=self, parent_container=self.inner_frame_bottom, text=self.data[4],
                height=130, width=480, wraplength=430
            )
            container_canvas.grid(row=3, column=1, columnspan=3, rowspan=4, sticky='nsew', pady=(0, 0))

    def handler_icon_reverso(self):
        """ Обработчик иконки Reverso. Открывает Reverso Context на странице с текущим словом/фразой. """
        self.parent.handler_icon_reverso(self)                                                  # Метод из родителя

    def set_ch_box(self) -> None:
        """ Фиксация в переменных основного окна приложения отметки чек-бокса. """
        self.parent.show_answer = self.feature_var.get()

    def check_if_show_answer(self) -> bool:
        """
        Проверяем на запрос проверки ответа.
        Если требуется ответ, записываем в data данные сохранённой рабочей строки.
        """
        return self.parent.check_if_show_answer(self)                                           # Метод из родителя

    def check_if_not_db(self) -> bool:
        """
        Проверка если не выбран тип базы или файл с базой.
        Устанавливает пустые данные-заглушку для отображения визуала контейнеров.
        """
        return self.parent.check_if_not_db(self)                                                # Метод из родителя

    def handler_icon_edit_data(self) -> None:
        """
        Обработчик иконки перехода к редактированию записи.
        Открывает окно редактирования, после закрытия отображает изменённые данные.

        self.data - список с исходными данными строки:
        [3, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
        """
        self.parent.handler_icon_edit_data(self)                                                # Метод из родителя

    def handler_show_answer_button(self) -> None:
        """ Обработчик кнопки ПОКАЗАТЬ ОТВЕТ. Фиксирует отметку чек-бокса. """
        self.parent.handler_show_answer_button(self)                                            # Метод из родителя

    def handler_next_button(self) -> None:
        """ Обработчик кнопки ДАЛЕЕ. Выводит следующее слово/фразу. """
        self.parent.handler_next_button(self)                                                   # Метод из родителя

    def handler_icon_previous_word(self) -> None:
        """ Обработчик иконки ПРЕДЫДУЩЕЕ СЛОВО. Возвращает к предыдущей записи. """
        self.parent.handler_previous_word(self)                                                 # Метод из родителя

    def handler_yes_button(self) -> None:
        """ Обработчик кнопки ДА. Фиксирует попытку, генерирует следующее слово/фразу. """
        self.parent.handler_yes_button(self)                                                    # Метод из родителя

    def handler_no_button(self) -> None:
        """ Обработчик кнопки НЕТ. Фиксирует попытку, генерирует следующее слово/фразу. """
        self.parent.handler_no_button(self)                                                     # Метод из родителя

    def handler_say_word(self) -> None:
        """ Обработчик иконки ОЗВУЧИТЬ в транскрипции """
        self.parent.engine_speech.say_out(self.data[1])                                         # Метод из родителя

    def handler_say_context_partial(self) -> None:
        """ Обработчик иконки ОЗВУЧИТЬ в контексте. Озвучивает примеры по одному за каждое нажатие."""

        self.current_say, self.index_context = self.parent.engine_speech.say_out_partial(
            data_list=self.data, current_say=self.current_say, index_context=self.index_context)

    def handler_write_statistic_button(self) -> None:
        """ Обработчик кнопки ЗАПИСАТЬ. Создаёт новый отчёт статистики. """
        self.parent.handler_write_statistic_button(self)                                        # Метод из родителя

    def get_data(self) -> None:
        """ Формирование данных data для вывода. Запись в self.data. """
        self.parent.get_word_data(self)                                                         # Метод из родителя

    def get_statistic_data_to_show(self) -> tuple[int, int, int]:
        """ Получить данные для отображения статистики en > ru AUDIO.

        :return: tuple(right, wrong, attempts)
        """
        return self.parent.get_attempts_stat_data_to_show(self)                                 # Метод из родителя

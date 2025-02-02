import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import settings
import styles
from Utils.custom_widgets.custom_label import HighlightableLabel
from Utils.custom_widgets.tooltips import TooltipCursorOnHover


class EnRuWindow(ttk.Frame):
    """ Окно для вывода en -> ru: word данных """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.bg = styles.STYLE_COLORS[self.parent.current_color_style]['background']
        self.mock_data = ['' for i in range(0, 5)]                      # Заглушка для данных с пустым выводом
        self.current_say = None                                         # Последний озвучивавшийся контекст
        self.index_context = 0                                          # Индекс примера контекста к озвучке
        self.test_type = settings.TEST_TYPES[0]                         # Тип тестирования для фиксации статистики
        self.navigation = self.parent.navigation                        # Тип навигации из родителя

        self.put_widgets()

    def put_widgets(self) -> None:
        """ Сборка основного окна страницы """

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2, minsize=400)     # Min ширина столбца B на уровне родительского div
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=3)
        self.grid_columnconfigure(5, weight=1)

        if not self.check_if_not_db():                      # Проверка на подключение к какой-либо базе + заглушка data
            self.get_data()                                 # Формирование self.data для вывода

        self.put_container_choose_sheet()                   # Сборка контейнеры выбора листа
        self.wrapper_word_stat = ttk.Frame(self)            # обёртка для div со словом (слева) и статистикой (справа)
        self.wrapper_word_stat.grid(row=1, column=0, columnspan=3, sticky='nswe')
        self.put_container_random_word(self.wrapper_word_stat)      # Сборка контейнера с рандомным словом - слева
        self.put_container_statistic(self.wrapper_word_stat)        # Сборка контейнера со статистикой - справа
        self.put_container_check_if_answer()                        # Сборка контейнера с чек-боксом просмотра ответа
        self.put_container_show_answer()                            # Сборка контейнера с ответами

    def put_container_choose_sheet(self) -> None:
        """ Сборка контейнера с выбором листа """

        # Собираем контейнер из родительского метода
        container_choose_sheet = self.parent.put_container_choose_sheet(self, self)
        container_choose_sheet.grid_columnconfigure(0, minsize=141)         # Устанавливаем ширину пустого столбца 0
        container_choose_sheet.grid(row=0, column=0, sticky='wesn')

    def put_container_random_word(self, wrapper_word_stat) -> None:
        """ Сборка контейнера с рандомным словом """

        # Внутренний контейнер с рандомным словом, перелистыванием, контекстом (слева на странице)
        inner_frame_left = tk.Frame(wrapper_word_stat, background=self.bg)
        inner_frame_left.grid_columnconfigure(0, minsize=175)
        inner_frame_left.grid_columnconfigure(1, minsize=400)
        inner_frame_left.grid(row=0, column=0, columnspan=3, sticky='nswe')

        # Контейнер с лейблом и иконкой НАЗАД
        container_label_with_icon_rewind = tk.Frame(inner_frame_left, background=self.bg)
        container_label_with_icon_rewind.grid(row=0, column=0, sticky='w')

        label_word = ttk.Label(container_label_with_icon_rewind, text='Слово/Фраза: ', style='BlItGrey.TLabel')
        label_word.grid(row=0, column=0, sticky='w')                                # Лейбл

        # Поле со случайно выбранным словом
        self.random_word = HighlightableLabel(inner_frame_left, text=self.data[1], style='Cell.TLabel', window=self,
                                              is_tip=True)
        self.random_word.grid(row=0, column=1, columnspan=2, sticky='we')

        # Кнопка ДАЛЕЕ
        btn_next_word = ttk.Button(inner_frame_left, text='Далее', command=self.handler_next_button, style='h2.TButton')
        btn_next_word.grid(row=0, column=3, sticky='e')

        # Иконка НАЗАД
        image = Image.open(settings.ICON_REWIND_BACK['path'])
        image = image.resize((22, 22))
        icon = ImageTk.PhotoImage(image)
        icon_previous_word = tk.Button(container_label_with_icon_rewind, bd=0, background=self.bg, image=icon,
                                command=self.handler_icon_previous_word)
        icon_previous_word.image = icon
        icon_previous_word.grid(row=0, column=1, sticky='w', padx=0)
        TooltipCursorOnHover(icon_previous_word, x=27, y=217, text='Вернуться к предыдущему слову', hand_cursor=True)

        # Контейнер с кнопками "Да"/"Нет" - сборка из родителя
        btn_wrapper = self.parent.put_container_btns_yes_no(self, inner_frame_left)
        btn_wrapper.columnconfigure(0, minsize=75)
        btn_wrapper.grid(row=1, column=1, columnspan=2, ipadx=25)

        # Блок с отображением контекста
        context_container = tk.Frame(inner_frame_left, background=self.bg)
        context_container.grid(row=2, column=0, columnspan=2, sticky='w')       # Контейнер с лейблом и кнопкой озвучки

        label_context = ttk.Label(context_container, text='Контекст употребления: ', style='BlItGrey.TLabel',
                                  padding=(20, 20, 10, 20))
        label_context.grid(row=0, column=0, columnspan=2, sticky='w')           # Лейбл контекста

        # Собираем иконку озвучки примеров из родителя, переопределяем command (Если есть примеры)
        if self.data[4]:
            self.parent.put_icon_say_aloud(widget=self, container=context_container)
            self.parent.icon_say_aloud.config(command=self.handler_say_context_partial)
            TooltipCursorOnHover(self.parent.icon_say_aloud, x=115, y=300, hand_cursor=True,
                                 text='Произнести пример.\nЧтобы озвучить следующий,\n нажмите повторно')
            self.parent.icon_say_aloud.grid(row=0, column=2, sticky='w', padx=(0, 0), pady=(3, 0))

        # Иконка перехода к редактированию записи (Если есть данные) - из родительского метода
        if self.data[0]:
            icon_edit = self.parent.put_icon_edit_data(self, inner_frame_left, tltp_x_y=(525, 303))
            icon_edit.grid(row=2, column=3, sticky='e')

        # Сборка контейнера с примерами контекста в Canvas со скролл-баром.
        cont_canvas = self.parent.put_container_with_canvas_n_label(
            widget=self, parent_container=inner_frame_left, text=self.data[4],
            width=630, height=200, wraplength=600, pady=(0, 0)
        )
        cont_canvas.grid(row=3, column=0, columnspan=4, rowspan=4, sticky='nsew')

    def put_container_statistic(self, wrapper_word_stat) -> None:
        """ Сборка контейнера со статистикой """

        # Собираем контейнер из родительского метода
        self.inner_frame_right = self.parent.put_container_with_stat(self, wrapper_word_stat)
        self.inner_frame_right.grid(row=0, column=4, sticky='en')
        self.inner_frame_right.grid_columnconfigure(0, minsize=450)                          # Отступ слева

    def put_container_check_if_answer(self) -> None:
        """ Контейнер с чек-боксом ПОКАЗЫВАТЬ ОТВЕТЫ и кнопкой сборки контейнера с ответами """

        # Сборка контейнера с содержимым из родителя
        answer_frame = self.parent.put_container_check_if_answer(widget=self, parent_container=self)
        answer_frame.grid(row=7, column=0, sticky='wsne', pady=0)

    def put_container_show_answer(self) -> None:
        """ Сборка контейнера с транскрипцией и переводом """

        if self.parent.show_answer:                                     # Отображение только при включенном чек-боксе
            # Внутренний контейнер с ответами - внизу
            self.inner_frame_bottom = tk.Frame(self, background=self.bg)
            self.inner_frame_bottom.grid(row=8, column=0, sticky='wes')

            # Транскрипция
            label_trnscr = ttk.Label(self.inner_frame_bottom, text='Транскрипция:', style='BlItGrey.TLabel')
            label_trnscr.grid(row=3, column=0, sticky='ws')                                 # Лейбл

            transcr_answer_container = tk.Frame(self.inner_frame_bottom, background=self.bg)
            transcr_answer_container.grid(row=3, column=1, sticky='ws')

            # Сборка иконки проговаривания Слово/фраза из родителя common_handlers.py (при наличии данных)
            if self.data[0]:
                self.parent.put_icon_say_aloud(widget=self, container=transcr_answer_container)
                TooltipCursorOnHover(self.parent.icon_say_aloud, text='Произнести слово/фразу', x=50, y=640,
                                     hand_cursor=True)
                self.parent.icon_say_aloud.grid(row=0, column=0, sticky='w', padx=(20, 0))

            label_trnscr_answer = ttk.Label(transcr_answer_container, text=self.data[2], style='Answers.TLabel')
            label_trnscr_answer.grid(row=0, column=1, sticky='ws')                          # Транскрипция - написание

            # Перевод
            label_trnslt = ttk.Label(self.inner_frame_bottom, text='Перевод:', style='BlItGrey.TLabel', padding=(20, 0))
            label_trnslt.grid(row=4, column=0, sticky='wn')                                 # Лейбл

            if self.data[3]:
                self.data[3] = self.data[3][0].capitalize() + self.data[3][1:]
            label_trnslt_answer = ttk.Label(self.inner_frame_bottom, text=self.data[3], style='Answers.TLabel',
                                            padding=(20, 0))
            label_trnslt_answer.grid(row=4, column=1, sticky='wn')                          # Перевод

    def handler_icon_reverso(self):
        """ Обработчик иконки Reverso. Открывает Reverso Context на странице с текущим словом/фразой. """
        self.parent.handler_icon_reverso(self)                                              # Метод из родителя

    def set_ch_box(self) -> None:
        """ Фиксация в переменных основного окна отметки чек-бокса """
        self.parent.show_answer = self.feature_var.get()

    def handler_say_word(self):
        """ Обработчик иконки ОЗВУЧИТЬ в транскрипции """
        self.parent.engine_speech.say_out(self.data[1])                                     # Метод из родителя

    def handler_say_context_partial(self):
        """ Обработчик иконки ОЗВУЧИТЬ в контексте.
         Озвучивает примеры по одному за каждое нажатие"""

        self.current_say, self.index_context = self.parent.engine_speech.say_out_partial(
            data_list=self.data, current_say=self.current_say, index_context=self.index_context)

    def handler_show_answer_button(self) -> None:
        """ Обработчик кнопки ПОКАЗАТЬ ОТВЕТ """
        self.parent.handler_show_answer_button(self)                                        # Метод из родителя

    def handler_next_button(self) -> None:
        """ Обработчик кнопки ДАЛЕЕ """
        self.parent.handler_next_button(self)                                               # Метод из родителя

    def handler_yes_button(self) -> None:
        """ Обработчик кнопки ДА """
        self.parent.handler_yes_button(self)                                                # Метод из родителя

    def handler_no_button(self) -> None:
        """ Обработчик кнопки НЕТ """
        self.parent.handler_no_button(self)                                                 # Метод из родителя

    def handler_icon_previous_word(self) -> None:
        """ Обработчик иконки ПРЕДЫДУЩЕЕ СЛОВО """
        self.parent.handler_previous_word(self)                                             # Метод из родителя

    def handler_icon_edit_data(self) -> None:
        """
        Обработчик иконки перехода к редактированию записи.
        Открывает окно редактирования, после закрытия отображает изменённые данные.

        self.data - список с исходными данными строки:
        [3, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
        """
        self.parent.handler_icon_edit_data(self)                                            # Метод из родителя

    def handler_write_statistic_button(self) -> None:
        """ Обработчик кнопки ЗАПИСАТЬ для записи статистики в xsl файл/БД """
        self.parent.handler_write_statistic_button(self)                                    # Метод из родителя

    def check_if_show_answer(self) -> bool:
        """
        Проверяем на запрос проверки ответа.
        Если требуется ответ, записываем в data данные сохранённой рабочей строки.
        """
        return self.parent.check_if_show_answer(self)                                       # Метод из родителя

    def check_if_not_db(self) -> bool:
        """
        Проверка если не выбран тип базы или файл с базой.
        Устанавливает пустые данные-заглушку для отображения визуала контейнеров
        """
        return self.parent.check_if_not_db(self)                                            # Метод из родителя

    def get_data(self) -> None:
        """ Формирование данных data для вывода. Запись в self.data """
        self.parent.get_word_data(self)                                                     # Метод из родителя

    def get_statistic_data_to_show(self) -> tuple[int, int, int]:
        """ Получить данные для статистики en > ru

        :return: tuple(right, wrong, attempts)
        """
        return self.parent.get_attempts_stat_data_to_show(self)                             # Метод из родителя

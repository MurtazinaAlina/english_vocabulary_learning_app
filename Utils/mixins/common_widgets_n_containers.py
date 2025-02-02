import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import settings
import styles
from Utils import auxiliary_tools as tls
from Utils.custom_widgets.hover_btn_text import HoverButton
from Utils.custom_widgets.tooltips import TooltipCursorOnHover


class CommonWidgetsMixin:
    """ Общие виджеты и контейнеры """

    def __init__(self):
        pass

    def put_icon_refresh(self, widget: tk.Tk, container: tk.Frame) -> tk.Button:
        """
        Иконка ОБНОВИТЬ страницу.
        После вызова функции возвращенный виджет необходимо разместить/отконфигурировать по стилю.
        Функция обработки уже определена в методе.

        :param widget: класс-наследник tk.Tk.
        :param container: контейнер, в котором будет размещён виджет.
        :return: виджет иконки
        """
        image = Image.open(settings.ICON_REFRESH['path'])
        image = image.resize((24, 24))
        icon = ImageTk.PhotoImage(image)
        btn_refresh_icon = tk.Button(container, image=icon, bd=0, command=lambda: self.handler_refresh(widget))
        btn_refresh_icon.image = icon

        # Подсказка + изменение курсора при наведении
        TooltipCursorOnHover(btn_refresh_icon, text="Обновить страницу", x=1100, y=112, hand_cursor=True)

        return btn_refresh_icon

    def put_icon_chrome_reverso(self, widget: tk.Frame, parent_container: tk.Frame) -> tk.Button:
        """
        Кнопка-иконка Перехода в Reverso Context по текущему слову.
        После вызова функции возвращенный виджет необходимо разместить.
        Функция обработки уже определена в методе, должна присутствовать в widget.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk.
        :param parent_container: контейнер окна, в котором будет размещён виджет.
        :return: виджет иконки
        """
        image = Image.open(settings.ICON_CHROME['path'])
        image = image.resize((20, 20))
        icon = ImageTk.PhotoImage(image)
        icon_reverso = HoverButton(parent_container, background=widget.bg, bd=0, image=icon,
                                   text='Перейти в Reverso Context ', compound=tk.RIGHT, fg=styles.DARK_BLUE_FG_MAIN,
                                   command=widget.handler_icon_reverso)
        icon_reverso.image = icon

        return icon_reverso

    def put_icon_edit_data(self, widget: tk.Frame, parent_container: tk.Frame, tltp_x_y: tuple[int, int]) -> tk.Button:
        """
        Иконка редактирования записи слова/фразы. Запускает всплывающее окно с данными для редактирования.
        После вызова функции возвращенный виджет необходимо разместить.
        Функция обработки уже определена в методе, должна присутствовать в widget.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk.
        :param parent_container: контейнер окна, в котором будет размещён виджет.
        :param tltp_x_y: кортеж с координатами для размещения подсказки.
        :return: виджет иконки
        """

        # Иконка РЕДАКТИРОВАТЬ ЗАПИСЬ
        image = Image.open(settings.ICON_EDIT_SHEET['path'])
        image = image.resize((20, 20))
        icon = ImageTk.PhotoImage(image)
        icon_edit = tk.Button(parent_container, background=widget.bg, bd=0, image=icon,
                              command=widget.handler_icon_edit_data)
        icon_edit.image = icon

        # Всплывающая подсказка
        TooltipCursorOnHover(icon_edit, text='Перейти к редактированию записи', x=tltp_x_y[0], y=tltp_x_y[1],
                             hand_cursor=True)

        return icon_edit

    def put_icon_search_in_filter(self, widget: tk.Frame, parent_container: tk.Frame,
                                  tooltip_x_y: tuple = (20, 210)) -> tk.Button:
        """
        Иконка поиска с подсказкой в Combobox выбора листов.
        После вызова функции возвращенный контейнер необходимо разместить.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :param parent_container: контейнер окна, в котором будет размещена иконка
        :param tooltip_x_y: кортеж с координатами для размещения подсказки (если нестандартные)
        :return: виджет иконки
        """
        image = Image.open(settings.ICON_SEARCH_IN_SHEETS['path'])
        image = image.resize((17, 17))
        icon = ImageTk.PhotoImage(image)
        self.icon_search_in_sheets = tk.Button(parent_container, image=icon, bd=0,  command=None, bg=widget.bg,
                                               relief="flat", activebackground=widget.bg, highlightthickness=0)
        self.icon_search_in_sheets.image = icon

        # Объявление подсказки
        TooltipCursorOnHover(self.icon_search_in_sheets, x=tooltip_x_y[0], y=tooltip_x_y[1],
                             text="Для поиска начните вводить часть названия,\nфильтрация применится автоматически",
                             )
        return self.icon_search_in_sheets

    def put_icon_sort_sheets(self, widget: tk.Tk, container: tk.Frame, func: str,
                             in_frame: tk.Frame | None = None) -> None:
        """
        Кнопка сортировки листов в Combobox выбора.
        Функция обработки уже определена в методе, должна присутствовать в Tk(или его миксинах).

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :param container: Контейнер Frame для размещения кнопки
        :param func: str название метода сборки контейнера container с кнопкой
        :param in_frame: родительский контейнер для container с кнопкой, если он не находится напрямую в self виджета
        :return: Функция ничего не возвращает, но из родителя после вызова функции становится доступна
                кнопка self.btn_sort_sheets
        """
        image = Image.open(settings.ICON_SORT_SHEETS['path'])
        image = image.resize((13, 13))
        icon = ImageTk.PhotoImage(image)
        self.btn_sort_sheets = ttk.Button(
            container, image=icon, command=lambda: self.handler_select_sort_type(widget, container, func, in_frame))
        self.btn_sort_sheets.image = icon

    def put_container_choose_sheet(self, widget: tk.Frame, parent_container: tk.Frame, with_sorting: bool = True,
                                   tooltip_x_y: tuple[int, int] = (30, 150), with_reverso: bool = True) -> tk.Frame:
        """
        Сборка контейнера с выбором листа. Собирает лейбл, иконку с подсказкой, Combobox с выбором, кнопку сортировки
        (опционально) и кнопку выбора листа + заполняет Combobox + настроена фильтрация и сортировка (опционально).
        После вызова функции возвращенный контейнер необходимо разместить, при необходимости отконфигурировать
        ширину столбцов.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :param parent_container: контейнер окна, в котором будет размещён контейнер с выбором
        :param tooltip_x_y: кортеж с координатами для размещения подсказки фильтрации поиска (если нестандартные)
        :param with_sorting: bool требуется ли сборка кнопки сортировки, True если да. Корректно сработает только если
                            parent_container == widget (для refresh) + учитывать координаты подсказки.
        :param with_reverso: bool Размещать ли ссылку на Reverso Context, True если да
        :return: виджет с контейнером выбора листа
        """
        container_choose_sheet = ttk.Frame(parent_container)

        # Настраиваем лейбл
        text = 'Выбрать тему' if widget.parent.db.engine else 'Выбрать лист'
        lbl = ttk.Label(container_choose_sheet, text=text, style='BlItGrey.TLabel', padding=(20, 20, 15, 20))
        lbl.grid(row=0, column=0, sticky='w')

        # Иконка поиска с подсказкой - сборка из родительского метода
        x_y = {'tooltip_x_y': tooltip_x_y} if tooltip_x_y else {}  # Координаты будут по виджету, если не передано иное

        icon_search_in_sheets = widget.parent.put_icon_search_in_filter(parent_container=container_choose_sheet,
                                                                        widget=widget, **x_y)
        icon_search_in_sheets.grid(row=0, column=1, sticky='e', padx=3)

        # Формируем список листов Excel / тем в БД
        if widget.parent.data_type == 'Excel':
            widget.cmbbx_list = widget.parent.excel_get_list_all_sheets() if widget.parent.wb else []
        elif widget.parent.data_type == 'База':
            widget.cmbbx_list = widget.parent.db.get_list_all_themes() if widget.parent.db.engine else []
        else:
            widget.cmbbx_list = []                                              # Заглушка при отсутствии выбора базы

        if widget.parent.sorted:                                # Сортируем полученный список по заданной настройке
            widget.cmbbx_list = widget.parent.sort_sheet_list(widget.cmbbx_list)
        widget.cmbbx_list.insert(0, '-')

        # Определяем выбранный лист/тему для отображения в Combobox
        set_cmbbx_value = []                                                    # Заглушка
        if widget.parent.data_type == 'Excel':
            set_cmbbx_value = widget.parent.choosen_excel_list if widget.parent.choosen_excel_list else '-'
        elif widget.parent.data_type == 'База':
            set_cmbbx_value = widget.parent.choosen_db_theme if widget.parent.choosen_db_theme else '-'

        # Combobox с выбором листа/темы
        widget.choose_list = ttk.Combobox(container_choose_sheet, values=widget.cmbbx_list, width=59)
        widget.choose_list.set(set_cmbbx_value)                                   # Отображение выбранного листа
        widget.choose_list.grid(row=0, column=2, sticky='ew', pady=20)

        # Настройка фильтра выпадающего списка на основе введенного в поле значения
        widget.choose_list.bind("<KeyRelease>", lambda event: widget.parent.on_key_release_filter_by_search(
            event, value_list=widget.cmbbx_list, cmbbx_form=widget.choose_list))

        # Кнопка ВЫБРАТЬ ЛИСТ/ТЕМУ
        text = 'Выбрать тему' if widget.parent.db.engine else 'Выбрать лист'
        widget.btn_choose_list = ttk.Button(container_choose_sheet, text=text, style='List.TButton',
                                          command=lambda: widget.parent.handler_select_sheet(
                                              widget.choose_list.get(), widget.cmbbx_list))
        widget.btn_choose_list.grid(row=0, column=4, sticky='ew')

        # Сборка кнопки сортировки из родителя - если не передано False
        if with_sorting:
            widget.parent.put_icon_sort_sheets(container=container_choose_sheet, widget=widget,
                                               func='put_container_choose_sheet')
            widget.parent.btn_sort_sheets.grid(row=0, column=3, sticky='w')
            TooltipCursorOnHover(widget.parent.btn_sort_sheets, x=425, y=155,
                                 text=f'Изменить сортировку на:\n{settings.SORTING_SHEETS[widget.parent.sorted]}')

        # Сборка Иконки-ссылки на Reverso Context на странице с текущим словом/фразой, если with_reverso=True
        if with_reverso:
            icon_reverso = self.put_icon_chrome_reverso(widget, container_choose_sheet)
            icon_reverso.grid(row=0, column=5, padx=(140, 0))

        return container_choose_sheet

    def put_container_with_stat(self, widget: tk.Frame, parent_container: tk.Frame) -> tk.Frame:
        """
        Контейнер со статистикой для окна приложения. Функции-обработчики уже заданы.
        После вызова функции возвращенный контейнер необходимо разместить, при необходимости отконфигурировать
        ширину столбцов.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :param parent_container: контейнер окна, в котором будет размещён контейнер со статистикой
        :return: виджет с контейнером
        """

        inner_frame_right = ttk.Frame(parent_container)  # Внутренний контейнер со статистикой - справа

        # Забираем данные для отображения
        right, wrong, attempts = widget.get_statistic_data_to_show()
        current_percent = round(right / attempts * 100, 1) if attempts != 0 else 0

        # Статистика - визуализация
        label_stat_header = ttk.Label(inner_frame_right, text='Статистика ответов', style='BlItGrey.TLabel')
        label_stat_header.grid(row=0, column=1, columnspan=2, sticky='we')                      # Лейбл-заголовок

        label_stat_right = ttk.Label(inner_frame_right, text='Верно:', style='StatGrey.TLabel')
        label_stat_right.grid(row=1, column=1, sticky='e')                                      # Лейбл ВЕРНО

        label_data_stat_right = ttk.Label(inner_frame_right, text=right, style='StatGreen.TLabel')
        label_data_stat_right.grid(row=1, column=2, sticky='w')                                 # ВЕРНО - цифры

        label_stat_wrong = ttk.Label(inner_frame_right, text='Ошибка:', style='StatGrey.TLabel')
        label_stat_wrong.grid(row=2, column=1, sticky='e')                                      # Лейбл ОШИБКА

        label_data_stat_wrong = ttk.Label(inner_frame_right, text=wrong, style='StatRed.TLabel')
        label_data_stat_wrong.grid(row=2, column=2, sticky='w')                                 # ОШИБКА - цифры

        label_stat_percent = ttk.Label(inner_frame_right, text='Результат:', style='StatGrey.TLabel')
        label_stat_percent.grid(row=3, column=1, sticky='e')                                    # Лейбл РЕЗУЛЬТАТ

        label_data_stat_percent = ttk.Label(inner_frame_right, text=f'{current_percent} %',
                                            style=tls.get_percent_style(current_percent))
        label_data_stat_percent.grid(row=3, column=2, sticky='w')                               # РЕЗУЛЬТАТ - %

        # Кнопка - запись результата
        btn_write_result = ttk.Button(inner_frame_right, text='Записать результат', style='h2.TButton',
                                      command=widget.handler_write_statistic_button)
        btn_write_result.grid(row=4, column=1, columnspan=2)

        return inner_frame_right

    def put_container_btns_yes_no(self, widget: tk.Frame, parent_container: tk.Frame) -> tk.Frame:
        """
        Сборка контейнера с кастомными кнопками "Да"/"Нет". Функции-обработчики уже заданы.
        После вызова функции возвращенный контейнер необходимо разместить, при необходимости отконфигурировать
        ширину столбцов.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :param parent_container: контейнер окна, в котором будет размещён контейнер с кнопками
        :return: виджет с контейнером
        """
        btn_wrapper = tk.Frame(parent_container, background=widget.bg)

        # Кнопка ДА
        image = Image.open(settings.ICON_YES['path'])
        image = image.resize((15, 15))
        icon = ImageTk.PhotoImage(image)
        btn_yes = ttk.Button(btn_wrapper, image=icon, text='Да', compound=tk.LEFT, command=widget.handler_yes_button,
                             style='Yes.TButton')
        btn_yes.image = icon
        btn_yes.grid(row=0, column=1)

        # Кнопка НЕТ
        image = Image.open(settings.ICON_NO['path'])
        image = image.resize((15, 15))
        icon = ImageTk.PhotoImage(image)
        btn_no = ttk.Button(btn_wrapper, image=icon, text='Нет', compound=tk.LEFT, command=widget.handler_no_button,
                            style='No.TButton')
        btn_no.image = icon
        btn_no.grid(row=0, column=2)

        return btn_wrapper

    def put_container_check_if_answer(self, widget: tk.Frame, parent_container: tk.Frame) -> tk.Frame:
        """
        Контейнер с чек-боксом ПОКАЗЫВАТЬ ОТВЕТЫ и кнопкой сборки контейнера с ответами.
        Функция-обработчик уже задана.
        После вызова функции возвращенный контейнер необходимо разместить.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :param parent_container: контейнер окна, в котором будет размещён контейнер с чек-боксом и кнопкой
        :return: виджет с контейнером
        """

        # Общий и внутренний контейнеры для чек-бокса
        answer_frame = tk.Frame(parent_container, background=widget.bg)

        chbx_frame = ttk.Frame(answer_frame, padding=(0, 30, 0, 0))
        chbx_frame.grid(row=0, column=0, sticky='nswe')

        # Чек-бокс запроса ответов
        widget.feature_var = tk.BooleanVar()
        widget.feature_var.set(widget.parent.show_answer)                       # Автозаполнение по данным из родителя
        widget.feature_checkbutton = ttk.Checkbutton(chbx_frame, text='Отображать ответы', variable=widget.feature_var,
                                                     style='TCheckbutton')
        widget.feature_checkbutton.grid(row=0, column=0, sticky='w', padx=20)

        # Кнопка подтверждения
        btn_show_answer = ttk.Button(chbx_frame, text='Применить', command=widget.handler_show_answer_button)
        btn_show_answer.grid(row=0, column=1, sticky='w')

        return answer_frame

    def put_container_with_canvas_n_label(self, widget: tk.Frame, parent_container: tk.Frame, text: str,
                                          height: int = 130, width: int = 630, wraplength: int = 600,
                                          pady: tuple[int, int] = (10, 0)) -> tk.Frame:
        """
        Сборка контейнера с Canvas по заданным настройкам, в котором отобразится переданный текстовый лейбл.
        После вызова функции необходимо будет разместить возвращённый виджет.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :param parent_container: контейнер окна, в котором будет размещён контейнер с Canvas
        :param text: str текст, который будет отображаться в Canvas
        :param height: высота виджета Canvas
        :param width: ширина виджета Canvas
        :param wraplength: ширина области размещения текста в Canvas - для переноса текста лейбла
        :param pady: кортеж с отступами y
        :return: tk.Frame созданный настроенный container_canvas с текстом
        """

        # Внешний контейнер
        container_canvas = tk.Frame(parent_container, bg=widget.bg)
        container_canvas.columnconfigure(0, minsize=20)

        # Внутренний контейнер
        cont_canvas_inner = tk.Frame(container_canvas, background=widget.bg)
        cont_canvas_inner.grid(row=0, column=1, columnspan=3, rowspan=4, sticky='nsew', pady=pady)

        # Canvas - создание объекта
        canvas = tk.Canvas(cont_canvas_inner, bg='white', height=height, width=width)
        canvas.grid(row=0, column=1, columnspan=4, rowspan=4, sticky='nsew')

        # Scrollbar - прокрутка канваса
        scrollbar = tk.Scrollbar(cont_canvas_inner, orient='vertical', command=canvas.yview)
        scrollbar.grid(row=0, column=5, rowspan=4, sticky='ns')
        canvas.configure(yscrollcommand=scrollbar.set)

        # ТЕКСТ контекста - размещение
        label_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=label_frame, anchor='nw')
        lbl = ttk.Label(label_frame, text=text, style='Context.TLabel', wraplength=wraplength)
        lbl.grid(row=0, column=0, sticky='w')

        label_frame.update_idletasks()

        # Привязываем прокрутку по колёсику ко всей области конкретного Canvas
        canvas.bind("<Enter>", lambda event, canvas=canvas: canvas.bind_all(
            "<MouseWheel>", lambda event, canvas=canvas: widget.parent.on_mouse_wheel(event, canvas)))
        canvas.bind("<Leave>", lambda event, canvas=canvas: canvas.unbind_all("<MouseWheel>"))

        canvas.config(scrollregion=canvas.bbox("all"))                   # Добавляем прокрутку scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        return container_canvas

    def put_btns_navi_container(self, widget: tk.Frame, parent_container: tk.Frame) -> tk.Frame:
        """
        Контейнер с кастомными кнопками навигации ВПЕРЁД-НАЗАД. Функции-обработчики уже заданы.
        После вызова функции необходимо будет разместить возвращённый виджет.

        :param widget: окно приложения, в котором вызывается функция, наследник tk.Tk
        :param parent_container: контейнер окна, в котором будет размещён контейнер с навигацией
        :return: tk.Frame созданный настроенный btns_navi_cont с содержимым
        """

        # Контейнер
        btns_navi_cont = tk.Frame(parent_container, bg=widget.bg)

        # Кнопка НАЗАД
        image = Image.open(settings.ICON_REWIND_BACK['path'])
        image = image.resize((15, 15))
        icon = ImageTk.PhotoImage(image)
        btn_previous_word = ttk.Button(btns_navi_cont, text='Назад', image=icon, compound=tk.LEFT,
                                           style='h2.TButton',
                                           command=widget.handler_icon_previous_word, padding=(-7, 2, -7, 2))
        btn_previous_word.image = icon
        btn_previous_word.grid(row=0, column=0, sticky='e')

        # Кнопка ДАЛЕЕ
        image = Image.open(settings.ICON_NEXT['path'])
        image = image.resize((15, 15))
        icon = ImageTk.PhotoImage(image)
        btn_next_word = ttk.Button(btns_navi_cont, text='Далее', image=icon, compound=tk.RIGHT, style='h2.TButton',
                                       command=widget.handler_next_button, padding=(-7, 2, -7, 2))
        btn_next_word.image = icon
        btn_next_word.grid(row=0, column=1, sticky='e')

        return btns_navi_cont

    def put_icon_say_aloud(self, widget: tk.Frame, container: tk.Frame) -> None:
        """
        Сбор иконки с произнесением.
        У widget должен существовать метод .handler_say_word() - или необходимо переопределить command= через
        .config() после сборки; + атрибут .bg для задания фона.

        :param widget: окно, в котором вызывается сборка (EnRuWindow, EnRuAudioWindow ...)
        :param container: контейнер, в котором непосредственно происходит сборка иконки
        :return: Функция ничего не возвращает, но из родителя после вызова функции становится доступна
                иконка icon_say_aloud
        """
        image = Image.open(settings.ICON_SOUND['path'])
        image = image.resize((20, 20))
        icon = ImageTk.PhotoImage(image)
        self.icon_say_aloud = tk.Button(container, image=icon, bd=0, background=widget.bg,
                                 command=widget.handler_say_word)
        self.icon_say_aloud.image = icon

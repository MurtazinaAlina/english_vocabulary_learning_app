"""
Окно для работы с данными.
Доступно создание, редактирование, удаление тем/листов Excel.
Доступно отображение записей: всех записей выбранного листа Excel/темы, либо всех записей в базе - для БД.
Данные доступны к поиску, созданию, просмотру, редактированию, удалению.
"""
import functools
import tkinter as tk
from tkinter import ttk, messagebox as mbox
from PIL import Image, ImageTk

from Utils import auxiliary_tools as tls
import settings
import styles
from Utils.custom_widgets.hover_btn_text import HoverButton
from Utils.paginator import Paginator
from Utils.custom_widgets.tooltips import TooltipCursorOnHover, TooltipHiding


class DataWindow(ttk.Frame):
    """ Окно для работы с данными."""

    def __init__(self, parent):             # При инициализации передаётся app Tk()
        super().__init__(parent)
        self.parent = parent                # Имя-связка для обращения к родителю за его атрибутами и методами
        self.bg = styles.STYLE_COLORS[self.parent.current_color_style]['background']

        self.current_say = None             # Последнее озвучивавшееся слово в контексте.
        self.index_context = 0              # Индекс для следующего озвучиваемого примера контекста

        self.put_widgets()

    def put_widgets(self) -> None:
        """ Сборка основного окна страницы. """

        if not self.parent.wb and not self.parent.db.engine:
            mbox.showerror('Ошибка', 'Не выбран файл')                          # Если не подключен ни один вид базы

        header_container = ttk.Frame(self)
        header_container.pack(anchor='center')

        header_label = ttk.Label(header_container, text=settings.APP_WINDOWS['data']['label'], style='HeadLbl.TLabel')
        header_label.pack(anchor='center')

        self.wrapper_choose_frame = tk.Frame(self)          # Верхний контейнер с выбором листа и иконками управления
        self.wrapper_choose_frame.pack(anchor='w')

        self.put_container_block_above_table(self.wrapper_choose_frame)         # Сборка верхнего контейнера

        self.table_container = tk.Frame(self, bg=self.bg)                       # Сборка контейнера с данными
        self.table_container.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.put_container_with_table()

        self.put_bottom_container()                                             # Сборка контейнера с пагинацией

    def put_icon_add_sheet(self) -> None:
        """ Иконка добавление нового листа/темы. """

        image = Image.open(settings.ICON_ADD_SHEET['path'])
        image = image.resize((20, 20))
        icon = ImageTk.PhotoImage(image)
        self.btn_add_sheet_icon = tk.Button(self.container_manage_sheet_icons, image=icon,
                                            command=self.parent.popup.add_new_sheet_popup, bd=0)
        self.btn_add_sheet_icon.image = icon
        self.btn_add_sheet_icon.config(bg=styles.STYLE_COLORS[self.parent.current_color_style]['background'])
        text = 'Создать новую тему' if self.parent.db.engine else 'Создать новый лист'
        TooltipCursorOnHover(self.btn_add_sheet_icon, text=text, hand_cursor=True, x=435, y=220)

    def put_icon_delete_sheet(self) -> None:
        """ Иконка удаление листа/темы. """

        image = Image.open(settings.ICON_DELETE_SHEET['path'])
        image = image.resize((20, 20))
        icon = ImageTk.PhotoImage(image)
        self.btn_delete_sheet_icon = tk.Button(self.container_manage_sheet_icons, image=icon,
                                               command=self.parent.popup.on_click_DELETESHEET,
                                               bd=0)
        self.btn_delete_sheet_icon.image = icon
        self.btn_delete_sheet_icon.config(bg=styles.STYLE_COLORS[self.parent.current_color_style]['background'])
        text = 'Удалить тему' if self.parent.db.engine else 'Удалить лист'
        TooltipCursorOnHover(self.btn_delete_sheet_icon, text=text, hand_cursor=True, x=470, y=220)

    def put_icon_edit_sheet(self) -> None:
        """ Иконка редактирование листа/темы. """

        image = Image.open(settings.ICON_EDIT_SHEET['path'])
        image = image.resize((20, 20))
        icon = ImageTk.PhotoImage(image)
        self.btn_edit_sheet_icon = tk.Button(self.container_manage_sheet_icons, image=icon,
                                             command=self.parent.popup.edit_sheet_popup, bd=0)
        self.btn_edit_sheet_icon.image = icon
        self.btn_edit_sheet_icon.config(bg=styles.STYLE_COLORS[self.parent.current_color_style]['background'])
        text = 'Редактировать тему' if self.parent.db.engine else 'Редактировать лист'
        TooltipCursorOnHover(self.btn_edit_sheet_icon, text=text, hand_cursor=True, x=435, y=220)

    def put_icon_add_data(self) -> None:
        """ Иконка с добавлением записи - новое слово/фраза. """

        image = Image.open(settings.ICON_ADD_DATA['path'])
        image = image.resize((40, 40))
        icon = ImageTk.PhotoImage(image)
        self.btn_add_data_icon = tk.Button(self.container_choose_sheet, image=icon,
                                           command=self.parent.popup.add_row, bd=0)
        self.btn_add_data_icon.image = icon
        self.btn_add_data_icon.config(bg=styles.STYLE_COLORS[self.parent.current_color_style]['background'])
        TooltipCursorOnHover(self.btn_add_data_icon, text='Добавить запись', x=1070, y=220, hand_cursor=True)

    def put_container_block_above_table(self, wrapper_choose_frame) -> None:
        """ Сборка верхнего контейнера над таблицей, с выбором листа, иконками управления, поиском. """

        self.container_choose_sheet = tk.Frame(wrapper_choose_frame, bg=self.bg)
        self.container_choose_sheet.grid(row=0, column=0, sticky='w')

        # Собираем контейнер с выбором листа из родителя - кроме reverso и сортировки, т.к. нестандартный рефреш и tltip
        container_label_choose_sheet = self.parent.put_container_choose_sheet(
            self, self.container_choose_sheet, tooltip_x_y=None, with_sorting=False, with_reverso=False)
        container_label_choose_sheet.grid(row=0, column=0)

        # Сборка кнопки сортировки из родителя
        self.parent.put_icon_sort_sheets(container=container_label_choose_sheet, widget=self,
                                         func='put_container_block_above_table', in_frame=wrapper_choose_frame)
        self.parent.btn_sort_sheets.grid(row=0, column=3, sticky='w')
        TooltipCursorOnHover(self.parent.btn_sort_sheets, x=430, y=215,
                             text=f'Изменить сортировку на:\n{settings.SORTING_SHEETS[self.parent.sorted]}')

        # Сборка иконок управления, поисковика и добавления записи
        self.put_container_manage_sheet_icons()                     # Сборка контейнера с иконками управления листа

        if self.parent.choosen_excel_list or self.parent.db.engine:
            self.put_icon_add_data()                                # Сборка иконки добавления данных
            self.btn_add_data_icon.grid(row=0, column=7, padx=5)
            self.put_container_search_field()                       # Сборка контейнера с поиском в данных
            self.search_frame.grid(column=6, row=0, sticky='nswe')

    def put_container_manage_sheet_icons(self) -> None:
        """ Сборка контейнера с иконками управления листом/темой. """

        if not self.parent.wb and not self.parent.db.engine:
            return

        self.container_manage_sheet_icons = tk.Frame(self.container_choose_sheet, background=self.bg)
        self.container_manage_sheet_icons.grid(row=0, column=5, padx=35)

        # Иконку управления отображаются при выбранном листе Excel или подключении к БД
        if self.parent.choosen_excel_list or self.parent.db.engine:
            self.put_icon_delete_sheet()
            self.put_icon_edit_sheet()
            self.put_icon_add_sheet()

            self.btn_edit_sheet_icon.grid(row=0, column=0, sticky='w')
            self.btn_delete_sheet_icon.grid(row=0, column=1, sticky='w', padx=5)
            self.btn_add_sheet_icon.grid(row=0, column=2, sticky='w')

            # Активны только при выбранном листе/теме
            if not (self.parent.choosen_excel_list or self.parent.choosen_db_theme):
                self.btn_edit_sheet_icon.config(state='disabled')
                self.btn_delete_sheet_icon.config(state='disabled')

        else:
            self.put_icon_add_sheet()
            self.btn_add_sheet_icon.grid(row=0, column=0, sticky='w')

    def put_container_search_field(self) -> None:
        """ Сборка контейнера с поиском данных. """

        self.container_choose_sheet.grid_columnconfigure(6, minsize=500)    # Резервирование пространства в 6 col
        self.search_frame = tk.Frame(self.container_choose_sheet, bg=self.bg)

        label = ttk.Label(self.search_frame, text='Поиск', style='BlItGrey.TLabel', padding=(90, 20, 5, 20))
        label.pack(side='left')

        self.search_word_form = ttk.Entry(self.search_frame, width=40)      # Ввод данных для поиска
        if self.parent.search_key:                                          # Автозаполнение при наличии key поиска
            self.search_word_form.insert(0, self.parent.search_key)
        self.search_word_form.pack(side='left')

        image = Image.open(settings.ICON_SEARCH_IN_SHEETS['path'])          # Кнопка ПОИСК
        image = image.resize((14, 14))
        icon = ImageTk.PhotoImage(image)
        self.btn_search_word_in_data = ttk.Button(self.search_frame, command=self.handler_search_field, image=icon)
        self.btn_search_word_in_data.image = icon
        self.btn_search_word_in_data.pack(side='left')
        TooltipCursorOnHover(self.btn_search_word_in_data, text='Нажмите, чтобы начать поиск', x=880, y=220)

    def put_container_with_table(self) -> None:
        """ Заполнение контейнера с таблицей. Получение данных + отрисовка. """

        # Получаем срез данных для вывода на текущую страницу таблицы
        self.pagi = Paginator(widget=self, array=self.get_table_data(), current_page=self.parent.data_pagi_page)
        self.result_data = self.pagi.get_data_slice()

        # Отрисовка строки-таблицы с заголовками
        header_bg = {'background': styles.STYLE_COLORS[self.parent.current_color_style]['cnvs_headers_bg']}
        canvas1 = tk.Canvas(self.table_container, height=25, **header_bg)
        canvas1.pack(side=tk.TOP, fill=tk.BOTH)
        header_frame_cnvs = ttk.Frame(canvas1)
        canvas1.create_window((0, 0), window=header_frame_cnvs, anchor='nw')
        header_y = 0
        header_x = 0
        columns = list(settings.COLUMN_WIDTH.items())           # Чтобы легко обратиться к последнему элементу
        for idx, (k, v) in enumerate(columns):
            canvas1.create_text(header_x + 10, header_y + 5, text=k, anchor='nw', width=v - 10,
                                **styles.CANVAS_HEADERS)
            if idx != len(columns) - 1:                         # Правую границу НЕ отрисовываем (т.к. ниже прокрутка)
                canvas1.create_rectangle(header_x + 1, header_y, header_x + v + 1, 30,
                                         **styles.CANVAS_TABLE_BORDER_DASH_GRAY)
            header_x += v

        # Рисуем таблицу с данными
        canvas = tk.Canvas(self.table_container, background='white')        # Создаём объект canvas
        canvas.pack(expand=tk.YES, fill=tk.BOTH, side=tk.LEFT)

        table_frame = ttk.Frame(canvas)                   # Создаем div внутри Canvas, который будет содержать данные
        canvas.create_window((0, 0), window=table_frame, anchor='nw')
        coord_y = 0
        all_rows_data = []                                # Список для хранения всех строк данных + info о флаге выбора

        for idx, row in enumerate(self.result_data):
            x1 = 0

            if self.parent.data_type == 'Excel':
                tls.context_formatting(row, indent='\n')        # Форматируем Excel для вывода - заменяем пробелы на \n

            row_height = tls.calculate_row_high_for_cnvs(row)   # Расчет высоты строки в зав-ти от длины контента
            row_data = {'rect_ids': [],          # Словарь для хранения данных строки, id прямоугольников + флаг выбора
                        'is_selected': False}

            # Создаём рамку и текст для каждого элемента строки
            for col_idx, (header, cell) in enumerate(zip(settings.COLUMN_WIDTH.keys(), row)):

                if col_idx == 5:    # Служебный - инфо о теме, для вывода в popup, не отображаем
                    continue

                col_width = settings.COLUMN_WIDTH[header]
                x2 = x1 + col_width
                column_width = settings.COLUMN_WIDTH[header] - 10   # Ширина столбца для расчета переноса текста
                rect_id = canvas.create_rectangle(x1, coord_y, x2, coord_y + row_height,
                                                  **styles.CANVAS_TABLE_BORDER_DASH_GRAY)

                # Для столбцов idx 1 и 4 делаем иконки озвучки
                if col_idx == 1 or (col_idx == 4 and cell not in ('\n', '', ' ')):     # Кроме пустых

                    if col_idx == 1:                                    # Определяем обработчик
                        command = functools.partial(self.parent.engine_speech.say_out, data=cell)
                    elif col_idx == 4:
                        command = functools.partial(self._save_tuple_from_speech, data_list=row)

                    image = Image.open(settings.ICON_SOUND['path'])     # Иконка озвучки
                    image = image.resize((20, 20))
                    icon = ImageTk.PhotoImage(image)
                    icon_say = tk.Button(canvas, bd=0, image=icon, background='white', command=command)
                    icon_say.image = icon
                    canvas.create_window(x1 + 15, coord_y + 20, window=icon_say)
                    x1 += 25
                    column_width -= 25

                    # Привязываем события к иконкам озвучки
                    icon_say.bind("<Enter>", functools.partial(self.event_on_hover_with_cursor_change,
                                                               row_data=row_data, canvas=canvas,
                                                               all_rows_data=all_rows_data, widget=icon_say,
                                                               col_idx=col_idx))
                    icon_say.bind("<Leave>", functools.partial(self.event_on_leave_with_cursor_change,
                                                               row_data=row_data, canvas=canvas,
                                                               all_rows_data=all_rows_data, widget=icon_say))

                text_id = canvas.create_text(x1 + 5, coord_y + 10, anchor="nw", text=cell,
                                             width=column_width,
                                             **styles.CANVAS_TABLE_TEXT)
                x1 = x2                                             # Обновляем x1 для следующей ячейки
                row_data['rect_ids'].append(rect_id)                # Добавляем id прямоугольника в row_data
                all_rows_data.append(row_data)                      # Добавляем в итоговый список словарь строки

                # Привязываем реагирование на события для отрисованных элементов - текста и пространства в рамке
                self.events_set_main_table_events(rect_id, canvas, all_rows_data, row_data, row)
                self.events_set_main_table_events(text_id, canvas, all_rows_data, row_data, row)

            # Добавляем кнопку "Редактировать" справа от данных в строке
            edit_btn = ttk.Button(canvas, text='Править', command=lambda row=row: self.parent.popup.edit_row_popup(row),
                                  style='Edit.TButton')
            canvas.create_window(x1 + 45, coord_y + 20, window=edit_btn)
            rect_id = canvas.create_rectangle(x1, coord_y, x1 + 100, coord_y + row_height,
                                              **styles.CANVAS_TABLE_BORDER_DASH_GRAY)
            coord_y += row_height
            row_data['rect_ids'].append(rect_id)            # Добавляем id ячейки в инфо о строке

            # Привязываем события для нового rect_id - т.к. он вне цикла, и к кнопкам
            self.events_set_main_table_events(rect_id, canvas, all_rows_data, row_data, row)
            edit_btn.bind("<Enter>", functools.partial(self.event_on_hover, row_data=row_data, canvas=canvas,
                                                       all_rows_data=all_rows_data))
            edit_btn.bind("<Leave>", functools.partial(self.event_off_hover, row_data=row_data, canvas=canvas,
                                                       all_rows_data=all_rows_data))

        # Добавляем вертикальный скроллбар для Canvas + прокрутку по всей области canvas
        canvas.bind_all("<MouseWheel>", lambda event, canvas=canvas: self.parent.on_mouse_wheel(event, canvas))
        scroll_panel = ttk.Scrollbar(canvas, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scroll_panel.set)
        scroll_panel.pack(side=tk.RIGHT, fill=tk.Y)
        table_frame.update_idletasks()                                  # Обновляем после всех операций рисования
        canvas.config(scrollregion=canvas.bbox("all"))                  # Устанавливаем область прокрутки

    def put_bottom_container(self) -> None:
        """ Сборка контейнера с пагинацией. """

        # Определяем цвета подсветки кнопок пагинации при select и hover on
        select_colour = styles.STYLE_COLORS[self.parent.current_color_style]['menu_btn_color_main']
        hover_colour = styles.STYLE_COLORS[self.parent.current_color_style]['pagi_on_hover_bg']

        # Настройки стиля для HoverButton при создании
        style_hoverbtn = {
            'bg': self.bg,
            'select_colour': select_colour,
            'hover_colour': hover_colour
        }

        # Общий контейнер с пагинацией и переходом на страницу
        bottom_container = tk.Frame(self, bg=self.bg, pady=5)
        bottom_container.grid_columnconfigure(0, minsize=1100)
        bottom_container.grid_columnconfigure(1, minsize=300)
        bottom_container.pack(anchor='w', fill='x')

        # Внутренний контейнер с пагинацией
        container_pagi = tk.Frame(bottom_container, bg=self.bg, pady=5)
        container_pagi.grid(row=0, column=0, sticky='e', padx=320)

        # Определяем номера 3х отображаемых номерных страниц пагинации
        pg1, pg2, pg3 = self.pagi.get_pages_1_2_3_numbers()

        # Настраиваем навигацию по страницам
        if self.pagi.has_previous():

            # Страница 1 - переход
            self.btn_first_page = HoverButton(container_pagi, text='<<', **style_hoverbtn,
                                              command=self.pagi.go_to_first_page)
            self.btn_first_page.grid(row=0, column=0, sticky='we', padx=(100, 0))

            # Предыдущая страница - переход
            self.btn_previous_page = HoverButton(container_pagi, text='<', **style_hoverbtn,
                                                 command=self.pagi.go_to_previous_page)
            self.btn_previous_page.grid(row=0, column=1, sticky='we', padx=(5, 0))

            # Лейбл '...' если есть неотображенные страницы
            if pg1 > 1:
                lbl = tk.Label(container_pagi, bg=self.bg, text='...')
                lbl.grid(row=0, column=2, sticky='we', padx=(5, 0), pady=(4, 10))

        # Номерная страница 1
        self.pg_1 = HoverButton(container_pagi, text=str(pg1), crnt=self.parent.data_pagi_page, **style_hoverbtn,
                                command=lambda: self.pagi.go_to_page_number(pg1))
        self.pg_1.grid(row=0, column=3, sticky='we', padx=(5, 0))

        # Номерная страница 2
        if self.pagi.pages_total > 1:
            self.pg_2 = HoverButton(container_pagi, text=str(pg2), crnt=self.parent.data_pagi_page, **style_hoverbtn,
                                    command=lambda: self.pagi.go_to_page_number(pg2))
            self.pg_2.grid(row=0, column=4, sticky='we', padx=(5, 0))

        # Номерная страница 3
        if self.pagi.pages_total > 2:
            self.pg_3 = HoverButton(container_pagi, text=str(pg3), crnt=self.parent.data_pagi_page, **style_hoverbtn,
                                    command=lambda: self.pagi.go_to_page_number(pg3))
            self.pg_3.grid(row=0, column=5, sticky='we', padx=(5, 0))

            # Лейбл '...' если есть неотображенные страницы
            if pg3 < self.pagi.pages_total:
                lbl = tk.Label(container_pagi, bg=self.bg, text='...')
                lbl.grid(row=0, column=9, sticky='we', padx=(5, 0), pady=(4, 10))

        # Следующая страница - переход
        if self.pagi.has_next():
            self.btn_next_page = HoverButton(container_pagi, text='>', **style_hoverbtn,
                                             command=self.pagi.go_to_next_page)
            self.btn_next_page.grid(row=0, column=10, sticky='we', padx=(5, 0))

            # Последняя страница - переход
            self.btn_last_page = HoverButton(container_pagi, text='>>', **style_hoverbtn,
                                             command=self.pagi.go_to_last_page)
            self.btn_last_page.grid(row=0, column=11, sticky='we', padx=(5, 0))

        # Контейнер с переходом на конкретную страницу
        if self.pagi.pages_total < 3:
            return                                                          # Только при условии, что страниц более 3х

        container_go_to_page = tk.Frame(bottom_container, bg=self.bg)       # Лейбл
        container_go_to_page.grid(row=0, column=1, sticky='e')
        lbl = tk.Label(container_go_to_page, bg=self.bg, text='Перейти на страницу: ')
        lbl.grid(row=0, column=0, sticky='e')

        # Форма ввода номера страницы
        f_to_page = tk.Entry(container_go_to_page, bg='white', width=3, justify=tk.RIGHT, validate='key',
                             validatecommand=(self.register(self._validate_form_pagi_to), '%P'))
        f_to_page.grid(row=0, column=1, sticky='e')

        # Кнопка перехода на введённую страницу
        self.btn_go_to_page = HoverButton(container_go_to_page, text='>', **style_hoverbtn,
                                          command=lambda: self.pagi.go_to_page_number(int(f_to_page.get())))
        self.btn_go_to_page.grid(row=0, column=2, sticky='e', padx=(3, 20))

    def handler_search_field(self) -> None:
        """ Обработчик поиска. Сохраняет отфильтрованный по введённому в поле ключу список строк
        (по полю слово/фраза) + обновляет окно с таблицей. """

        # Фиксируем ключ поиска и массив отфильтрованных данных
        self.parent.search_key = self.search_word_form.get().lower()
        self.parent.search_data = list(filter(lambda x: self.parent.search_key in x[1].lower(), self.data))

        # Сбрасываем текущую страницу пагинации
        self.parent.data_pagi_page = 1
        self.pagi.current_page_number = 1
        self.parent.refresh()
        return

    def handler_choose_sheet(self, cmbbx_list: list[str]) -> None:
        """ Обработчик кнопки выбора листа.
        Вызывает родительский метод выбора листа из списка combobox + обновляет пагинацию. """

        self.parent.handler_select_sheet(self.cmbbx_choose_sheet.get(), cmbbx_list)

        # Сбрасываем текущую страницу пагинации и поиск
        self.parent.data_pagi_page = 1
        self.pagi.current_page_number = 1
        self.parent.search_data = None
        self.parent.search_key = None
        self.parent.refresh()

    def get_table_data(self) -> list:
        """ Получение списка с данными для отображения. """

        if not self.parent.wb and not self.parent.db.engine:                                # Заглушка
            return []

        # Запись всех данных листа для смены поиска
        if self.parent.data_type == 'Excel':
            if not self.parent.choosen_excel_list:                                          # Заглушка
                return []
            self.data = self.parent.excel_get_all_data_from_sheet(self.parent.choosen_excel_list)

        elif self.parent.data_type == 'База':

            # Если None - выводит ВСЕ записи без фильтра по теме
            self.data = self.parent.db.get_all_words_from_subject(self.parent.choosen_db_theme)

        # Если задействован поиск - возвращает отфильтрованный массив
        if self.parent.search_key:
            return self.parent.search_data
        else:
            return self.data

    def _reset_selection_hover_events(self, canvas: tk.Canvas, all_rows_data: list[dict]) -> None:
        """
        Сбрасываем подсветку для всех строк.

        :param canvas: объект Canvas
        :param all_rows_data: список со словарями, содержащими информацию о строке: id объектов строки и признак выбора
        """
        for i in all_rows_data:
            if i['is_selected'] is True:
                for rect_id in i['rect_ids']:
                    canvas.itemconfig(rect_id, fill="white")
                i['is_selected'] = False

    def event_on_hover(self, event, row_data: dict, canvas: tk.Canvas, all_rows_data: list[dict]) -> None:
        """
        Подсветка строки при наведении курсора.

        :param row_data: словарь с информацией о текущей строке
        :param canvas: объект Canvas
        :param all_rows_data: список со словарями, содержащими информацию о строке: id объектов строки и признак выбора
        """
        if not row_data['is_selected']:                             # Подсвечиваем только если строка не выбрана
            for rect_id in row_data['rect_ids']:
                canvas.itemconfig(rect_id, fill=styles.EVENT_HOVER_CURSOR_TABLE)

    def event_off_hover(self, event, row_data: dict, canvas: tk.Canvas, all_rows_data: list[dict]) -> None:
        """
        Убираем подсветку при отведении курсора.

        :param row_data: словарь с информацией о текущей строке
        :param canvas: объект Canvas
        :param all_rows_data: список со словарями, содержащими информацию о строке: id объектов строки и признак выбора
        """
        if not row_data['is_selected']:                             # Подсвечиваем только если строка не выбрана
            for rect_id in row_data['rect_ids']:
                canvas.itemconfig(rect_id, fill=styles.EVENT_HOVER_OFF_CURSOR_TABLE)

    def event_on_single_click(self, event, row_data: dict, canvas: tk.Canvas, all_rows_data: list[dict]) -> None:
        """
        Обработчик события одиночный клик.

        :param row_data: словарь с информацией о текущей строке
        :param canvas: объект Canvas
        :param all_rows_data: список со словарями, содержащими информацию о строке: id объектов строки и признак выбора
        """
        self._reset_selection_hover_events(canvas, all_rows_data)   # Сбрасываем подсветку для всех строк
        for rect_id in row_data['rect_ids']:                        # Подсвечиваем новую выбранную строку
            canvas.itemconfig(rect_id, fill=styles.EVENT_SELECTED_CURSOR_TABLE)
        row_data['is_selected'] = True                              # Устанавливаем флаг, что эта строка выбрана

    def event_on_double_click(self, event, row_data: dict, canvas: tk.Canvas, all_rows_data: list[dict],
                              row: list[str]) -> None:
        """
        Обработчик события двойной клик.

        :param row_data: словарь с информацией о текущей строке
        :param canvas: объект Canvas
        :param all_rows_data: список со словарями, содержащими информацию о строке: id объектов строки и признак выбора
        :param row: список, содержащий информацию, отображаемую в строке таблицы
        :return: None
        """
        self._reset_selection_hover_events(canvas, all_rows_data)   # Сбрасываем подсветку для всех строк
        for rect_id in row_data['rect_ids']:
            canvas.itemconfig(rect_id, fill=styles.EVENT_SELECTED_CURSOR_TABLE)   # Подсвечиваем новую выбранную строку
        row_data['is_selected'] = True                              # Устанавливаем флаг, что эта строка выбрана
        self.parent.popup.edit_row_popup(row)                       # Вызов редактирования

    def event_on_right_button_click(self, event, row_data: dict, canvas: tk.Canvas, all_rows_data: list[dict],
                              row: list[int | str]) -> None:
        """
        Обработчик события клик правой кнопкой - вызов контекстного меню.

        :param row_data: словарь с информацией о текущей строке
        :param canvas: объект Canvas
        :param all_rows_data: список со словарями, содержащими информацию о строке: id объектов строки и признак выбора
        :param row: список, содержащий информацию, отображаемую в строке таблицы
        :return: None
        """
        self._reset_selection_hover_events(canvas, all_rows_data)   # Сбрасываем подсветку для всех строк
        for rect_id in row_data['rect_ids']:
            canvas.itemconfig(rect_id, fill=styles.EVENT_SELECTED_CURSOR_TABLE)   # Подсвечиваем новую выбранную строку
        row_data['is_selected'] = True                              # Устанавливаем флаг, что эта строка выбрана

        context_menu = tk.Menu(self, tearoff=0)                     # Просто создаём объект меню
                                                                    # навешиваем ему список команд с обработчиками
        context_menu.add_command(label='Открыть запись для редактирования',
                                 command=lambda row=row: self.parent.popup.edit_row_popup(row))
        context_menu.add_command(label='Удалить запись', command=lambda row=row: self._delete_row_in_context_menu(row))
        context_menu.add_separator()
        context_menu.add_command(label='Добавить новую запись в таблицу', command=self.parent.popup.add_row)
                                                                    # Отображаем меню по координатам (х, у)
        context_menu.post(event.x + canvas.winfo_rootx(), event.y + canvas.winfo_rooty())

    def _delete_row_in_context_menu(self, row: list) -> None:
        """
        Удаление строки из листа Excel по данным из строки таблицы + обновление таблицы Canvas.

        :param row: список с данными для отображения строки в таблице,  row:
                    [4, 'word', 'transcription', 'translate', 'context']
        """

        # Подтверждение удаления
        answer = mbox.askyesno('Подтвердите удаление',
                               'Вы действительно хотите удалить запись?\nОтменить действие бедет невозможно')
        if answer == 'Нет' or answer is False:
            return

        # Удаление из базы
        if self.parent.data_type == 'Excel':
            if self.parent.excel_delete_row_without_form(row, self):
                mbox.showinfo('', 'Запись удалена')
        elif self.parent.data_type == 'База':
            if self.parent.db.delete_word(row[0]):
                mbox.showinfo('', 'Запись удалена')

        self.parent.refresh(object=self, container=self.table_container, build_function='put_container_with_table')

    def events_set_main_table_events(self, obj_id: int, canvas: tk.Canvas, all_rows_data: list[dict], row_data: dict,
                                     row: list[str]) -> None:
        """
        Привязка основных событий таблицы к объекту canvas: Enter, Leave, Button-1, Button-3, Double-1.

        :param obj_id: id созданного объекта Canvas
        :param canvas: объект Canvas
        :param all_rows_data: список со словарями, содержащими информацию о строке: id объектов строки и признак выбора
        :param row_data: словарь с информацией о текущей строке
        :param row: список, содержащий информацию, отображаемую в строке таблицы
        :return: None
        """
        canvas.tag_bind(obj_id, "<Enter>", functools.partial(
            self.event_on_hover, row_data=row_data, canvas=canvas, all_rows_data=all_rows_data))
        canvas.tag_bind(obj_id, "<Leave>", functools.partial(
            self.event_off_hover, row_data=row_data, canvas=canvas, all_rows_data=all_rows_data))
        canvas.tag_bind(obj_id, "<Button-1>", functools.partial(
            self.event_on_single_click, row_data=row_data, canvas=canvas, all_rows_data=all_rows_data))
        canvas.tag_bind(obj_id, "<Double-1>", functools.partial(
            self.event_on_double_click, row_data=row_data, canvas=canvas, all_rows_data=all_rows_data, row=row))
        canvas.tag_bind(obj_id, "<Button-3>", functools.partial(
            self.event_on_right_button_click, row_data=row_data, canvas=canvas, all_rows_data=all_rows_data, row=row))

    def event_on_hover_with_cursor_change(self, event, widget, row_data: dict, canvas: tk.Canvas,
                                          all_rows_data: list[dict], col_idx: int) -> None:
        """
        Расширение к обработчику события при наведении: дополнено изменение курсора на hand + подсказка.

        :param widget: виджет tkinter, для которого будет меняться курсор (Button и т.д.)
        :param row_data: словарь с информацией о текущей строке
        :param canvas: объект Canvas
        :param all_rows_data: список со словарями, содержащими информацию о строке: id объектов строки и признак выбора
        :param col_idx: int индекс столбца, для которого настраивается событие
        """
        widget.config(cursor="hand2")
        text = 'Произнести' if col_idx == 1 else 'Произнести пример.\nЧтобы озвучить следующий,\n нажмите повторно'
        TooltipHiding(widget, text, event, 3000)
        self.event_on_hover(event, row_data=row_data, canvas=canvas, all_rows_data=all_rows_data)

    def event_on_leave_with_cursor_change(self, event, widget, row_data: dict, canvas: tk.Canvas,
                                          all_rows_data: list[dict]) -> None:
        """
        Расширение к обработчику события при отведении: дополнено изменение курсора на стандартный.

        :param widget: виджет tkinter, для которого будет меняться курсор (Button и т.д.)
        :param row_data: словарь с информацией о текущей строке
        :param canvas: объект Canvas
        :param all_rows_data: список со словарями, содержащими информацию о строке: id объектов строки и признак выбора

        """
        widget.config(cursor="arrow")
        self.event_off_hover(event, row_data=row_data, canvas=canvas, all_rows_data=all_rows_data)

    def _save_tuple_from_speech(self, data_list: list[int | str]) -> None:
        """
        Расширение к обработчику частичной озвучки: дополнена запись в атрибуты класса:
        self.current_say, self.index_context

        :param data_list: список с данными строки в формате: [4, 'word', 'transcription', 'translate', 'context']
        """
        self.current_say, self.index_context = self.parent.engine_speech.say_out_partial(
            data_list=data_list, current_say=self.current_say, index_context=self.index_context)

    def _validate_form_pagi_to(self, input) -> bool:
        """ Валидация формы ввода перехода к странице № в пагинации. """

        try:
            if input == '':
                return True

            value = int(input)
            if value <= self.pagi.pages_total:
                return True
            return False

        except ValueError:
            self.bell()
            return False

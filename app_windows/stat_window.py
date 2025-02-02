"""
Окно приложения с отображением статистики отчётов пройденных тестирований.
"""
import datetime
import tkinter as tk
from tkinter import ttk, messagebox as mbox
from tkcalendar import DateEntry
from PIL import Image, ImageTk

import settings
import styles
from Utils.custom_widgets.tooltips import TooltipCursorOnHover


class StatWindow(ttk.Frame):
    """ Окно для отображения статистики """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.bg = styles.STYLE_COLORS[self.parent.current_color_style]['background']
        self.current_hovered = None

        self.put_widgets()

    def put_widgets(self) -> None:
        """ Сборка основного окна страницы """

        header_label = ttk.Label(self, text=settings.APP_WINDOWS['stat']['label'], style='HeadLbl.TLabel')
        header_label.pack(anchor='center')
        self.grid_columnconfigure(0, weight=1)

        # Сборка контейнера над таблицей с фильтрами
        self.container_above_table = tk.Frame(self, height=35, bg=self.bg)
        self.container_above_table.pack(fill='both')
        self.put_container_above_table()

        # Сборка контейнера с таблицей
        self.container_with_table = tk.Frame(self, background='white')
        self.container_with_table.pack(expand=tk.YES, fill=tk.BOTH, padx=(5, 5), pady=(0, 5))
        self.container_with_table.grid_columnconfigure(0, weight=1)
        self.container_with_table.grid_rowconfigure(0, weight=1)

        if not self.parent.wb and not self.parent.db.engine:                        # Обработка отсутствия базы
            mbox.showerror('Ошибка', 'Не выбран файл')
            return

        # Заполнение таблицы
        self.get_data_for_table_from_db()                                           # Формирование данных
        self.put_table_with_stat()                                                  # Заполнение

    def put_container_above_table(self) -> None:
        """ Сборка контейнера над таблицей с фильтрами """

        # Радио с выбором всех записей или установкой фильтра по дате
        self.radio_filter_data_var = tk.StringVar()
        self.radio_filter_data_var.set('all')

        self.rbtn_all_data = ttk.Radiobutton(self.container_above_table, text='Все записи',
                                             variable=self.radio_filter_data_var, value='all')
        self.rbtn_all_data.pack(side='left', anchor='w', padx=(10, 0), pady=10)

        self.rbtn_filter_data = ttk.Radiobutton(self.container_above_table, text='только записи за период c',
                                                variable=self.radio_filter_data_var, value='filter')
        self.rbtn_filter_data.pack(side='left', anchor='w', padx=5, pady=0)

        # Виджеты выбора дат для фильтрации
        self.date_from = DateEntry(self.container_above_table, **styles.DATE_ENTRY_WIDGET)
        self.date_from.pack(side='left', anchor='w', padx=0, pady=0)

        self.label = tk.Label(self.container_above_table, text='по', background=self.bg)
        self.label.pack(side='left', anchor='w', padx=2, pady=0)

        self.date_before = DateEntry(self.container_above_table, **styles.DATE_ENTRY_WIDGET)
        self.date_before.pack(side='left', anchor='w', padx=0, pady=0)

        # Чек-бокс для отметки фильтра по типу тестирования
        self.filter_type_var = tk.BooleanVar()
        self.chbx_filter_test_type = ttk.Checkbutton(self.container_above_table, text='Только выбранный тип тестов',
                                                     variable=self.filter_type_var, padding=(30, 0, 5, 0))
        self.chbx_filter_test_type.pack(side='left', anchor='w')

        # Комбобокс с выбором типа тестирования
        all_test_types = settings.TEST_TYPES[:]                         # Список названий всех типов тестов
        all_test_types.insert(0, '-')

        self.cmbbx_choose_test_type = ttk.Combobox(self.container_above_table, width=15, values=all_test_types)
        self.cmbbx_choose_test_type.pack(side='left', anchor='w')

        # Чек-бокс для отметки фильтра по названию листа
        self.filter_sheet_var = tk.BooleanVar()
        text = 'Только выбранная тема' if self.parent.db.engine else 'Только выбранный лист'
        self.chbx_filter_sheet = ttk.Checkbutton(self.container_above_table, text=text, variable=self.filter_sheet_var,
                                                 padding=(30, 0, 5, 0))
        self.chbx_filter_sheet.pack(side='left', anchor='w')

        # Иконка поиска с подсказкой - сборка из родительского метода
        icon_search_in_sheets = self.parent.put_icon_search_in_filter(
            parent_container=self.container_above_table, widget=self, tooltip_x_y=(595, 200))
        icon_search_in_sheets.pack(side='left', anchor='w', padx=2, pady=15)

        # Сборка контейнера с выбором листа и кнопкой сортировки
        self.container_cmbbx_filter = tk.Frame(self.container_above_table, background=self.bg)
        self.container_cmbbx_filter.pack(side='left', anchor='w')
        self.put_container_choose_sheet()

        # Простановка отметок фильтрации после обновления по сохранённым данным
        self._set_choose_filters()

        # Кнопка запроса формирования отчёта
        image = Image.open(settings.ICON_DOWNLOAD['path'])
        image = image.resize((17, 17))
        icon = ImageTk.PhotoImage(image)
        self.btn_create_report = ttk.Button(self.container_above_table, text='Сформировать отчёт',
                                            command=self.handler_generate_report, image=icon, compound=tk.LEFT, style='List.TButton')
        self.btn_create_report.image = icon
        self.btn_create_report.pack(side='right', anchor='w', padx=(10, 20), pady=0)

    def put_container_choose_sheet(self) -> None:
        """ Сборка контейнера с выбором листа и кнопкой сортировки """

        # Комбобокс выбор листа
        cmbbx_list = []                                                 # Получаем список листов/тем
        if self.parent.data_type == 'Excel':
            cmbbx_list = self.parent.excel_get_list_all_sheets() if self.parent.wb else []
        elif self.parent.data_type == 'База':
            cmbbx_list = self.parent.db.get_list_all_themes() if self.parent.db.engine else []

        if self.parent.sorted:
            cmbbx_list = self.parent.sort_sheet_list(cmbbx_list)        # Сортируем по заданной настройке
        cmbbx_list.insert(0, '-')

        self.choosen_sheet = ttk.Combobox(self.container_cmbbx_filter, values=cmbbx_list)
        self.choosen_sheet.pack(side='left', anchor='w', padx=0, pady=15)

        # Настройка фильтра выпадающего списка на основе введенного в поле значения
        self.choosen_sheet.bind("<KeyRelease>", lambda event: self.parent.on_key_release_filter_by_search(
            event, value_list=cmbbx_list, cmbbx_form=self.choosen_sheet))

        # Кнопка сортировки из родителя
        self.parent.put_icon_sort_sheets(container=self.container_cmbbx_filter, widget=self,
                                         func='put_container_choose_sheet')
        self.parent.btn_sort_sheets.pack(side='left', anchor='w', padx=0)
        TooltipCursorOnHover(self.parent.btn_sort_sheets, x=860, y=205,
                             text=f'Изменить сортировку на:\n{settings.SORTING_SHEETS[self.parent.sorted]}')

    def put_table_with_stat(self) -> None:
        """ Сборка контейнера с таблицей статистики """

        # Создаём таблицу
        heads = settings.TBL_STAT_HEADERS                                           # Заголовки столбцов таблицы
        self.table = ttk.Treeview(self.container_with_table, show='headings')
        self.table['columns'] = heads
        for header in heads:
            self.table.heading(header, text=header, anchor='center')
            self.table.column(header, anchor='center', width=172)

        # Очищаем таблицу перед вставкой новых данных - для корректной обработки событий при фильтрации
        for item in self.table.get_children():
            self.table.delete(item)

        # Добавление тегов для стилевого форматирования строк
        self.table.tag_configure("green", foreground=styles.GREEN_RED_GREY_FORMAT_STYLE[0])  # Тег для зеленого текста
        self.table.tag_configure("red", foreground=styles.GREEN_RED_GREY_FORMAT_STYLE[1])    # Тег для красного текста

        # Заполняем таблицу данными
        data = list(self.parent.stat_data)                  # Забираем список записей для вывода
        if data != []:
            for row in data:
                percent = row[4]                            # Форматируем данные
                if isinstance(percent, str):
                    percent = float(percent.split(' ')[0])
                row_formatted = row.copy()
                row_formatted[4] = f'{row_formatted[4]} %'

                value_threshholds = sorted(list(settings.STAT_COLOR_MATCH.keys()))            # Гибкая настройка стиля
                if percent < value_threshholds[0]:
                    self.table.insert('', tk.END, values=row_formatted, tags=("red",))
                elif percent > value_threshholds[1]:
                    self.table.insert('', tk.END, values=row_formatted, tags=("green",))
                else:
                    self.table.insert('', tk.END, values=row_formatted)

        # Привязка событий к таблице
        self.table.bind("<Double-1>", self.event_on_double_click)
        self.table.bind("<Button-3>", self.event_on_right_button_click)
        self.table.bind("<Motion>", self.event_on_off_hover_mouse)
        self.table.bind('<Button-1>', self.event_on_column_header_click)

        # Добавляем скроллинг
        self.scroll_panel = ttk.Scrollbar(self.container_with_table, command=self.table.yview)
        self.scroll_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscrollcommand=self.scroll_panel.set)
        self.table.pack(side='left', fill='both')

    def get_data_for_table_from_db(self) -> None:
        """ Забрать данные из Excel при отсутствии данных в атрибуте для хранения отчётов к выводу в таблице.
        Формируется список со списками данных каждого отчёта формата:
        [[1, datetime.datetime(2025, 1, 21, 1, 51, 1), 4, 4, 100.0, '-', 5, 'en -> ru: word'] ... ].
        Функция записывает данные в атрибут self.parent.stat_data"""

        # Получение данных всех отчётов из Excel
        if self.parent.data_type == 'Excel':
            if self.parent.stat_data is None:
                self.parent.stat_data = list(self.parent.excel_get_statistic_sheet_data())

        # Получение данных всех отчётов из БД
        elif self.parent.data_type == 'База':
            if self.parent.stat_data is None:
                self.parent.stat_data = self.parent.db.get_list_all_statistic_reports()

    def filter_dataset_for_table(self, if_all: str, from_date: str, date_before: str, if_type: bool, test_type: str,
                                 if_sheet: bool, sheet: str, sort_by: str | None = None, desc_order: bool = True
                                 ) -> None:
        """
        Фильтрация отчётов для отображения в таблице согласно пользовательским фильтрам.
        Принимает набор фильтров и записывает в self.parent.stat_data отфильтрованные данные для отображения в таблице.
        Пример набора фильтров: ['filter', '2025-01-15', '2025-01-21', True, 'en -> ru: word', True, '-']

        :param if_all: str 'all' или 'filter' - записи за все даты или с фильтром по датам
        :param from_date: str записи НАЧИНАЯ С ДАТЫ
        :param date_before: str записи ДАТА ПО
        :param if_type: bool фильтр по типу тестирования
        :param test_type: str название типа тестирования
        :param if_sheet: bool фильтр по теме/листу
        :param sheet: str название темы/листа
        :param sort_by: str обозначение вида сортировки (если есть) или None
        :param desc_order: bool реверсивность сортировки
        """
        # Получение отфильтрованных данных из БД
        if self.parent.data_type == 'База':
            self.parent.stat_data = self.parent.db.get_list_filtered_statistic_reports(
                [if_all, from_date, date_before, if_type, test_type, if_sheet, sheet], sort_by, desc_order)

        # Получение отфильтрованных данных из Excel
        if self.parent.data_type == 'Excel':

            filtered_stat = list(self.parent.excel_get_statistic_sheet_data())      # Все отчёты

            if if_type and test_type:                                               # Фильтр по типу
                filtered_stat = [i for i in filtered_stat if i[7] == test_type]

            if if_sheet and sheet:                                                  # Фильтр по листу
                filtered_stat = [i for i in filtered_stat if sheet == i[5]]

            if from_date and if_all == 'filter':                                    # Фильтр период с
                from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
                filtered_stat = [i for i in filtered_stat if i[1] >= from_date]

            if date_before and if_all == 'filter':                                  # Фильтр период по
                date_before = datetime.datetime.strptime(date_before, '%Y-%m-%d').date()
                filtered_stat = [i for i in filtered_stat if i[1] <= date_before]

            self.parent.stat_data = list(filtered_stat)            # Запись отфильтрованных данных в атрибут

    def event_on_double_click(self, event=None) -> None:
        """ Обработчик двойного клика по строке отчёта статистики. Вызов детализации отчёта """

        item = self.table.selection()[0]                            # Получаем выбранную строку
        values = self.table.item(item, 'values')
        self.parent.popup.view_stat_row_popup(values)               # Вызов окна с детализацией отчёта

    def event_on_off_hover_mouse(self, event) -> None:
        """ Обработчик события наведение курсора на строку, настройка подсветки """

        item = self.table.identify_row(event.y)                     # Получаем строку по значению y
        if item != self.current_hovered:                            # Если курсор находится на новой строке
            if self.current_hovered:                                # Снимаем подсветку с предыдущей строки
                current_tags = self.table.item(self.current_hovered, "tags")
                if "highlight" in current_tags:
                    current_tags = tuple(tag for tag in current_tags if tag != "highlight")
                    self.table.item(self.current_hovered, tags=current_tags)
            if item:                                                # Добавляем подсветку на новую строку
                current_tags = self.table.item(item, "tags")
                current_tags = tuple([current_tags, 'highlight'])   # Добавляем подсветку
                self.table.item(item, tags=current_tags)
                self.table.tag_configure("highlight", background=styles.EVENT_HOVER_CURSOR_TABLE)
                self.current_hovered = item                         # Обновляем текущую строку в var

    def event_on_right_button_click(self, event) -> None:
        """ Создание контекстного меню для вызова правой клавишей """

        # Создаём меню
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Открыть отчёт", command=self.event_on_double_click)
        self.context_menu.add_command(label="Удалить", command=self.handler_delete_row_from_table)

        item = self.table.identify_row(event.y)                     # Получаем строку по координату y
        if item:
            self.table.selection_set(item)                          # Выбираем строку в select
            self.context_menu.post(event.x_root, event.y_root)      # Показываем контекстное меню

    def event_on_column_header_click(self, event) -> None:
        """ Обработчик клика на заголовок колонки в таблице. Сортировка по параметру"""

        # Определяем индекс столбца, по хедеру которого был клик
        region = self.table.identify_region(event.x, event.y)   # Определяем, что клик по заголовку
        if region == 'heading':
            col = self.table.identify_column(event.x)           # Получаем идентификатор столбца по координатам клика
            col = int(col.strip('#')) - 1                       # Преобразуем его в индекс столбца

            # Логика сортировки - получаем тип сортировки и реверсивность
            if col == 0:                                                # id
                if self.parent.col_id_reverse == True:
                    sort_by, desc_order = 'id', False
                    self.parent.col_id_reverse = False
                elif self.parent.col_id_reverse == False:
                    sort_by, desc_order = 'id', True
                    self.parent.col_id_reverse = True

            elif col == 4:                                              # % прохождения
                if self.parent.col_percent_reverse == True:
                    desc_order = True
                    self.parent.col_percent_reverse = False
                elif self.parent.col_percent_reverse == False:
                    desc_order = False
                    self.parent.col_percent_reverse = True

            elif col == 5:                                              # Тема/Название листа
                if self.parent.col_theme_reverse == False:
                    sort_by, desc_order = 'theme', False
                    self.parent.col_theme_reverse = True
                elif self.parent.col_theme_reverse == True:
                    sort_by, desc_order = 'theme', True
                    self.parent.col_theme_reverse = False

            elif col == 7:                                              # Тип тестирования
                if self.parent.col_test_type_reverse == False:
                    sort_by, desc_order = 'type', False
                    self.parent.col_test_type_reverse = True
                elif self.parent.col_test_type_reverse == True:
                    sort_by, desc_order = 'type', True
                    self.parent.col_test_type_reverse = False

            # Настраиваем сортировку для работы с БД
            if self.parent.data_type == 'База':

                # Для вычисляемого столбца сильно проще вычислить на стороне python
                if col == 4:
                    self.parent.stat_data = sorted(self.parent.stat_data, key=lambda x: x[col], reverse=desc_order)
                    self.parent.refresh()
                    return

                # Определяем фильтры
                mock_filter = ['all', '', '', False, '', False, '']     # Заглушка фильтрации для запроса
                fltrs = self.parent.filter_stat_settings if self.parent.filter_stat_settings else mock_filter

                # Достаём из БД отфильтрованные данные с нужной сортировкой
                self.filter_dataset_for_table(*fltrs, sort_by, desc_order)
                self.parent.refresh()

            elif self.parent.data_type == 'Excel':
                self.parent.stat_data = sorted(self.parent.stat_data, key= lambda x: x[col], reverse=desc_order)
                self.parent.refresh()

    def handler_delete_row_from_table(self) -> None:
        """ Удалить запись отчёта статистики """

        selected_item = self.table.selection()                      # Получаем выбранную строку
        if selected_item:
            values = self.table.item(selected_item[0], 'values')    # Достаём значения строки

            # Подтверждение удаления или отмена действия
            answer = mbox.askyesno('Подтвердите удаление',
                                   f'Вы действительно хотите удалить отчёт id '
                                   f'{int(values[0])}?\nОтменить действие будет невозможно')
            if answer == 'Нет' or answer == False:
                return

            # Удаляем запись в Excel
            if self.parent.data_type == 'Excel':
                deleted = self.parent.excel_delete_statistic_report_row(int(values[0]), self.parent.excel_path)
                if deleted:
                    self.table.delete(selected_item)                # Удаление из отображения таблицы при успехе

            # Удаление из БД отчёта + связанных попыток
            elif self.parent.data_type == 'База':
                deleted: bool = self.parent.db.delete_statistic_report_by_id(int(values[0]))
                if deleted:
                    self.table.delete(selected_item)                # Удаление из отображения таблицы при успехе

        self.parent.stat_data = None                                # Сброс данных для отображения

    def handler_generate_report(self) -> None:
        """Обработчик кнопки Формирования отчёта.
        Получает информацию от всех форм с фильтрами, фиксирует её, формирует новую выборку отчётов с учётом фильтров"""

        # Получаем информацию от всех форм фильтров
        if_all = self.radio_filter_data_var.get()
        from_date = self.date_from.get()
        date_before = self.date_before.get()

        if_type = self.filter_type_var.get()
        test_type = self.cmbbx_choose_test_type.get()

        if_sheet = self.filter_sheet_var.get()
        sheet = self.choosen_sheet.get()

        # Записываем их в родительский атрибут
        self.parent.filter_stat_settings = [if_all, from_date, date_before, if_type, test_type, if_sheet, sheet]

        # Отфильтровываем данные для вывода в таблицу и обновляем окно
        self.filter_dataset_for_table(if_all, from_date, date_before, if_type, test_type, if_sheet, sheet)
        self.parent.refresh()

    def _set_choose_filters(self) -> None:
        """
        Установить отметки фильтрации записей по сохранённым данным.

        Формат self.parent.filter_stat_settings:
        ['filter', '2025-01-01', '2025-01-08', True, 'en -> ru: word', True, '-']
        """
        if self.parent.filter_stat_settings:
            self.radio_filter_data_var.set(self.parent.filter_stat_settings[0])     # Все даты / Выбор периода

            if self.parent.filter_stat_settings[0] == 'filter':
                if self.parent.filter_stat_settings[1]:
                    self.date_from.set_date(self.parent.filter_stat_settings[1])    # Установить период с
                if self.parent.filter_stat_settings[2]:
                    self.date_before.set_date(self.parent.filter_stat_settings[2])  # Установить период по

            if self.parent.filter_stat_settings[3]:                                 # Выбор типа теста
                self.filter_type_var.set(self.parent.filter_stat_settings[3])
                if self.parent.filter_stat_settings[4]:                             # Выбранный тип теста
                    self.cmbbx_choose_test_type.set(self.parent.filter_stat_settings[4])

            if self.parent.filter_stat_settings[5]:
                self.filter_sheet_var.set(self.parent.filter_stat_settings[5])      # Выбор листа
                if self.parent.filter_stat_settings[6]:
                    self.choosen_sheet.set(self.parent.filter_stat_settings[6])     # Выбранный лист

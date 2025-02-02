import tkinter as tk
from tkinter import messagebox as mbox, ttk

from Utils import auxiliary_tools as tls
import settings
import styles
from Utils.auxiliary_tools import get_percent_style, replace_none_to_empty_str_in_list, context_formatting
from Utils.custom_widgets.tooltips import TooltipCursorOnHover
from Utils.custom_widgets.hover_btn_text import HoverButton


class Popup:
    """ Класс для гибкой генерации всплывающих окон """

    def __init__(self, master):
        self.master = master  # Закрепляем в атрибут ссылку на родителя для обращения к его св-вам и методам

        self.flag_error_cmbbx = False       # Для изменения стилей при ошибках валидации
        self.flag_error_word = False

        self.choosen_sheet_cmbbx = None     # Сохранение данных из форм ввода новой записи
        self.word = None
        self.transcript = None
        self.translate = None
        self.context = None

    def show_popup(self, popup_method):
        """ Вызывает переданный метод объекта Popup """
        getattr(self, popup_method)()

    def exit_confirmation(self):
        answer = mbox.askquestion('Закрыть приложение', 'Вы уверены, что хотите выйти из приложения?')
        if answer == 'yes':
            self.master.destroy()

    def reset_confirmation(self):
        answer = mbox.askquestion('Перезапустить приложение', 'Вы уверены, что хотите перезапустить приложение?')
        if answer == 'yes':
            self.master.destroy()
            app = self.master.__class__()
            app.mainloop()

    def show_wb(self):
        """ Посмотреть выбранную книгу Excel """
        mbox.showinfo('Выбранная книга Excel', self.master.excel_path)

    def loading_excel_data_to_db_popup(self) -> None:
        """ Окно запуска импорта данных в БД из Excel книги"""

        dialog = tk.Toplevel(self.master)                       # Настройки окна
        text = 'Загрузка данных из Excel'
        dialog.title(text)
        dialog.transient(self.master)
        dialog.geometry('350x115+100+100')
        dialog.minsize(350, 115)
        dialog.maxsize(350, 115)
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)

        bg = styles.STYLE_COLORS[self.master.current_color_style]['background']
        container = tk.Frame(dialog, background=bg, width=350)
        container.grid_columnconfigure(0, weight=1)
        container.grid(row=0, column=0, sticky='nswe')

        # Контейнер с текстовым лейблом и лейблом подсчёта загруженных строк
        label_container = tk.Frame(container, background=bg)
        label_container.grid(row=0, column=0, sticky='wsne')

        label = ttk.Label(label_container, text=f'Слов загружено:', style='AddRowLbl.TLabel', padding=(10, 20, 20, 10))
        label.grid(row=0, column=0, sticky='ws')                                    # Лейбл

        self.percentage_label = ttk.Label(label_container, text='0', style='AddRowLbl.TLabel', padding=(10, 20, 20, 10))
        self.percentage_label.grid(row=0, column=1, sticky='e')                     # Количество загруженных слов

        # Прогресс-бар
        self.progress_bar = ttk.Progressbar(container, orient='horizontal', length=300, mode="determinate", maximum=20)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky='we', padx=10)

        # Кнопка ВЫБОР ФАЙЛА / ссылка на его изменение
        if not self.master.wb:
            btn_choose_xls = ttk.Button(container, text='Выберите файл .xls', style='AddRow.TButton',
                                        command=lambda: self.on_click_choose_wb(dialog))
            btn_choose_xls.grid(row=2, column=0, sticky='wn', padx=10, pady=10)
        else:
            btn_choose_xls = HoverButton(container, text='Файл .xls выбран. Изменить?', bd=0, background=bg,
                                         fg=styles.STYLE_COLORS[self.master.current_color_style]['foreground_main'],
                                         command=lambda: self.on_click_choose_wb(dialog))
            btn_choose_xls.grid(row=2, column=0, sticky='ws', padx=10, pady=8)

        # Кнопка запуска загрузки
        if self.master.wb:
            btn_submit = ttk.Button(container, text='Начать загрузку', style='AddRow.TButton',
                                    command=lambda: self.on_click_start_loading_words(dialog))
            btn_submit.grid(row=2, column=1, sticky='en', padx=10, pady=10)

        dialog.wait_window()

    def on_click_choose_wb(self, dialog: tk.Toplevel) -> None:
        """
        Обработчик выбора файла Excel.
        Открывает диалог к выбору файла, загружает его в переменную, перезапускает всплывающее окно
        с учетом выбранного файла.

        :param dialog: всплывающее окно с загрузкой.
        """
        self.master.excel_open_file()
        dialog.destroy()
        self.loading_excel_data_to_db_popup()

    def on_click_start_loading_words(self, dialog: tk.Toplevel) -> None:
        """
        Обработчик старта импорта данных из Excel в БД.
        Загружает из выбранного файла Excel новые данные в БД.

        :param dialog: всплывающее окно с загрузкой.
        """
        all_sheets = self.master.excel_get_list_all_sheets()        # Список всех листов книги (кроме системных)
        all_themes = self.master.db.get_list_all_themes()           # Список с названиями всех тем в БД
        counter_ = 0                                                # Счётчик загруженных слов

        # Расчёт общего количества слов в Excel для корректного отображания прогресс-бара
        total_counter = 0
        for sheet_name in all_sheets:
            total_counter += self.master._get_counter_rows_from_excel(
                self.master.wb[sheet_name], index_from=settings.EXCEL_INDEX_FIRST_ROW_WITH_DATA)
        self.progress_bar['maximum'] = total_counter                # Общее количество строк со словами в книге Excel

        # Итерируемся по каждому листу
        for sheet_name in all_sheets:

            # Если названия листа нет в темах БД - создаём новую тему с названием листа
            if sheet_name not in all_themes:
                self.master.db.create_new_subject(sheet_name)

            # Получаем список со списками со всеми данными записей листа
            sheet_all_words = self.master.excel_get_all_data_from_sheet(sheet_name)

            # Для каждой строки-записи листа - если отсутствует в БД, то создаём
            for row in sheet_all_words:
                replace_none_to_empty_str_in_list(row)                          # Форматирование None

                is_new = self.master.db.is_new_word(row[1], row[2], row[3])
                if is_new:
                    context_formatting(row, indent='\n')                        # Форматирование Контекста - переносы
                    self.master.db.create_new_word(sheet_name, row[1], row[2], row[3], row[4])
                    counter_ += 1

                    # Обновляем визуал прогресс-бара и лейбла с подсчётом загруженных слов
                    self.progress_bar['value'] = counter_                       # Устанавливаем значение прогресс-бара
                    self.percentage_label.config(text=f"{counter_}")            # Обновляем текст с процентом
                    dialog.update_idletasks()                                   # Обновляем интерфейс

        # Выводим системку с результатом
        if counter_ == 0:
            mbox.showwarning('', 'Нет новых данных для загрузки')
        else:
            self.progress_bar['value'] = self.progress_bar['maximum']           # Заполняем прогресс-бар
            mbox.showinfo('', 'Данные успешно загружены!')

        self.master.wb = None                                                   # Сбрасываем рабочую книгу Excel
        self.master.refresh()
        dialog.destroy()

    def add_new_sheet_popup(self):
        """ Окно ввода данных для добавления нового листа Excel в выбранной книге """

        dialog = tk.Toplevel(self.master)
        text = 'Создание новой темы в БД' if self.master.db.engine else 'Создание нового листа в книге Excel'
        dialog.title(text)
        dialog.transient(self.master)       # Привязываем Toplevel к родительскому окну, чтобы оно всегда было поверх
        dialog.geometry('350x115+100+100')
        dialog.minsize(350, 115)
        dialog.maxsize(350, 115)
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)

        bg = styles.STYLE_COLORS[self.master.current_color_style]['background']
        container = tk.Frame(dialog, background=bg, width=350)
        container.grid_columnconfigure(0, weight=1)
        container.grid(row=0, column=0, sticky='nswe')
        text = 'Укажите название новой темы' if self.master.db.engine else 'Укажите название нового листа Excel'
        header = ttk.Label(container, text=text, style='AddRowLbl.TLabel', padding=(10, 20, 20, 10))
        header.grid(row=0, column=0, sticky='ws')
        self.form_enter_sheet_name = ttk.Entry(container, width=50)
        self.form_enter_sheet_name.grid(row=1, column=0, sticky='we', padx=10)
        btn_submit = ttk.Button(container, text='Создать', command=lambda: self.on_click_ADDSHEET(dialog), style='AddRow.TButton')
        btn_submit.grid(row=2, column=0, sticky='en', padx=10, pady=10)

        dialog.wait_window()

    def on_click_ADDSHEET(self, dialog):
        """ Добавление нового листа в книгу Excel """
        self.new_sheet_name = self.form_enter_sheet_name.get()
        self.new_sheet_name = self.new_sheet_name[0].upper() + self.new_sheet_name[1:]

        if not self.validate_sheet_name():                              # Валидация названия
            return

        # Создание и сохранение листа
        if self.master.data_type == 'Excel':
            wb_name = self.master.excel_create_sheet(self.new_sheet_name, self.master.excel_path)
            mbox.showinfo('', f'Вы создали новый лист "{self.new_sheet_name}" в файле {wb_name}')
        elif self.master.data_type == 'База':
            new_theme = self.master.db.create_new_subject(self.new_sheet_name)
            if new_theme:
                mbox.showinfo('', f'Вы создали новый раздел "{self.new_sheet_name}" в файле {self.master.db.db_path}')

        dialog.destroy()
        self.master.refresh()

    def edit_sheet_popup(self):
        """ Диалоговое окно с формами для редактирования листа Excel """
        dialog = tk.Toplevel(self.master)
        text = 'Редактирование темы' if self.master.db.engine else 'Редактирование листа'
        dialog.title(text)
        dialog.transient(self.master)
        dialog.geometry('350x115+100+100')
        dialog.minsize(350, 115)
        dialog.maxsize(350, 115)
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)

        bg = styles.STYLE_COLORS[self.master.current_color_style]['background']
        container = tk.Frame(dialog, background=bg, width=350)
        container.grid_columnconfigure(0, weight=1)
        container.grid(row=0, column=0, sticky='nswe')
        text = 'темы' if self.master.db.engine else 'листа Excel'
        header = ttk.Label(container, text=f'Укажите новое название {text}', style='AddRowLbl.TLabel',
                           padding=(10, 20, 20, 10))
        header.grid(row=0, column=0, sticky='ws')
        self.form_enter_sheet_name = ttk.Entry(container, width=50)
        current_name = self.master.choosen_db_theme if self.master.choosen_db_theme else self.master.choosen_excel_list
        self.form_enter_sheet_name.insert(0, current_name)
        self.form_enter_sheet_name.grid(row=1, column=0, sticky='we', padx=10)


        btn_container = tk.Frame(container, bg=bg)
        btn_container.grid(row=2, column=0, sticky='en', padx=10, pady=10)

        self.var_delete_sheet = tk.BooleanVar()
        text = 'тему' if self.master.db.engine else 'лист Excel'
        self.chkbx_delete_sheet = ttk.Checkbutton(btn_container, text=f'Удалить {text}',
                                                  variable=self.var_delete_sheet, style='Red.TCheckbutton')
        self.chkbx_delete_sheet.grid(row=0, column=0, sticky='s', padx=50)

        btn_submit = ttk.Button(btn_container, text='Подтвердить', command=lambda: self.on_click_EDITSHEET(dialog),
                                style='AddRow.TButton')
        btn_submit.grid(row=0, column=1, sticky='en')

        dialog.wait_window()

    def on_click_DELETESHEET(self):
        """ Обработчик удаления листа Excel / темы в БД """

        # Подтверждение удаления
        text = 'тему' if self.master.db.engine else 'лист'
        answer = mbox.askyesno('Подтвердите удаление',
                               f'Вы действительно хотите удалить {text}?\nОтменить действие бедет невозможно')
        if answer == 'Нет' or answer == False:
            return

        # Удаление из базы
        if self.master.data_type == 'Excel':
            self.master.excel_delete_sheet(self.master.choosen_excel_list, self.master.excel_path)
            mbox.showinfo('Сообщение', f'Лист "{self.master.choosen_excel_list}" удалён')
            self.master.choosen_excel_list = None

        elif self.master.data_type == 'База':
            if self.master.db.delete_subject(self.master.choosen_db_theme):
                mbox.showinfo('Сообщение', f'Тема "{self.master.choosen_db_theme}" удалена')
                self.master.choosen_db_theme = None

        self.master.refresh()

    def on_click_EDITSHEET(self, dialog):
        """ Обработчик редактирования листа Excel """
        to_delete = self.var_delete_sheet.get()
        if to_delete:
            self.on_click_DELETESHEET()                             # Удаление листа
            dialog.destroy()
            return
        # Редактирование названия листа
        self.new_sheet_name = self.form_enter_sheet_name.get()
        if not self.validate_sheet_name():                          # Валидация названия листа
            return
                                                                    # Редактирование и сохранение
        self.master.excel_edit_sheet_name(old_sheet_name=self.master.choosen_excel_list,
                                          new_sheet_name=self.new_sheet_name, excel_path=self.master.excel_path)
        mbox.showinfo('Сообщение', 'Изменения сохранены')
        self.master.choosen_excel_list = self.new_sheet_name        # Обновление переменной
        dialog.destroy()
        self.master.refresh()

    def edit_row_popup(self, row: list) -> None:
        """
        Окно с формами ввода для редактирования записей в базе

        :param row: список с данными для отображения:
                    [3, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
        """
        dialog = tk.Toplevel(self.master)                                   # Параметры окна
        dialog.title('Редактирование записи')
        dialog.geometry('760x415+100+100')
        dialog.transient(self.master)
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        bg = styles.STYLE_COLORS[self.master.current_color_style]['background']
        self.bg = bg
        self.data = row

        # Записываем данные ДО изменений
        self.given_choosen_sheet_cmbbx = self.master.choosen_excel_list if self.master.choosen_excel_list else \
            self.master.choosen_db_theme
        if len(row) == 6:                                                 # Если вызов из en-ru, имя листа в row[5]
            self.given_choosen_sheet_cmbbx = row[5]

        self.given_row_id = row[0]
        self.given_word = row[1]
        self.given_transcript = row[2]
        self.given_translate = row[3]
        self.given_context = row[4]

        container = tk.Frame(dialog, background=bg)
        container.grid(row=0, column=0, sticky='nswe')
        self.forms_container = tk.Frame(container, bg=bg)
        self.forms_container.grid(row=0, column=0, sticky='nswe', pady=20)

        # Выбор листа
        text = 'Выбранная тема:' if self.master.db.engine else 'Выбранный лист:'
        label_choose_sheet = ttk.Label(self.forms_container, text=text, style='AddRowLbl.TLabel', padding=(10, 8))
        label_choose_sheet.grid(row=1, column=0, sticky='en')                   # Лейбл

        self._put_container_choose_sheet()    # Сборка контейнера с Combobox выбора листа, фильтрацией и иконкой поиска

        # Слово - редактирование
        fg_validation_error = {}                                                # Настройка стилей после валидации
        if self.flag_error_word:
            fg_validation_error = {'foreground': styles.GREEN_RED_GREY_FORMAT_STYLE[1]}

        label_enter_word = ttk.Label(self.forms_container, text='Слово/Фраза:', style='AddRowLbl.TLabel',
                                     padding=(10, 8), **fg_validation_error)
        label_enter_word.grid(row=2, column=0, sticky='en')                     # Лейбл

        self.form_enter_word = ttk.Entry(self.forms_container, width=90)        # Форма ввода
        self.form_enter_word.insert(0, self.given_word)
        self.form_enter_word.grid(row=2, column=1, sticky='w')

        # Транскрипция - редактирование
        label_enter_transcript = ttk.Label(self.forms_container, text='Транскрипция:', style='AddRowLbl.TLabel',
                                           padding=(10, 8))
        label_enter_transcript.grid(row=3, column=0, sticky='en')               # Лейбл

        self.form_enter_transcript = ttk.Entry(self.forms_container, width=90)
        self.form_enter_transcript.insert(0, self.given_transcript)
        self.form_enter_transcript.grid(row=3, column=1, sticky='w')            # Форма ввода

        # Перевод - редактирование
        label_enter_translate = ttk.Label(self.forms_container, text='Перевод:', style='AddRowLbl.TLabel', padding=(10, 8))
        label_enter_translate.grid(row=4, column=0, sticky='en')                # Лейбл

        self.form_enter_translate = tk.Text(self.forms_container, width=68, height=5)
        self.form_enter_translate.insert(1.0, self.given_translate)
        self.form_enter_translate.grid(row=4, column=1, sticky='w', pady=10)    # Форма ввода

        # Контекст - редактирование
        label_enter_context = ttk.Label(self.forms_container, text='Примеры:', style='AddRowLbl.TLabel', padding=(10, 8))
        label_enter_context.grid(row=5, column=0, sticky='en')                  # Лейбл

        self.form_enter_context = tk.Text(self.forms_container, width=68, height=5)
        self.form_enter_context.insert(1.0, self.given_context)
        self.form_enter_context.grid(row=5, column=1, sticky='w', pady=5)       # Форма ввода

        # Кнопки
        btn_container = tk.Frame(self.forms_container, bg=bg)
        btn_container.grid(row=6, column=1, sticky='nse')
        btn_submit = ttk.Button(btn_container, text='Сохранить изменения', command=lambda: self.on_click_EDITROW(dialog),
                                style='AddRow.TButton')
        btn_submit.grid(row=0, column=1, sticky='en')                           # СОХРАНИТЬ

        self.delete_var = tk.BooleanVar()
        self.delete_checkbox = ttk.Checkbutton(container, text='Удалить запись из базы', variable=self.delete_var,
                                               style='Red.TCheckbutton')
        self.delete_checkbox.grid(row=1, column=0, columnspan=2, padx=40)       # УДАЛИТЬ

        dialog.wait_window()

    def on_click_EDITROW(self, dialog: tk.Toplevel) -> None:
        """ Обработчик кнопки редактирования записи с данными """
        self.choosen_sheet_cmbbx = self.form_choose_sheet.get()  # Забираем все переменные из форм
        self.word = self.form_enter_word.get()
        self.transcript = self.form_enter_transcript.get()
        self.translate = self.form_enter_translate.get(1.0, tk.END)
        self.context = self.form_enter_context.get(1.0, tk.END)
        to_delete = self.delete_var.get()

        # Подтверждение удаления
        if to_delete:
            answer = mbox.askyesno('Подтвердите удаление',
                                   'Вы действительно хотите удалить запись?\nОтменить действие бедет невозможно')
            if answer == 'Нет' or answer == False:
                return

            # Удаление записи из базы
            if self.master.data_type == 'Excel':
                if self.master.excel_delete_row(self):              # Удаление строки в Excel по данным из форм ввода
                    mbox.showinfo('', 'Запись удалена')
                else:
                    mbox.showerror('Ошибка', 'Ошибка индексации!\nID строки не соответствует значению.\nПроверьте файл')
            elif self.master.data_type == 'База':
                if self.master.db.delete_word(self.given_row_id):
                    mbox.showinfo('', 'Запись удалена')

            dialog.destroy()
            self.clear_self_atributes()                         # Сброс данных формы ввода
            self.master.refresh()                               # Обновление данных в окне
            return

        # Если непосредственно изменение данных
        if not self.validate_self_word():                       # Валидация слова/фразы
            dialog.destroy()
            self.edit_row_popup(self.data)
            return
        self.flag_error_word = False

        # Редактирование данных без изменения листа
        if self.master.data_type == 'Excel':

            if self.given_choosen_sheet_cmbbx == self.choosen_sheet_cmbbx:
                if self.master.excel_edit_row_data(self):                           # Редактирование в Excel
                    mbox.showinfo('Сообщение', 'Запись успешно обновлена!')
                else:
                    mbox.showerror('Ошибка', 'Ошибка индексации!\nID строки не соответствует значению.\nПроверьте файл')
            # Если при редактировании меняется лист
            else:
                if self.master.excel_delete_row(self):  # Удаление строки из старой страницы Excel
                    self.master.excel_create_row(self)  # Создание записи на новом листе книги Excel
                    mbox.showinfo('', 'Запись изменена!')
                    self.master.choosen_excel_list = self.choosen_sheet_cmbbx
                else:
                    mbox.showerror('Ошибка', 'Ошибка индексации!\nДействие не выполнено, проверьте файл')

        elif self.master.data_type == 'База':
            if self.master.db.update_word(self.given_row_id, self.word, self.transcript, self.translate, self.context,
                                          self.choosen_sheet_cmbbx):
                mbox.showinfo('', 'Запись изменена!')
            self.master.choosen_db_theme = self.choosen_sheet_cmbbx

        dialog.destroy()
        self.clear_self_atributes()                 # Сброс данных формы ввода
        self.master.refresh()                       # Обновление данных в окне

    def _put_container_choose_sheet(self) -> None:
        """ Сборка контейнера с выбором листа, фильтром, иконкой поиска + настроенными событиями поиска и фильтрации """

        bg = styles.STYLE_COLORS[self.master.current_color_style]['background']
        container_choose_sheet = tk.Frame(self.forms_container, bg=bg)
        container_choose_sheet.grid(row=1, column=1, sticky='w')

        # Иконка поиска с подсказкой
        icon_search_in_sheets = self.master.put_icon_search_in_filter(
            parent_container=container_choose_sheet, widget=self, tooltip_x_y=(70, 175))
        icon_search_in_sheets.grid(row=0, column=0, sticky='w', padx=(0, 2))

        # Форма Combobox

        # Список листов/разделов
        if self.master.data_type == 'Excel':
            cmbbx_values = self.master.excel_get_list_all_sheets() if self.master.wb else []
        elif self.master.data_type == 'База':
            cmbbx_values = self.master.db.get_list_all_themes() if self.master.db.engine else []

        # Сортируем по заданной настройке
        if self.master.sorted:
            cmbbx_values = self.master.sort_sheet_list(cmbbx_values)
        self.form_choose_sheet = ttk.Combobox(container_choose_sheet, values=cmbbx_values, width=80)

        # Настройка фильтра выпадающего списка на основе введенного в поле значения
        self.form_choose_sheet.bind("<KeyRelease>", lambda event: self.master.on_key_release_filter_by_search(
                event, value_list=cmbbx_values, cmbbx_form=self.form_choose_sheet))

        # Сборка кнопки сортировки из родителя
        self.master.put_icon_sort_sheets(container=container_choose_sheet, widget=self,
                                         func='_put_container_choose_sheet')
        self.master.btn_sort_sheets.grid(row=0, column=2, sticky='w')
        TooltipCursorOnHover(self.master.btn_sort_sheets, x=420, y=175,
                             text=f'Изменить сортировку на:\n{settings.SORTING_SHEETS[self.master.sorted]}')

        # Автозаполнение комбобокса
        if self.choosen_sheet_cmbbx:                                # Автозаполнение выбранного листа после валидации
            self.form_choose_sheet.set(self.choosen_sheet_cmbbx)
        elif self.master.choosen_excel_list:
            self.form_choose_sheet.set(self.master.choosen_excel_list)
        elif self.master.choosen_db_theme:
            self.form_choose_sheet.set(self.master.choosen_db_theme)
        elif hasattr(self, 'given_choosen_sheet_cmbbx'):
            if self.given_choosen_sheet_cmbbx:
                self.form_choose_sheet.set(self.given_choosen_sheet_cmbbx)  # До валидации - по изначальному листу/теме

        self.form_choose_sheet.grid(row=0, column=1, sticky='w')

    def add_row(self) -> None:
        """ Окно ввода данных для добавления новой записи в базу """
        dialog = tk.Toplevel(self.master)                           # Параметры окна
        text = f'БД {self.master.db.db_path}' if self.master.db.engine else f'книгу {self.master.excel_path}'
        dialog.title(f'Добавление новой записи в {text}')
        dialog.geometry('760x415+100+100')
        dialog.transient(self.master)
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        bg = styles.STYLE_COLORS[self.master.current_color_style]['background']
        self.bg = bg

        container = tk.Frame(dialog, background=bg)
        container.grid(row=0, column=0, sticky='nswe')
        self.forms_container = tk.Frame(container, bg=bg)
        self.forms_container.grid(row=0, column=0, sticky='nswe', pady=20)

        # Выбор листа
        fg_validation_error = {}                                    # Cловарь для настройки стиля при ошибках валидации
        if self.flag_error_cmbbx:
            fg_validation_error = {'foreground': styles.GREEN_RED_GREY_FORMAT_STYLE[1]}

        text = 'Выберите тему:' if self.master.db.engine else 'Выберите лист:'
        label_choose_sheet = ttk.Label(self.forms_container, text=text, style='AddRowLbl.TLabel',
                                       padding=(10, 8),
                                       **fg_validation_error)
        label_choose_sheet.grid(row=1, column=0, sticky='en')        # Лейбл

        # Сборка контейнера с выбором листа, фильтрацией и иконкой поиска
        self._put_container_choose_sheet()

        # Ввод слова/фразы
        fg_validation_error = {}                                                # Проверка валидации
        if self.flag_error_word:
            fg_validation_error = {'foreground': styles.GREEN_RED_GREY_FORMAT_STYLE[1]}

        label_enter_word = ttk.Label(self.forms_container, text='Слово/Фраза:', style='AddRowLbl.TLabel',
                                     padding=(10, 8), **fg_validation_error)
        label_enter_word.grid(row=2, column=0, sticky='en')                     # Лейбл

        self.form_enter_word = ttk.Entry(self.forms_container, width=90)        # Форма ввода
        if self.word:
            self.form_enter_word.insert(0, self.word)                           # Автозаполнение после валидации
        self.form_enter_word.grid(row=2, column=1, sticky='w')

        # Ввод транскрипции
        label_enter_transcript = ttk.Label(self.forms_container, text='Транскрипция:', style='AddRowLbl.TLabel',
                                           padding=(10, 8))
        label_enter_transcript.grid(row=3, column=0, sticky='en')               # Лейбл

        self.form_enter_transcript = ttk.Entry(self.forms_container, width=90)  # Форма ввода
        if self.transcript:
            self.form_enter_transcript.insert(0, self.transcript)               # Автозаполнение после валидации
        self.form_enter_transcript.grid(row=3, column=1, sticky='w')

        # Ввод перевода
        label_enter_translate = ttk.Label(self.forms_container, text='Перевод:', style='AddRowLbl.TLabel',
                                          padding=(10, 8))
        label_enter_translate.grid(row=4, column=0, sticky='en')                        # Лейбл

        self.form_enter_translate = tk.Text(self.forms_container, width=68, height=5)   # Форма ввода
        if self.translate:                                                              # Автозаполнение после валидации
            self.form_enter_translate.insert(1.0, self.translate)
        self.form_enter_translate.grid(row=4, column=1, sticky='w', pady=10)

        # Ввод контекста
        label_enter_context = ttk.Label(self.forms_container, text='Примеры:', style='AddRowLbl.TLabel',
                                        padding=(10, 8))
        label_enter_context.grid(row=5, column=0, sticky='en')                          # Лейбл

        self.form_enter_context = tk.Text(self.forms_container, width=68, height=5)     # Форма ввода
        if self.context:                                                            # Автозаполнение после валидации
            self.form_enter_context.insert(1.0, self.context)
        self.form_enter_context.grid(row=5, column=1, sticky='w', pady=5)

        # Кнопки
        btn_container = tk.Frame(self.forms_container, bg=bg)
        btn_container.grid(row=6, column=1, sticky='nswe', padx=393)
        btn_clear = ttk.Button(btn_container, text='Очистить', command=self.on_click_CLEAR)
        btn_clear.grid(row=0, column=0, sticky='wn', padx=0)                        # ОЧИСТИТЬ

        btn_submit = ttk.Button(btn_container, text='Записать', command=lambda: self.on_click_ADDROW(dialog),
                                style='AddRow.TButton')                             # ЗАПИСАТЬ
        btn_submit.grid(row=0, column=1, sticky='wn', padx=5)

        foot_container = tk.Frame(container, bg=bg)
        foot_container.grid(row=1, column=0, sticky='snwe', padx=280)               # ВЫБРАТЬ ДРУГОЙ ФАЙЛ
        label_change_file = ttk.Label(foot_container, text='Выбрать другой файл .xls', style='ChooseFile.TLabel')
        label_change_file.grid(row=0, column=0)
        btn_change_file = ttk.Button(foot_container, text='Изменить', style='ChngFile.TButton',
                                     command=self.master.handler_select_file_wb)
        btn_change_file.grid(row=0, column=1)

        dialog.wait_window()

    def on_click_ADDROW(self, dialog: tk.Toplevel) -> None:
        """ Обработчик добавления новой записи в Excel """
        self.choosen_sheet_cmbbx = self.form_choose_sheet.get()            # Забираем все переменные из форм
        self.word = self.form_enter_word.get()
        self.transcript = self.form_enter_transcript.get()
        self.translate = self.form_enter_translate.get(1.0, tk.END)
        self.context = self.form_enter_context.get(1.0, tk.END)

        # Валидация данных из форм
        if not self.choosen_sheet_cmbbx:
            text = 'тему' if self.master.db.engine else 'лист Excel'
            mbox.showerror('', f'Необходимо выбрать {text}')
            self.flag_error_cmbbx = True
            dialog.destroy()                                                # Для обновления стилей валидации
            self.add_row()
            return
        if not self.validate_self_word():
            dialog.destroy()                                                # Для обновления стилей валидации
            self.add_row()
            return

        self.flag_error_word = False                 # Если валидация прошла отменяем флаги и форматируем под эксель
        self.flag_error_cmbbx = False


        if self.master.data_type == 'Excel':
            self.context = self.context.replace('\n', '     ')  # Мне просто так удобнее в Excel файле
            self.master.excel_create_row(self)                                  # Создаём и сохраняем новую запись
            mbox.showinfo('', 'Запись успешно создана!')
            self.master.choosen_excel_list = self.choosen_sheet_cmbbx  # Если был выбор другого листа, устанавливаем его
        elif self.master.data_type == 'База':
            new_word = self.master.db.create_new_word(self.choosen_sheet_cmbbx, self.word, self.transcript, self.translate, self.context)
            if new_word:
                mbox.showinfo('', 'Запись успешно создана!')

        dialog.destroy()
        self.clear_self_atributes()                                         # Сброс данных формы ввода
        self.master.refresh()                                               # Обновление данных в окне

    def on_click_CLEAR(self) -> None:
        """ Очистка данных в формах """
        self.form_choose_sheet.delete(0, tk.END)
        self.form_enter_word.delete(0, tk.END)
        self.form_enter_transcript.delete(0, tk.END)
        self.form_enter_translate.delete(1.0, tk.END)
        self.form_enter_context.delete(1.0, tk.END)

    def settings_speech_popup(self) -> None:
        """ Окно настроек синтеза речи """
        dialog = tk.Toplevel(self.master)                           # Параметры окна
        dialog.title(f'Настройки речи')
        dialog.geometry('710x275+100+100')
        dialog.transient(self.master)
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        self.bg = styles.STYLE_COLORS[self.master.current_color_style]['background']
        container = tk.Frame(dialog, background=self.bg)
        container.grid(row=0, column=0, sticky='nswe')

        # Контейнер с громкостью
        container_with_volume = tk.Frame(container, background=self.bg)
        container_with_volume.pack(anchor='sw', pady=(40, 10))

        lbl = ttk.Label(container_with_volume, text='Громкость', style='AddRowLbl.TLabel')
        lbl.pack(anchor='w', side='left', padx=(70, 20))        # Лейбл

        lbl = tk.Label(container_with_volume, text='0', font=("Arial", 12), background=self.bg)
        lbl.pack(side='left', padx=3)                           # Лейбл MIN

        value_label = tk.Label(container_with_volume, text=str(int(self.master.engine_speech.speech_volume)), font=("Arial", 12), background=self.bg)

        volume_scale = ttk.Scale(container_with_volume, from_=0, to=100, orient=tk.HORIZONTAL,
                                 command= lambda val, value_label=value_label:self.master.engine_speech.set_volume(val, value_label),
                                 style="Custom.Horizontal.TScale", length=380)
        volume_scale.set(self.master.engine_speech.speech_volume)
        volume_scale.pack(side='left', pady=(0, 0))             # Бегунок для громкости от 0 до 100

        value_label.pack(side='left', padx=3)                   # Лейбл VALUE

        # Контейнер со скоростью речи
        container_with_speed = tk.Frame(container, background=self.bg)
        container_with_speed.pack(anchor='sw', pady=(10, 10))

        lbl = ttk.Label(container_with_speed, text='Скорость речи', style='AddRowLbl.TLabel')
        lbl.pack(anchor='w', side='left', padx=(45, 20))        # Лейбл

        lbl = tk.Label(container_with_speed, text='0', font=("Arial", 12), background=self.bg)
        lbl.pack(side='left', padx=3)                           # Лейбл MIN

        speed_label = tk.Label(container_with_speed, text=f"{self.master.engine_speech.speech_rate}", font=("Arial", 12), background=self.bg)

        volume_scale = ttk.Scale(container_with_speed, from_=0, to=200, orient=tk.HORIZONTAL,
                                 command=lambda val, value_label=speed_label: self.master.engine_speech.set_speed(val, speed_label),
                                 style="Custom.Horizontal.TScale", length=380)
        volume_scale.set(self.master.engine_speech.speech_rate)
        volume_scale.pack(side='left', pady=(0, 0))             # Бегунок для скорости от 0 до 200

        speed_label.pack(side='left', padx=3)                   # Лейбл VALUE

        # Контейнер с голосом
        container_with_voice = tk.Frame(container, background=self.bg)
        container_with_voice.pack(anchor='sw', pady=(10, 0))

        lbl = ttk.Label(container_with_voice, text='Выберите голос', style='AddRowLbl.TLabel')
        lbl.pack(anchor='w', side='left', padx=(34, 66))        # Лейбл

        self.rbtn_var = tk.StringVar()                                # Радио кнопки
        self.rbtn_var.set(self.master.engine_speech.speech_voice)
        rbtn_1 = ttk.Radiobutton(container_with_voice, text='Женский', variable=self.rbtn_var, value='female',
                                 command=lambda: self.master.engine_speech.set_voice(self.rbtn_var.get()))
        rbtn_1.pack(side='left', padx=(45, 35))
        rbtn_1 = ttk.Radiobutton(container_with_voice, text='Мужской', variable=self.rbtn_var, value='male',
                                 command=lambda: self.master.engine_speech.set_voice(self.rbtn_var.get()))
        rbtn_1.pack(side='left', padx=(35, 5))

        # Кнопка выхода
        btn_submit = ttk.Button(container, text='OK', command=lambda: self.on_click_OK_settings_speech(dialog),
                                style='AddRow.TButton')
        btn_submit.pack(side='right', anchor='s', pady=(0, 10), padx=20)

        dialog.wait_window()

    def on_click_OK_settings_speech(self, dialog: tk.Toplevel) -> None:
        """
        Обработчик кнопки выхода из настроек речи. Подтверждение данных для записи в настройки БД

        :param dialog: объект диалогового окна
        """
        if self.master.data_type == 'База':                     # Записываем в пользовательские настройки приложения
            self.master.db.set_new_speech_settings(
                self.master.engine_speech.speech_volume, self.master.engine_speech.speech_rate, self.rbtn_var.get())
        dialog.destroy()

    def handler_choose_db(self):                                    # TODO: ! НЕАКТУАЛ КРОМЕ ТЕСТ
        self.popup_ask_db_type()
        self.master.parent.data_type = self.result
        if self.result == 'Excel':
            self.master.parent.handler_select_file_wb()
        if self.result == 'База':
            self.master.parent.excel_path = None
            self.master.parent.wb = None
            self.master.parent.refresh()

    def popup_ask_db_type(self):                                    # TODO: ! НЕАКТУАЛ КРОМЕ ТЕСТ
        """ Вывод окна с выбором типа базы """
        dialog = tk.Toplevel(self.master)
        self.master.parent.bell()
        tls.toplvl_msg_set_standart_params(dialog, '')

        main_container = tk.Frame(dialog, **styles.TOP_LVL_MSG_STANDART_CONTAINER)
        main_container.grid(row=0, column=0, sticky='nswe')
        main_container.grid_columnconfigure(0, weight=1)
        cont_msg = tk.Frame(main_container, background='white')
        cont_msg.grid(row=0, column=0, sticky='nswe')
        message_label = ttk.Label(cont_msg, text="Выберите тип данных", style='MsgLbl.TLabel')
        message_label.grid(row=0, column=0, sticky='snwe', pady=8, padx=20)

        cont_btns = tk.Frame(main_container, background=styles.LIGHTGRAY_SYSTEM)
        cont_btns.grid(row=1, column=0, sticky='snwe', padx=5)
        button_1 = ttk.Button(cont_btns, text="Excel", command=lambda: self.on_click_Excel(dialog), style='Popup.TButton')
        button_1.grid(row=0, column=0, sticky='sne', pady=12, padx=10)
        button_2 = ttk.Button(cont_btns, text="База", command=lambda: self.on_click_DB(dialog), style='Popup.TButton')
        button_2.grid(row=0, column=1, sticky='snw', pady=12,padx=10)

        dialog.wait_window(dialog)   # Ожидаем завершения диалога иначе код пойдет дальше не дождавшись выбора значения

    def view_stat_row_popup(self, values: tuple) -> None:
        """
        Окно просмотра отчёта статистики с детализацией

        :param values: кортеж данных из выделенной строки таблицы формата:
                        ('1', '2025-01-21 22:43:09', '4', '4', '100.0 %', 'Attack on Titans', '2', 'en -> ru: word')
        :return: None
        """
        dialog = tk.Toplevel(self.master)                                           # Общие параметры окна
        dialog.title(f'Просмотр записи статистики')
        dialog.geometry('760x415+100+100')
        dialog.transient(self.master)
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        bg = styles.STYLE_COLORS[self.master.current_color_style]['background']
        text_paddings = (10, 5)                                                     # Отступы строк отчёта

        # Настройка контейнера с общей информацией отчёта
        container = tk.Frame(dialog, background=bg)
        container.grid(row=0, column=0, sticky='nswe')
        container_with_labels = tk.Frame(container, bg=bg)
        container_with_labels.grid(row=0, column=0, sticky='nswe', pady=(10, 15), padx=60)
        container_with_labels.grid_columnconfigure(0, minsize=100)
        container_with_labels.grid_columnconfigure(1, minsize=260)
        container_with_labels.grid_columnconfigure(2, minsize=170)
        container_with_labels.grid_columnconfigure(3, minsize=100)

        # Верхний блок с общей информацией об отчёте
        label = ttk.Label(container_with_labels, text='ID отчёта: ', style='AddRowLbl.TLabel', padding=text_paddings)
        label.grid(row=0, column=0, sticky='e')
        label = ttk.Label(container_with_labels, text=values[0], style='Base.TLabel', padding=text_paddings)
        label.grid(row=0, column=1, sticky='w')

        label = ttk.Label(container_with_labels, text='Дата: ', style='AddRowLbl.TLabel', padding=text_paddings)
        label.grid(row=1, column=0, sticky='e')
        label = ttk.Label(container_with_labels, text=values[1], style='Base.TLabel', padding=text_paddings)
        label.grid(row=1, column=1, sticky='w')

        label = ttk.Label(container_with_labels, text='Тип теста: ', style='AddRowLbl.TLabel', padding=text_paddings)
        label.grid(row=2, column=0, sticky='e')
        label = ttk.Label(container_with_labels, text=values[7], style='Base.TLabel', padding=text_paddings)
        label.grid(row=2, column=1, sticky='w')

        label = ttk.Label(container_with_labels, text='Лист: ', style='AddRowLbl.TLabel', padding=text_paddings)
        label.grid(row=3, column=0, sticky='e')
        label = ttk.Label(container_with_labels, text=values[5], style='Base.TLabel', padding=text_paddings)
        label.grid(row=3, column=1, sticky='w')

        color_style = get_percent_style(float(values[4].split(' ')[0]))
        label = ttk.Label(container_with_labels, text='Результат: ', style='AddRowLbl.TLabel', padding=text_paddings)
        label.grid(row=0, column=2, sticky='e')
        label = ttk.Label(container_with_labels, text=values[4], style=color_style, padding=text_paddings)
        label.grid(row=0, column=3, sticky='w')

        label = ttk.Label(container_with_labels, text='Верно: ', style='AddRowLbl.TLabel', padding=text_paddings)
        label.grid(row=1, column=2, sticky='e')
        label = ttk.Label(container_with_labels, text=values[2], style='Base.TLabel', padding=text_paddings)
        label.grid(row=1, column=3, sticky='w')

        label = ttk.Label(container_with_labels, text='Всего попыток: ', style='AddRowLbl.TLabel', padding=text_paddings)
        label.grid(row=2, column=2, sticky='e')
        label = ttk.Label(container_with_labels, text=values[3], style='Base.TLabel', padding=text_paddings)
        label.grid(row=2, column=3, sticky='w')

        label = ttk.Label(container_with_labels, text='Всего слов: ', style='AddRowLbl.TLabel', padding=text_paddings)
        label.grid(row=3, column=2, sticky='e')
        label = ttk.Label(container_with_labels, text=values[6], style='Base.TLabel', padding=text_paddings)
        label.grid(row=3, column=3, sticky='w')

        # Настройка контейнера с таблицей детализации попыток
        table_container = tk.Frame(container, bg='white', height=220)
        table_container.grid(row=1, column=0, sticky='we', padx=(5, 190))

        # Таблица детализации попыток
        tree = ttk.Treeview(table_container, show='headings')
        headers = settings.TBL_STAT_ATTEMPTS_DETAIL_HEADERS
        tree['columns'] = list(headers.keys())
        for header, width in headers.items():
            tree.heading(header, text=header, anchor='center')
            tree.column(header, anchor='center', width=width)

        scroll_panel = ttk.Scrollbar(table_container, command=tree.yview)           # Прокрутка отчёта попыток
        scroll_panel.pack(side='right', fill=tk.Y)
        tree.configure(yscrollcommand=scroll_panel.set)
        tree.pack(side='left', fill='both')

        # Загрузить данные о попытках
        data = []
        if self.master.data_type == 'Excel':
            data = self.master.excel_get_attempts_by_report_id(int(values[0]))
        elif self.master.data_type == 'База':
            data = self.master.db.get_attempts_by_report_id(int(values[0]))

        for row in data:
            tree.insert('', tk.END, values=row)                                     # Заполнение таблицы

        # Кнопки
        btn_container = tk.Frame(container, bg=bg)                                  # Кнопка выхода
        btn_container.grid(row=2, column=0, sticky='e', pady=(5, 0), padx=5)
        btn_submit = ttk.Button(btn_container, text='Закрыть', command=dialog.destroy, style='AddRow.TButton')
        btn_submit.grid(row=0, column=0, sticky='se', padx=201)

        dialog.wait_window()

    def on_click_Excel(self, dialog: tk.Toplevel) -> None:
        """ Обработчик кнопки выбора Excel"""
        self.result = 'Excel'
        dialog.destroy()

    def on_click_DB(self, dialog: tk.Toplevel) -> None:
        """ Обработчик кнопки выбора БД"""
        self.result = 'База'
        dialog.destroy()

    def validate_self_word(self) -> bool:
        """ Валидация введённого слова/фразы """
        if not self.word:
            mbox.showerror('', 'Необходимо указать Слово/Фразу')
            self.flag_error_word = True
            return False
        if len(self.word) < 2:
            mbox.showerror('', 'Слово/Фраза должны содержать не менее 2х символов')
            self.flag_error_word = True
            return False
        return True

    def validate_sheet_name(self) -> bool:
        """ Валидация названия листа Excel """

        if self.master.data_type == 'Excel':
            self.actual_sheets_or_themes = self.master.excel_get_list_all_sheets()
        elif self.master.data_type == 'База':
            self.actual_sheets_or_themes = self.master.db.get_list_all_themes()

        if self.new_sheet_name in self.actual_sheets_or_themes:
            mbox.showerror('Ошибка', 'Лист с таким названием уже существует.\nУкажите другое название листа.')
            return False
        if not self.new_sheet_name:
            mbox.showerror('Ошибка', 'Необходимо указать название листа')
            return False
        elif len(self.new_sheet_name) < 3:
            mbox.showerror('Ошибка', 'Название листа должно содержать не менее 3х символов')
            return False
        return True

    def clear_self_atributes(self) -> None:
        """ Сброс данных формы ввода, записанных в self """

        self.choosen_sheet_cmbbx = None
        self.word = None
        self.transcript = None
        self.translate = None
        self.context = None

        self.given_choosen_sheet_cmbbx = None
        self.given_row_id = None
        self.given_word = None
        self.given_context = None
        self.given_translate = None
        self.given_transcript = None

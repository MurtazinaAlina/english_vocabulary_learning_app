import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import settings
import styles
from Utils.auxiliary_tools import open_url


class MainMenuBTN:
    """ Главное меню наверху приложения """

    def __init__(self, parent):
        self.parent = parent

        # Активно только при выбранной книге Excel
        self.state_is_wb = tk.DISABLED if self.parent.wb is None else tk.ACTIVE

        # Активно только при подключенной БД SQL
        self.state_is_db = tk.DISABLED if self.parent.db.engine is None else tk.ACTIVE

        # Активно при подключении любого из видов базы
        self.is_any_db = tk.ACTIVE if (self.parent.wb or self.parent.db.engine) else tk.DISABLED

        self.put_menu()                                                 # Сборка меню

    def put_menu(self):
        """ Сборка меню """

        # Контейнер для меню
        container_menu = tk.Frame(self.parent,
                                  background=styles.STYLE_COLORS[self.parent.current_color_style][
                                      'menu_btn_color_others'])
        container_menu.grid(row=0, column=0, sticky='we')

        # Перегрузка стиля меню под пользовательскую цветовую тему
        menu_cascade_settings = styles.MENU_CASCADE_VIEW
        menu_cascade_settings['activebackground'] = styles.STYLE_COLORS[self.parent.current_color_style][
            'menu_active_bg_color']
        menu_cascade_settings['activeforeground'] = styles.STYLE_COLORS[self.parent.current_color_style][
            'menu_active_fg_color']

        # Кнопка МЕНЮ
        image = Image.open(settings.ICON_MENU['path'])                 # Иконка для кнопки
        image = image.resize((17, 17))
        icon = ImageTk.PhotoImage(image)
        menubtn = ttk.Menubutton(container_menu, image=icon, text='Меню', compound=tk.LEFT, direction='below',
                                 style='MENU.TMenubutton')
        menubtn.image = icon
        menubtn.pack(anchor='nw', side='left')

        menu = tk.Menu(menubtn, tearoff=0, **menu_cascade_settings)     # Выпадающее меню с окнами приложения
        menubtn.configure(menu=menu)                                    # Размещаме его в кнопке МЕНЮ
        for k, v in settings.APP_WINDOWS.items():                       # МЕНЮ, автозаполнение
            menu.add_command(label=v['label'], command=lambda k=k: self.parent.choose_window(win_type=k))

        # Кнопка ФАЙЛ
        menu_btn_file = ttk.Menubutton(container_menu, text='Файл', direction='below', style='Others.TMenubutton')
        menu_btn_file.pack(anchor='nw', side='left')
        file_menu = tk.Menu(menu_btn_file, tearoff=0, **menu_cascade_settings)
        menu_btn_file.configure(menu=file_menu)

        # ФАЙЛ - вложенное меню с выбором типа базы
        choose_db_type = tk.Menu(file_menu, tearoff=0, **menu_cascade_settings)
        self.data_type_var = tk.StringVar()
        self.data_type_var.set(self.parent.data_type)
        choose_db_type.add_radiobutton(label='Файл Excel', variable=self.data_type_var, value='Excel',
                                       command=lambda: self.parent.handler_select_data_type(self.data_type_var.get()))
        choose_db_type.add_radiobutton(label='База данных', variable=self.data_type_var, value='База',
                                       command=lambda: self.parent.handler_select_data_type(self.data_type_var.get()))

        # ФАЙЛ - наполнение выпадающего меню
        file_menu.add_command(label='Открыть книгу Excel', command=self.parent.handler_select_file_wb)
        file_menu.add_command(label='Сохранить книгу Excel как', command=self.parent.handler_excel_save_as,
                              state=self.state_is_wb)
        file_menu.add_command(label='Посмотреть выбранную книгу Excel',
                              command=lambda: self.parent.popup.show_popup('show_wb'), state=self.state_is_wb)
        file_menu.add_command(label='Создать новую книгу Excel со структурой базы',
                              command=self.parent.handler_create_new_excel_structure)
        file_menu.add_separator()

        file_menu.add_command(label='Подключиться к БД', command=self.parent.handler_select_file_sql_db)
        file_menu.add_command(label='Сохранить БД как', command=self.parent.db.save_db_as, state=self.state_is_db)
        file_menu.add_command(label='Создать новую БД со структурой базы', command=self.parent.db.create_db)
        file_menu.add_separator()
        file_menu.add_cascade(label='Изменить тип базы', menu=choose_db_type)
        file_menu.add_separator()
        file_menu.add_command(label='Обновить окно', command=self.parent.refresh)
        file_menu.add_command(label='Перезагрузить приложение',
                              command=lambda: self.parent.popup.show_popup('reset_confirmation'))
        file_menu.add_separator()
        file_menu.add_command(label='Выход', command=lambda: self.parent.popup.show_popup('exit_confirmation'))

        # Кнопка ДАННЫЕ
        menu_btn_data = ttk.Menubutton(container_menu, text='Данные', direction='below', style='Others.TMenubutton')
        menu_btn_data.pack(anchor='nw', side='left')
        data_menu = tk.Menu(menu_btn_data, tearoff=0, **menu_cascade_settings)
        menu_btn_data.configure(menu=data_menu)

        # ДАННЫЕ - наполнение выпадающего меню
        data_menu.add_command(label='Добавить новый лист в книгу Excel', state=self.state_is_wb,
                              command=lambda: self.parent.popup.show_popup('add_new_sheet_popup'))
        data_menu.add_separator()
        data_menu.add_command(label='Добавить новый раздел в БД', state=self.state_is_db,
                              command=lambda: self.parent.popup.show_popup('add_new_sheet_popup'))
        data_menu.add_command(label='Обновить данные таблиц БД',state=self.state_is_db,
                              command=self.parent.db.refresh_db_after_new_tables)
        data_menu.add_command(label='Загрузить данные из Excel в БД', state=self.state_is_db,
                              command=lambda: self.parent.popup.loading_excel_data_to_db_popup())
        data_menu.add_separator()
        data_menu.add_command(label='Добавить запись', state=self.is_any_db,
                              command=lambda: self.parent.popup.show_popup('add_row'))

        # Кнопка РЕЧЬ
        menu_btn_say = ttk.Menubutton(container_menu, text='Речь', direction='below', style='Others.TMenubutton')
        menu_btn_say.pack(anchor='nw', side='left')
        say_menu = tk.Menu(menu_btn_say, tearoff=0, **menu_cascade_settings)
        menu_btn_say.configure(menu=say_menu)

        icn = '⚙'
        say_menu.add_command(label=f'{icn} Настройки речи',
                             command=lambda: self.parent.popup.show_popup('settings_speech_popup'))

        # Кнопка ВИД
        menu_btn_view = ttk.Menubutton(container_menu, text='Вид', direction='below', style='Others.TMenubutton')
        menu_btn_view.pack(anchor='nw', side='left')
        view_menu = tk.Menu(menu_btn_view, tearoff=0, **menu_cascade_settings)
        menu_btn_view.configure(menu=view_menu)

        # ВИД - вложенное каскадное меню с выбором цветовой темы
        choose_color_theme = tk.Menu(file_menu, tearoff=0, **menu_cascade_settings)
        self.color_var = tk.StringVar()
        self.color_var.set(self.parent.current_color_style)
        for k, v in styles.STYLE_COLORS.items():
            choose_color_theme.add_radiobutton(label=v['title'], variable=self.color_var, value=k,
                                               command=lambda: self.parent.choose_color_theme(self.color_var.get()))
        view_menu.add_cascade(label='Выберите цветовой стиль оформления', menu=choose_color_theme)

        # ССЫЛКИ - меню с переходами в браузер на страницы онлайн-переводчиков и нейросетей
        menu_btn_links = ttk.Menubutton(container_menu, text='Ссылки', direction='below', style='Others.TMenubutton')
        menu_btn_links.pack(anchor='nw', side='left')
        links_menu = tk.Menu(menu_btn_view, tearoff=0, **menu_cascade_settings)
        menu_btn_links.configure(menu=links_menu)

        links_menu.add_command(label='Reverso Context', command=lambda: open_url(settings.REVERSO_CONTEXT_BASE_URL_RU))
        links_menu.add_command(label='Google Translator', command=lambda: open_url(settings.GOOGLE_TRANSLATOR))
        links_menu.add_command(label='Спросить у ChatGPT.ru', command=lambda: open_url(settings.GPT_RU_URL))

        # Иконка ОБНОВИТЬ в правом верхнем углу - из родителя
        icon_refresh = self.parent.put_icon_refresh(widget=self, container=container_menu)
        icon_refresh.config(bg=styles.STYLE_COLORS[self.parent.current_color_style]['menu_btn_color_others'])
        icon_refresh.pack(anchor='e', side='right', padx=6)

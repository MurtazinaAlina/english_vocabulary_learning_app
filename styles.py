"""
Настройки стилей и цветов
"""


# Основные шрифты и цвета
FONT_MAIN_TEXT = 'cambria'                                          # Основной текст
FONT_SYSTEM_TEXT = 'Segoe UI'                                       # Системный шрифт
FONT_HEADER_H1 = 'georgia'                                          # Заголовки h1
GREEN_RED_GREY_FORMAT_STYLE = ['#228709', '#920e0e', '#2d2d2d']
LIGHTGRAY_SYSTEM = '#f0f0f0'                                        # Системный серый фон
DARK_BLUE_FG_MAIN = '#064681'                                       # Тёмно-голубой цвет шрифта основной

EVENT_HOVER_CURSOR_TABLE = '#d6ebfc'                                # Выделение при наведении курсора - для таблиц, цвет
EVENT_HOVER_OFF_CURSOR_TABLE = 'white'                              # Выделение при уходе курсора - для таблиц, цвет
EVENT_SELECTED_CURSOR_TABLE = '#addaff'                             # Выделение при выборе объекта - для таблиц, цвет


# Основные цветовые стили оформления приложения
STYLE_COLORS = {
    'lav': {
        'title': 'Лавандовый',
        'background': '#f9f9fe',        # f4f4fd
        'foreground_main': '#064681',
        'cnvs_headers_bg': LIGHTGRAY_SYSTEM,
        'menu_btn_color_main': '#7875b9',
        'menu_btn_color_others': '#e6e6f5',
        'menu_active_bg_color': '#b6b6da',   # d0d0d0
        'menu_active_fg_color': 'black',
        'pagi_on_hover_bg': '#b6b6da'
    },
    'l_orange_2': {
        'title': 'Светлый тёплый',
        'background': '#fcf5ed',
        'foreground_main': '#064681',
        'cnvs_headers_bg': '#efeae5',
        'menu_btn_color_main': '#757575',
        'menu_btn_color_others': '#d9d1ca',
        'menu_active_bg_color': '#757575',
        'menu_active_fg_color': 'white',
        'pagi_on_hover_bg': '#c4b5a8'
    },
    'l_orange': {
        'title': 'Песочный',
        'background': '#fcf2e8',
        'foreground_main': '#064681',
        'cnvs_headers_bg': '#efeae5',
        'menu_btn_color_main': '#837a73',
        'menu_btn_color_others': '#d0c5bb',
        'menu_active_bg_color': '#837a73',
        'menu_active_fg_color': 'white',
        'pagi_on_hover_bg': '#c4b5a8'
    },
    'emer': {
        'title': 'Светло-изумрудный',
        'background': '#ecf5f3',
        'foreground_main': '#052747',
        'cnvs_headers_bg': 'white',
        'menu_btn_color_main': '#009070',
        'menu_btn_color_others': '#dbeeea',
        'menu_active_bg_color': '#009070',
        'menu_active_fg_color': 'white',
        'pagi_on_hover_bg': '#70b7a7'
    },
    'l_gr': {
        'title': 'Светлый холодный',
        'background': '#f9fcff',
        'foreground_main': '#064681',
        'cnvs_headers_bg': LIGHTGRAY_SYSTEM,
        'menu_btn_color_main': '#4577af',
        'menu_btn_color_others': '#e6eef7',
        'menu_active_bg_color': '#4577af',
        'menu_active_fg_color': 'white',
        'pagi_on_hover_bg': '#7a9cc4'
    },
}

# Флаги для динамичного выбора foreground при инициализации стиля
FLAG_SET_FG_STYLE_COLOR_MAIN = 'FLAG_style_color_main_fg'           # Основной цвет шрифта темы
FLAG_SET_MENU_BTN_COLOR = 'FLAG_style_color_menu_btn'               # Цвет основной кнопки меню
FLAG_SET_MENU_OTHER_BTNS_COLOR = 'FLAG_style_color_menu_other_btn'  # Цвет остальных кнопок меню
FLAG_SET_MENU_ACTIVE_BG_COLOR = 'Flag'                              # Цвет фона выбранного пункта в меню
FLAG_SET_MENU_ACTIVE_FG_COLOR = 'Flag'                              # Цвет шрифта выбранного пункта в меню


# Настройки стилей
STYLES_INIT = {

    # Лейблы
    'StatGreen.TLabel': {                                           # блок статистика - зелёный текст
        'foreground': GREEN_RED_GREY_FORMAT_STYLE[0]
    },
    'StatRed.TLabel': {
        'foreground': GREEN_RED_GREY_FORMAT_STYLE[1]                # блок статистика - красный текст
    },
    'StatGrey.TLabel': {                                            # блок статистика - базовые лейблы
        'foreground': GREEN_RED_GREY_FORMAT_STYLE[2],
        'padding': (20, 20, 20, 20),
        'font': (FONT_MAIN_TEXT, 11)
    },
    'HeadLbl.TLabel': {                                             # Заголовки универс ~h1
        'foreground': GREEN_RED_GREY_FORMAT_STYLE[2],
        'padding': (20, 20, 20, 20),
        'font': (FONT_HEADER_H1, 13, 'italic bold')
    },
    'BlItGrey.TLabel': {                                            # Подзаголовки - универс ~h2, темно-серый
        'foreground': GREEN_RED_GREY_FORMAT_STYLE[2],
        'padding': (20, 20, 20, 20),
        'font': (FONT_MAIN_TEXT, 12, 'italic bold')
    },
    'BlIt.TLabel': {                                                # Подзаголовки - универс ~h2
        'padding': (20, 20, 20, 20),
        'font': (FONT_MAIN_TEXT, 12, 'italic bold')
    },
    'Base.TLabel': {                                                # Базовый стиль, кроме DateEntry
        'padding': (20, 20, 20, 20),
        'font': (FONT_MAIN_TEXT, 11)
    },
    'TLabel': {                                                     # Под DateEntry виджет
    },
    'Cell.TLabel': {                                                # Ячейка с текстом - белый
        'background': 'white',
        'relief': 'solid',
        'borderwidth': 2,
        'padding': 5,
        'font': (FONT_MAIN_TEXT, 11)
    },
    'Context.TLabel': {                                             # Контекст - отображение
        'padding': (20, 10, 20, 10),
        'font': (FONT_MAIN_TEXT, 12, 'italic'),
        'foreground': FLAG_SET_FG_STYLE_COLOR_MAIN,
        'background': 'white',
        'wraplength': 580  # wraplength - для автопереноса при превышении длины строки
    },
    'Answers.TLabel': {                                             # Транскрипция и перевод
        'padding': (20, 20, 20, 20),
        'font': (FONT_MAIN_TEXT, 11),
        'foreground': FLAG_SET_FG_STYLE_COLOR_MAIN,
        'wraplength': 450
    },
    'Headers.TLabel': {                                             # Headers Label - в Canvas
        'background': '#f7f7f7',
        'height': 30,
        'font': (FONT_MAIN_TEXT, 11, 'bold'),
        'foreground': GREEN_RED_GREY_FORMAT_STYLE[2],
        'padding': (0, 5, 0, 5),
        # 'borderwidth': 1,
        # 'relief': 'solid'
    },
    'MsgLbl.TLabel': {                                              # Текст в системках
        'font': (FONT_SYSTEM_TEXT, 10),
        'background': 'white'     # f7f7f7
    },
    'MsgLblChoose.TLabel': {                                        # Cистемка c 1 строкой и кнопкой рядом
        'font': (FONT_SYSTEM_TEXT, 10),
        'padding' : (10, 40),                                       # Центрирование по стандартной высоте системки
        'background': 'white'
    },
    'AddRowLbl.TLabel': {                                           # Контекст - отображение
        'padding': (10, 8),
        'font': (FONT_MAIN_TEXT, 11, 'italic bold'),
        'foreground': FLAG_SET_FG_STYLE_COLOR_MAIN,
    },
    'ChooseFile.TLabel': {                                          # Мелкая подпись y выбора файла
        'padding': (5, 0),
        'font': (FONT_SYSTEM_TEXT, 8),
        'foreground': GREEN_RED_GREY_FORMAT_STYLE[1],
    },

    # Контейнеры
    'TFrame': {},                                                   # Перегрузка контейнеров, фон

    # Объекты Treeview
    'Treeview.Heading': {                                           # Headers Treeview
        'background': 'lightgray',
        'height': 30,
        'font': (FONT_MAIN_TEXT, 11, 'bold')
    },

    # Кнопки
    'TCheckbutton': {                                               # Лейбл с текстом к чек-боксу, перегрузка
        'relief': 'flat',
    },
    'Red.TCheckbutton': {                                           # Красный лейбл к чек-боксу
        'relief': 'flat',
        'foreground': GREEN_RED_GREY_FORMAT_STYLE[1]
    },
    'TRadiobutton': {                                               # Лейбл с текстом к radio, перегрузка
        'relief': 'flat',
    },
    'TButton': {                                                    # Перегрузка кнопки
        'relief': 'raised',
    },
    'h2.TButton': {                                                 # Кнопки под размер лейбла h2: Далее, Записать ...
        'relief': 'raised',
        'padding': (10, 5),
    },
    'Yes.TButton': {                                                # Кнопка ДА
        'relief': 'raised',
        'padding': (-7, 0, -2, 0)
    },
    'No.TButton': {                                                 # Кнопка НЕТ
        'relief': 'raised',
        'padding': (-7, 0, -2, 0)
    },
    'List.TButton': {                                               # Кнопка ВЫБОР ЛИСТА под Combobox
        'relief': 'raised',
        'foreground': FLAG_SET_FG_STYLE_COLOR_MAIN,
        'padding': (5, 0, 5, 0)
    },
    'EditList.TButton': {                                           # Кнопка РЕДАКТИРОВАТЬ ЛИСТ
        'relief': 'raised',
        'foreground': '#580f0f',
        'padding': (5, 0, 5, 0),
},
    'Popup.TButton': {                                              # Кнопки выбора в системках голубой кант
        'relief': 'raised',
        'foreground': 'black',
        'padding': (5, 0, 5, 0),
        'background': '#008cff',  # 26adf6
    },
    'AddRow.TButton': {                                             # Кнопка "Записать", предвыбранная синий кант
        'background': '#008cff'
    },
    'ChngFile.TButton': {                                           # Кнопка "Изменить файл" малая
        'background': GREEN_RED_GREY_FORMAT_STYLE[2],
        'font': (FONT_SYSTEM_TEXT, 8)
    },
    'Edit.TButton': {                                               # Кнопка "Редактировать" в Canvas
        'relief': 'raised',
        'foreground': FLAG_SET_FG_STYLE_COLOR_MAIN
    },
    'MENU.TMenubutton': {                                           # Кнопка МЕНЮ
        'background': FLAG_SET_MENU_BTN_COLOR,
        'foreground': LIGHTGRAY_SYSTEM,
        'padding': (0, 5),
        'width': 8,
        'anchor': 'center',
        'font': (FONT_SYSTEM_TEXT, 10, 'bold'),
        'relief': 'raised',
    },
    'Others.TMenubutton': {                                         # Остальные кнопки меню
        'background': FLAG_SET_MENU_OTHER_BTNS_COLOR,
        'padding': (5, 5),
        'width': 10,
        'font': (FONT_SYSTEM_TEXT, 10),
        'relief': 'raised',
        'height': 8,
        'anchor': 'center',
        'borderwidth': 4,
    },

    # Scale
    "Custom.Horizontal.TScale" : {                                  # Scale речевого синтеза
        # 'background': self.bg,  # Цвет самого ползунка
        'sliderlength': 100  # Размер ползунка
    },
}

# Стили для меню
MENU_CASCADE_VIEW = {                                               # Выпадающее меню
    'bg': LIGHTGRAY_SYSTEM,
    'activebackground': FLAG_SET_MENU_ACTIVE_BG_COLOR,
    'activeforeground': FLAG_SET_MENU_ACTIVE_FG_COLOR
}

# Стили для Canvas
CANVAS_TABLE_TEXT = {                                               # Данные в таблице Canvas - все данные листа
    'font': (FONT_MAIN_TEXT, 11),
}
CANVAS_HEADERS = {                                                  # Headers - в Canvas
        'font': (FONT_MAIN_TEXT, 11, 'bold'),
    }
CANVAS_TABLE_BORDER_DASH_GRAY = {                                   # Стиль пунктирной границы в Canvas
    'outline': 'lightgray',
    'dash': (1, 3)
}

# Стили для PopUp
TOP_LVL_MSG_STANDART_GEOMETRY = '220x122+300+300'                   # Геометрия окна стандартной системки
TOP_LVL_MSG_STANDART_CONTAINER = {
    'width': 220,
    # 'height': 140,
    # 'background': STYLES_INIT['MsgLbl.TLabel']['background']
}

# Стили для DateEntry
DATE_ENTRY_WIDGET = {
    'date_pattern': "yyyy-mm-dd",
    'foreground':'black',
    'normalforeground':'black',
    'selectforeground':'blue',
    'background':'white'
}

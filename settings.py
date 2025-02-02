"""
Настройки для работы приложения
"""


# Основные настройки приложения

# Режим автозагрузки тестового Excel файла
AUTOLOAD_EXCEL: bool = False                                                            # Отладка, автозагрузка книги
FILE_PATH_DEFAULT = 'C:\\Users\\Alynx\\Desktop\\Eng_vocab22.xlsx'                       # Файл автозагрузки

# Рабочие окна приложения.
# При добавлении нового окна необходимо прописать в App метод соответствующий 'app_func' + инициализируемый в нем класс
APP_WINDOWS = {
    'start': {'app_func': 'setup_en_ru_window', 'label': 'en -> ru: word'},             # 'label' - название окна в меню
    'ru_en': {'app_func': 'setup_ru_en_window', 'label': 'ru -> en: word'},
    'audio_en_ru': {'app_func': 'setup_en_ru_audio_window', 'label': 'en -> ru: audio'},
    'stat': {'app_func': 'setup_stat_window', 'label': 'Статистика'},
    'data': {'app_func': 'setup_data_window', 'label': 'Посмотреть все данные'}
}
APP_START_WINDOW = 'start'                                      # Окно при запуске - по ключу из APP_WINDOWS
APP_TITLE = 'Мой помощник в изучении английского'               # Отображаемое название

# путь к файлу .argosmodel для инициализации переводчика
ARGOSMODEL_PATH = 'Utils/translate-en_ru-1_9.argosmodel'

# Ссылки:

# URL адрес Reverso - базовый
REVERSO_CONTEXT_BASE_URL = 'https://context.reverso.net/translation/english-russian/'
# URL адрес Reverso - базовый для работы в РФ
REVERSO_CONTEXT_BASE_URL_RU = 'https://context.reverso.net/перевод/английский-русский/'
# URL адрес Google Translator
GOOGLE_TRANSLATOR = 'https://www.google.com/search?q=переводчик&oq=gtht&aqs=chrome.1.69i57j0i1i10i512j69i59j0i1i10i131i433i512l2j46i1i10i199i465i512j0i1i10i512l4.1710j0j7&sourceid=chrome&ie=UTF-8'
# GPT ru для вопросов
GPT_RU_URL = 'https://trychatgpt.ru/'
# GPT official для вопросов
GPT_URL = 'https://chatgpt.com/'

# Типы тестирования
TEST_TYPES = [
    'en -> ru: word',
    'ru -> en: word',
    'en -> ru: audio',
]

# Настройки визуализации
DEFAULT_COLOR_THEME = 'lav'                                     # Цветовая тема по умолчанию из styles.py
DEFAULT_WINDOW_GEOMETRY = '1405x700+50+50'                      # Размер окна + положение по умолчанию
DEFAULT_WINDOW_MINSIZE = (900, 450)

STAT_COLOR_MATCH = {                                # Настройка статистики: соответствие цветового выделения и порогов
            90: 'StatRed.TLabel',                   # от 0 до key
            95: 'StatGrey.TLabel',
            101: 'StatGreen.TLabel'
        }

# Настройки сортировки листов   [False, 'Ascending', 'Descending']
SORTING_SHEETS = {
    False: 'A-Z',                               # key= тип сортировки, value= подсказка для СЛЕДУЮЩЕЙ (!!!) сортировки
    'Ascending': 'Z-A',
    'Descending': 'Без сортировки'
}

# Настройки работы с Excel
EXCEL_UTILS_SHEETS = ['Свод', 'Utils', 'Stat', 'Attempts']      # вспомогательные листы - не исп-ть для выбора слова
EXCEL_STAT_LIST = 'Stat'                                        # лист со статистикой - для вывода в окне 'stat'
EXCEL_ATTEMPTS = 'Attempts'                                     # История попыток

EXCEL_INDEX_FIRST_ROW_WITH_DATA = 6                             # Индекс 1й строки с данными (у меня 6)
EXCEL_AUTOINDEX_LIMIT = 10000                                   # MAX значение автоматической индексации записей
EXCEL_KEY_COLUMN = [2]                                          # ключевая колонка для подсчёта строк B
EXCEL_DATA_COLUMNS = [1, 5]                                     # колонки с данными 1-5
EXCEL_KEY_CELL= f'B{EXCEL_INDEX_FIRST_ROW_WITH_DATA}'        # Ключевая ячейка для определения наличия записей на листе
EXCEL_WORD_SHEET_FROZEN_RANGE = 'F6'                         # Закрепляем все ячейки до F6, т.е. A1:E5 будут закреплены

EXCEL_SHEET_TAB_COLOR = 'addaff'                                # Цвет ярлычка листа
EXCEL_TEXT_ADD_COLOR = '064681'                                 # Дополнительный цвет шрифта - примеры, заметки
EXCEL_TEXT_TIPS_COLOR = 'dcc217'                                # Цвет подсказок самопроверки
EXCEL_RANGE_BOTTOM_BORDER = 'A5:E5'                             # Диапазон для выделения нижней границей

EXCEL_COLUMNS_WORD_SHEET = {                                # Данные для столбцов листа со словами - заголовки, ширина
    'A': {'header': 'ID', 'width': 8},
    'B': {'header': 'Слово/Фраза', 'width': 30},
    'C': {'header': 'Транскрипция', 'width': 20},
    'D': {'header': 'Перевод', 'width': 60},
    'E': {'header': 'Примеры использования в контексте', 'width': 80},
}

# Ячейки с формулами для самопроверки
RAND_TIP = ['B3', 'Случайно выбранное слово']               # Ячейка + записываемое значение
RAND_INDEX = 'A4'
RAND_WORD = 'B4'
RAND_WORD_TRANSCR = 'C4'
RAND_WORD_TRANSL = 'D4'
RAND_WORD_CONTEXT = 'E4'

# Формулы
formula_rand_index = f'=RANDBETWEEN(1, COUNTA(B{EXCEL_INDEX_FIRST_ROW_WITH_DATA}:B{EXCEL_AUTOINDEX_LIMIT}))'
formula_rand_word = f'=VLOOKUP({RAND_INDEX}, A{EXCEL_INDEX_FIRST_ROW_WITH_DATA}:D{EXCEL_AUTOINDEX_LIMIT}, 2, FALSE)'
formula_rand_transcr = f'=VLOOKUP({RAND_INDEX}, A{EXCEL_INDEX_FIRST_ROW_WITH_DATA}:D{EXCEL_AUTOINDEX_LIMIT}, 3, FALSE)'
formula_rand_transl = f'=VLOOKUP({RAND_INDEX}, A{EXCEL_INDEX_FIRST_ROW_WITH_DATA}:D{EXCEL_AUTOINDEX_LIMIT}, 4, FALSE)'
formula_rand_context = f'=VLOOKUP({RAND_INDEX}, A{EXCEL_INDEX_FIRST_ROW_WITH_DATA}:E{EXCEL_AUTOINDEX_LIMIT}, 5, FALSE)'

EXCEL_COLUMNS_STAT_SHEET = {                            # Данные для столбцов листа со статистикой - заголовки, ширина
    'A': {'header': 'Дата', 'width': 20},
    'B': {'header': 'Верно', 'width': 10},
    'C': {'header': 'Попыток', 'width': 10},
    'D': {'header': '%', 'width': 10},
    'E': {'header': 'Тема', 'width': 20},
    'F': {'header': 'Всего слов', 'width': 15},
    'G': {'header': 'ID отчёта', 'width': 15},
    'H': {'header': 'Тип теста', 'width': 15},
}

EXCEL_COLUMNS_ATTEMPTS_SHEET = {                            # Данные для столбцов листа с попытками - заголовки, ширина
    'A': {'header': 'ID', 'width': 10},
    'B': {'header': 'datetime', 'width': 20},
    'C': {'header': 'word', 'width': 30},
    'D': {'header': 'result', 'width': 15},
    'E': {'header': 'report_id', 'width': 15},
    'F': {'header': 'test_type', 'width': 15}
}

# Настройки для отрисовки таблицы с отображением данных в Canvas в data_window.py
COLUMN_WIDTH = {                                                # Фиксация ширины столбцов
                'ID': 45,
                'Word/Phrase': 250,
                'Transcription': 175,
                'Translate': 380,
                'Instances': 450,
                'Edit': 50
            }
CNV_ROW_HEIGH = {                                               # строк - высота px для ТЕКУЩЕГО шрифта таблицы!
    0: 40, 1: 40, 2: 55, 3: 70, 4: 85, 5: 100, 6: 120, 7: 135, 8: 145, 9: 160, 10: 185, 11: 200
}
CNV_COLUMN_SYMB_LIMIT = {4: 61, 3: 45, 1: 27, 2: 20}            # лимит для ТЕКУЩЕГО шрифта таблицы!
CNV_COLUMNS_MULTILINE_TEXT = [1, 2, 3, 4]         # Колонки для проверки на разбивку по строкам для опр-я высоты строки

# Настройки для статистики
TBL_STAT_HEADERS = [                                            # Заголовки столбцов таблицы отчётов
    'ID', 'Дата', 'Верно', 'Всего', '%', 'Лист', 'Всего слов', 'Тип теста'
]
TBL_STAT_ATTEMPTS_DETAIL_HEADERS = {            # Заголовки + ширина столбца в детализации попыток в отчёте статистики
    'ID': 102, 'Date': 162, 'Word': 302, 'Result': 162
}

# Используемые иконки
ICON_ADD_DATA = {
    'path': 'images/green_plus_circle_icon.png',
    'color': (0, 144, 112, 128),    # зелёный полупрозрачный
    'bg_active': 'white',
    'indent_tooltip': 530
}
ICON_EDIT_SHEET = {
    'path': 'images/edit.png',
    'color': (0, 0, 0, 128),    # gray полупрозрачный
    'bg_active': 'white',
    'indent_tooltip': 540
}
ICON_DELETE_SHEET = {
    'path': 'images/trash_2_icon.png',
    'color': (0, 0, 0, 128),    # gray полупрозрачный
    'bg_active': 'white',
    'indent_tooltip': 570
}
ICON_ADD_SHEET = {
    'path': 'images/file_plus_icon.png',
    'color': (0, 0, 0, 128),    # gray полупрозрачный
    'bg_active': 'white',
    'indent_tooltip': 530       # отступ подсказки
}
ICON_SORT_SHEETS = {
    'path': 'images/fluent_arrow_sort_filled_icon.png',
    'indent_tooltip': 0 - 160
}
ICON_MENU = {
    'path': 'images/white_menu_navigation_icon.png',
    'indent_tooltip': 0
}
ICON_REFRESH = {
    'path': 'images/refresh_ccw_icon.png',
    'color': (0, 0, 0, 150),    # gray полупрозрачный
    'bg_active': 'white',
    'indent_tooltip': - 105      # отступ подсказки
}
ICON_YES = {
    'path': 'images/check_icon.png'
}
ICON_NO = {
    'path': 'images/x_icon.png'
}
ICON_SEARCH_IN_SHEETS = {
    'path': 'images/search_icon.png',
    'indent_tooltip': 0 - 160
}
ICON_REWIND_BACK = {
    'path': 'images/chevrons_left_icon.png'
}
ICON_NEXT = {
    'path': 'images/chevrons_right_icon.png'
}
ICON_DOWNLOAD = {
    'path': 'images/download_down_save_icon.png'
}
ICON_SOUND = {
    'path': 'images/volume_2_icon.png'
}
ICON_CHROME = {
    'path': 'images/chrome_icon.png'
}

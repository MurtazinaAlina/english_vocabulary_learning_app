"""
Различные вспомогательные функции
"""
import os
import re
import webbrowser

import settings
import styles


def replace_non_breaking_space(some_row: list):
    """ Убрать из строки \xa0 и заменить на обычный пробел"""

    try:
        some_row[4] = some_row[4].replace('\xa0', ' ')
    except AttributeError:
        pass
    return some_row


def replace_none_to_empty_str_in_list(row: list[int | str | None]) -> list[int | str]:
    """
    Форматирование данных списка для исключения ошибок обработки None.
    Заменяет все элементы None на пустую строку ''.

    :param row: список с исходными данными строки:
                [3, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
    :return: тот же список без элементов None
    """
    for index, item in enumerate(row):
        if item is None:                                                # Все элементы None в списке
            row[index] = ' '                                            # Перезаписываем на str = ''
    return row


def context_formatting(some_row: list, indent='\n\n'):
    """ Отформатировать строку с примерами под вывод в контексте.
    Убрать лишние пробелы + каждый пример на новой строке """

    try:
        some_row[4] = [
            i.strip()[0].capitalize() + i.strip()[1:] + indent for i in some_row[4].split('   ') if i.strip() != '']
        some_row[4] = ''.join(some_row[4])
    except AttributeError:
        pass
    return some_row


def counter_row_splitted_by_column_width(some_str: str, limit: int) -> tuple[int, list]:
    """ Подсчет на сколько строк отображения будет разбит текст str при учете переносов строк и ширины столбца """

    splitted_data = some_str.split('\n')                                        # Сплит по пробелам
    splitted_data = list(filter(lambda x: x != '', splitted_data))              # Убираем пустые строки
    if False not in list(map(lambda x: len(x) <= limit, splitted_data)):        # Если все строки меньше лимита
        return len(splitted_data), splitted_data

    result_list = []                                                  # Результирующий список
    for row in splitted_data:
        if len(row) <= limit:
            result_list.append(row)                                   # Если строка меньше лимита, добавляем в результат
        else:
            chunk_string = ''
            words = row.split(' ')
            for ind, el in enumerate(words):                          # Если строка больше лимита
                if len(chunk_string) + len(el) <= limit:              # Если слово "помещается" в лимит
                    chunk_string = chunk_string + el + ' '
                    if ind == len(words) - 1:
                        result_list.append(chunk_string)
                else:
                    result_list.append(chunk_string)                  # Если слово НЕ помещается в лимит
                    chunk_string = ''
                    if ind == len(words) - 1:
                        result_list.append(chunk_string + el)
    return len(result_list), result_list                              # Кол-во строк + список со строками


def calculate_row_high_for_cnvs(some_row: list):
    """ Расчет высоты строки с учетом контента """

    for index, cell in enumerate(some_row):
        if cell is None:
            some_row[index] = ' '                                       # Приводим None -> str
    replace_non_breaking_space(some_row)                                # Сначала убираем пробелы

    column_rows_matching = {}                                           # Кол-во rows в каждом проверяемом столбце
    for indexex in settings.CNV_COLUMNS_MULTILINE_TEXT:
        rows_count, check = counter_row_splitted_by_column_width(some_row[indexex],
                                                                 settings.CNV_COLUMN_SYMB_LIMIT[indexex])
        column_rows_matching[indexex] = rows_count
    hypoth_height = settings.CNV_ROW_HEIGH[max(column_rows_matching.values())]      # Забираем из таблицы соответствий
    return hypoth_height


def toplvl_msg_set_standart_params(dialog, title):
    """ Настройка стандартных параметров Popup системки - растягивание фона, размеры, присвоение тайтла """

    dialog.title(title)
    dialog.geometry(styles.TOP_LVL_MSG_STANDART_GEOMETRY)
    dialog.grid_rowconfigure(0, weight=1)                           # Настроим растяжение элементов в grid
    dialog.grid_columnconfigure(0, weight=1)
    return dialog


def auto_resize_table_columns(table, heads, data):
    """ Настройка ширины столбцов таблицы TreeView в зависимости от содержимого """

    for i, header in enumerate(heads):
        max_length = len(header)                                    # Начинаем с длины заголовка
        for row in data:
            max_length = max(max_length, len(str(row[i])))          # Ищем максимальную длину значения
        table.column(header, width=max_length * 10)                 # Устанавливаем ширину столбца


def get_percent_style(percent, color_match_dict=settings.STAT_COLOR_MATCH) -> str:
    """ Определение стиля % в отображении статистики """

    percent_color = None
    for k, v in color_match_dict.items():
        if percent < k:
            percent_color = v                                           # Style
            break
    return percent_color


def check_autoload_excel_mode(app) -> None:
    """
    Проверка режима автозагрузки книги Excel. При включенном автоматически проставляет тип базы 'Excel' и загружает
    тестовую книгу Excel по заданному в settings пути.
    """
    if settings.AUTOLOAD_EXCEL:
        app.data_type = 'Excel'
        app.excel_path = settings.FILE_PATH_DEFAULT
        app.load_excel(settings.FILE_PATH_DEFAULT)


def process_string(input_string: str) -> str:
    """
    Функция обрабатывает строку со словом/фразой на английском, подготавливая к дальнейшему преобразованию в URL.
    Убирает заметки, раскрывает скобки английских слов, преобразует аббревиатуры.

    :param input_string: str строка со словом/фразой
    :return: str обработанная строка со словом/фразой
    """

    # Удаляем содержимое скобок, если в них есть не английские слова
    input_string = re.sub(r'\(.*?[А-Яа-яЁё].*?\)', '', input_string)

    # Удаляем скобки с содержимым, если внутри есть слово из списка adj, noun, adv
    input_string = re.sub(r'\((.*?(adj|noun|adv).*)\)', '', input_string)

    # Удаляем скобки если английские слова, но не из списка adj, noun, adv
    input_string = re.sub(r'\((?!adj|noun|adv)[a-zA-Z]+\)', lambda match: match.group(0)[1:-1], input_string)

    # Если встречается не английское слово (вне скобок), обрезаем строку до этого места
    input_string = re.sub(r'[А-Яа-яЁё].*', '', input_string)

    # Преобразуем некоторые аббревиатуры
    input_string = re.sub(r'SMTH', 'something', input_string)
    input_string = re.sub(r'SMB', 'somebody', input_string)
    input_string = re.sub(r'smb', 'somebody', input_string)

    return input_string


def open_url(target_url: str) -> None:
    """
    Функция для открытия переданного URL в браузере с приоритетом на Google Chrome

    :param target_url: str URL который необходимо открыть
    """

    # Пытаемся открыть в Google Chrome
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    if os.path.exists(chrome_path):                                         # Проверяем, существует ли путь к Chrome
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get('chrome').open(target_url)
    else:
        webbrowser.open(target_url)                 # Если Chrome не найден, открываем ссылку в стандартном браузере

import tkinter as tk
from tkinter import ttk

import argostranslate.package

from Utils import auxiliary_tools as tls
from Utils.db.database import Database
from Utils.mixins.common_functions import CommonFunctionsMixin
from Utils.navigation_word_history import WordNavigation
from Utils.mixins.common_widgets_n_containers import CommonWidgetsMixin
from Utils.mixins.mixin_excel import ExcelMixin
from Utils.mixins.common_handlers import CommonHandlersMixin
from Utils.mixins.mixin_events import CommonEvents

import settings
import styles
from Utils.speech_synthesis import SpeechSynthesis
from app_windows.ru_en_window import RuEnWindow
from app_windows.data_window import DataWindow
from app_windows.en_ru_window import EnRuWindow
from app_windows.en_ru_audio_window import EnRuAudioWindow
from Utils.custom_widgets.main_menu import MainMenuBTN
from app_windows.popup import Popup
from app_windows.stat_window import StatWindow


class App(tk.Tk,
          ExcelMixin,
          CommonHandlersMixin,
          CommonWidgetsMixin,
          CommonFunctionsMixin,
          CommonEvents):
    """ Основной класс приложения """

    def __init__(self):

        super().__init__()
        ExcelMixin.__init__(self)                       # Инициализация Mixin классов
        CommonHandlersMixin.__init__(self)
        CommonEvents.__init__(self)
        CommonFunctionsMixin.__init__(self)
        CommonWidgetsMixin.__init__(self)

        self.title(settings.APP_TITLE)
        self.minsize(*settings.DEFAULT_WINDOW_MINSIZE)
        self.geometry(settings.DEFAULT_WINDOW_GEOMETRY)
        self.window: str = settings.APP_START_WINDOW        # Название стартового окна приложения при запуске

        argostranslate.package.install_from_path(settings.ARGOSMODEL_PATH)          # Инсталляция модели переводчика

        self.navigation = WordNavigation()                  # Инициализации истории слов для навигации en-ru
        self.navigation_ru_en = WordNavigation()            # Инициализации истории слов для навигации ru-en
        self.navigation_audio = WordNavigation()            # История слов для навигации en-ru AUDIO
        self.engine_speech = SpeechSynthesis()              # Инициализация движка синтеза речи

        self.data_type: str | None = None                   # Название типа базы ('Excel', 'База')
        self.db = Database()                                # Инициализация класса для работы с БД SQL
        self.excel_path: str | None = None                  # Путь к выбранной книге Excel
        # self.wb - Загруженная книга Excel - доступен через родительский класс

        tls.check_autoload_excel_mode(self)                 # Проверка, требуется ли автозагрузка тестового Excel

        self.style = ttk.Style()                                        # Инициализация стиля
        self.current_color_style = settings.DEFAULT_COLOR_THEME         # Стиль по умолчанию

        # Сохранение в переменные результатов из окон приложения (для сохранения при переинициализации)

        # Общие
        self.show_answer: bool = True                       # Чек-бокс показать ответ
        self.work_row: list | None = None                   # Список с данными текущей строки рандомного слова
        self.choosen_excel_list: str | None = None          # Название выбранного листа в Excel
        self.choosen_db_theme: str | None = None            # Название выбранного раздела (листа, темы) в БД

        # data_window.py
        self.data_pagi_page: int = 1                        # Номер страницы пагинации в выводе данных
        self.search_key: str | None = None                  # Введённое в поиск
        self.search_data: list[list[int | str]] | None = None       # Список со списками отфильтрованных поиском данных

        # stat_window.py
        self.stat_data: list[list[int | str]] | None = None         # Список со списками данных отчётов статистики
        self.filter_stat_settings: list[str | bool] | None = None   # Список с фильтрами в статистике

        # Для логики сортировки на странице статистики stat_window.py
        self.col_id_reverse: bool = True                            # Реверсивность id
        self.col_percent_reverse: bool = False                      # Реверсивность %
        self.col_test_type_reverse: bool = False                    # Реверсивность тип теста
        self.col_theme_reverse: bool = False                        # Реверсивность тема/лист Excel

        # Для нормального отображения фона и центрирования текста + масштабирования окна
        self.grid_rowconfigure(1, weight=1)             # Растягиваем первую строку во всю ширину (фон, текст, и пр.)
        self.grid_columnconfigure(0, weight=1)          # Растягиваем первый столбец во всю высоту

        self.choose_color_theme(self.current_color_style)           # Установка цветового стиля
        self.popup = Popup(self)                                    # Инициализация всплывающих окон

    def put_menu(self) -> None:
        """ Сборка главного меню при запуске окна"""
        self.main_menu = MainMenuBTN(self)

    def choose_color_theme(self, color_theme: str) -> None:
        """
        Выбор цветовой темы. Фиксирует выбранную пользователем цветовую тему в настройках,
        переопределяет параметры стиля в зависимости от новой темы, обновляет окно для отображения изменений.

        :param color_theme: str название цветовой темы
        """

        if self.db.engine:                                                  # Если это работа с БД:
            self.db.set_new_color_theme(color_theme)                        # Записать настройку в Settings БД

        self.current_color_style = color_theme                              # Запись новой темы в атрибуты приложения

        for style, params in styles.STYLES_INIT.items():                    # Установка всех заданных стилей

            if 'foreground' in params:                                      # Ставим цвет шрифта темы по флагу
                if params['foreground'] == styles.FLAG_SET_FG_STYLE_COLOR_MAIN:
                    params = {**params,
                              **{'foreground': styles.STYLE_COLORS[self.current_color_style]['foreground_main']}}

            if 'background' not in params:                                  # Если фон не задан явно, делаем прозрачным
                params = {**params, **{'background': styles.STYLE_COLORS[self.current_color_style]['background']}}

            elif params['background'] == styles.FLAG_SET_MENU_BTN_COLOR:    # Проверяем флаги настройки стилей
                params = {**params,
                          **{'background': styles.STYLE_COLORS[self.current_color_style]['menu_btn_color_main']}}

            elif params['background'] == styles.FLAG_SET_MENU_OTHER_BTNS_COLOR:
                params = {**params,
                          **{'background': styles.STYLE_COLORS[self.current_color_style]['menu_btn_color_others']}}

            self.style.configure(style=style, **params)                     # Устанавливаем новые значения стиля
        self.refresh()

    def choose_window(self, win_type: str) -> None:
        """
        Выбор рабочего окна в главном меню.

        :param win_type: str название окна приложения
        """

        method_name = settings.APP_WINDOWS[win_type]['app_func']    # Название метода для инициализации выбранного окна
        getattr(self, method_name)()                                # Инициализируем окно
        self.window = win_type                                      # Записываем название окна в переменную приложения

    def refresh(self, object=None, container=None, build_function: str = None, in_frame=None) -> None:
        """
        Обновление данных окна или переданного контейнера. При вызове без передачи аргументов обновляет окно
        полностью.

        :param object: виджет-окно, у которого запускается метод сборки контейнера после обновления
        :param container: контейнер, данные которого необходимо обновить
        :param build_function: str название метода, которым обновлённый контейнер пересобирается
        :param in_frame: родительский контейнер для собираемого контейнера, если сборка происходит не в self виджета
        """
        widget = container if container else self           # По умолчанию работает с главным окном приложения

        all_frames = [f for f in widget.children]
        for f_name in all_frames:
            widget.nametowidget(f_name).destroy()           # Снос контейнера со старыми данными

        if widget == self:                                  # Пересборка контейнера/окна с новыми данными
            self.put_menu()
            self.choose_window(self.window)
        else:
            if in_frame:
                getattr(object, build_function)(in_frame)
                return
            getattr(object, build_function)()

    def setup_en_ru_window(self):
        """ Инициализация окна для тестирования en -> ru: word """

        self.en_ru_window = EnRuWindow(self)
        self.en_ru_window.grid(row=1, column=0, sticky='nswe')

    def setup_en_ru_audio_window(self):
        """ Инициализация окна для аудио тестирования en -> ru: audio """

        self.en_ru_audio_window = EnRuAudioWindow(self)
        self.en_ru_audio_window.grid(row=1, column=0, sticky='nswe')

    def setup_ru_en_window(self):
        """ Инициализация окна для вывода ru-en данных """

        self.ru_en_window = RuEnWindow(self)
        self.ru_en_window.grid(row=1, column=0, sticky='nswe')

    def setup_stat_window(self):
        """ Инициализация окна со статистикой """

        self.stat_window = StatWindow(self)
        self.stat_window.grid(row=1, column=0, sticky='nswe')

    def setup_data_window(self):
        """ Инициализация окна для просмотра и работы с данными """

        self.test_window = DataWindow(self)
        self.test_window.grid(row=1, column=0, sticky='nswe')


if __name__ == '__main__':
    app = App()
    app.mainloop()

"""
Всплывающие подсказки при наведении на виджет.
"""
import tkinter as tk


class TooltipHiding:
    """ Всплывающие текстовые подсказки с автоисчезновением через заданное время """

    def __init__(self, widget, text: str, event, delay: int = 1000):
        """
        Инициализация всплывающей подсказки

        :param widget: привязанный tkinter объект (Label, Button и т.д.)
        :param text: str текст подсказки
        :param event: событие tkinter объекта, которое инициализирует подсказку (для получения координат)
        :param delay: int задержка времени в миллисекундах, через которую скроется подсказка (1000 = 1 сек)
        """
        self.widget = widget                                        # Забираем переданные переменные
        self.text = text
        self.delay = delay

        # Создаём подсказку и размещаем её
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_attributes("-topmost", 1)
        self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root - 10}")
        label = tk.Label(self.tooltip, text=self.text, background="white", borderwidth=0)
        label.pack()

        self.widget.after(self.delay, self.hide_tooltip)            # Настраиваем скрытие подсказки

        # Настраиваем привязку событий реагирования
        self.widget.bind('<Leave>', self.hide_tooltip)              # Исчезает при отводе курсора с виджета
        self.widget.bind('<Button-1>', self.hide_tooltip)           # Исчезает при клике на виджет

    def hide_tooltip(self, event=None):
        """ Скрытие подсказки """
        if self.tooltip:
            self.tooltip.destroy()


class TooltipCursorOnHover:
    """ Класс для генерации подсказок во всплывающем окне + изменения курсора при наведении мыши.
     В объекте класса уже будет инициализирована привязка к событиям Enter и Leave"""

    def __init__(self, widget, text: str, x: int = None, y: int = None, hand_cursor: bool = False):
        """
        :param widget: объект, к которому будет привязана подсказка и события
        :param text: текст подсказки
        :param x: координата x для размещения
        :param y: координата y для размещения
        :param hand_cursor: изменение курсора при наведении. True для изменения на hand
        """
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.x = x
        self.y = y
        self.cursor = hand_cursor

        self.widget.bind("<Enter>", self.show_tooltip)                  # Привязываем событие на наведение мыши
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Button-1>", self.hide_tooltip)               # Закрытие при клике на widget
        self.widget.bind("<FocusOut>", self.hide_tooltip)               # Закрытие при потере фокуса виджетом

    def show_tooltip(self, event=None):
        """ Показать подсказку"""

        if self.cursor:                                                 # Настройка курсора
            self.widget.config(cursor="hand2")

        if self.x is None or self.y is None:            # Если координаты не переданы, то вычисляем их на основе события
            x = event.x_root
            y = event.y_root
        else:
            x = self.x
            y = self.y

        self.tooltip = tk.Toplevel(self.widget)                         # Создаем новое окно для подсказки
        self.tooltip.wm_overrideredirect(True)                          # Окно без рамки
        self.tooltip.wm_attributes("-topmost", 1)                       # Окно поверх всех окон

        tooltip_width = 200  # Ширина подсказки
        tooltip_height = 50  # Высота подсказки
        self.tooltip.wm_geometry(f"+{x + tooltip_width + 10}+{y - tooltip_height // 2}")    # Позиционируем подсказку

        label = tk.Label(self.tooltip, text=self.text, background="white", borderwidth=0)   # Создаем метку с подсказкой
        label.pack()
        self.tooltip.bind("<Button-1>", self.hide_tooltip)              # Скрытие подсказки при клике на саму подсказку

    def hide_tooltip(self, event=None):
        """ Скрыть подсказку """

        if self.tooltip:                                                # Закрываем окно подсказки
            self.tooltip.destroy()
            self.tooltip = None

        if self.cursor:                                                 # Возвращаем стандартный курсор
            self.widget.config(cursor="arrow")

import tkinter as tk


class HoverButton(tk.Button):
    """
    Кастомизация для кнопок пагинации.
    Изменение фона и курсора при наведении + дефолтные параметры (нет границы + отступ y)
    """
    def __init__(self, master=None, **kwargs):

        self.hlght: str = kwargs.pop('select_colour', 'white')              # Цвет подсветки при select
        self.hover_colour: str = kwargs.pop('hover_colour', 'white')        # Цвет подсветки при hover on
        self.crnt: int = kwargs.pop('crnt', None)                           # Номер текущей страницы пагинации

        if 'bd' not in kwargs:
            kwargs['bd'] = 0
        if 'pady' not in kwargs:
            kwargs['pady'] = 0

        tk.Button.__init__(self, master, **kwargs)                          # Инициализируем как кнопку

        self.default_bg = self['bg']                                        # Сохраняем изначальный фон кнопки
        self.default_fg = self['fg']                                        # Сохраняем изначальный цвет текста кнопки

        if self.cget('text') == str(self.crnt):                     # Выделяем подсветкой текущую страницу пагинации
            self.config(bg=self.hlght)
            self.config(fg='white')

        else:                                                               # Привязываем события наведения мыши
            self.bind('<Enter>', self.on_enter)
            self.bind('<Leave>', self.on_leave)

    def on_enter(self, event):
        """ Настройка при наведении мыши """
        self.config(bg=self.hover_colour, cursor='hand2')

    def on_leave(self, event):
        """ Настройка при отведении мыши """
        self.config(bg=self.default_bg, cursor='arrow')

import tkinter as tk
from tkinter import ttk

from typing import Union

from Utils.custom_widgets.tooltips import TooltipHiding


class HighlightableLabel(ttk.Label):
    """ Кастомизированные лейблы с возможностью выделения текста, вызова контекстного меню, копирования,
    привязки текстовой подсказки """

    def __init__(self, master: tk.Frame = None, window: Union[tk.Frame, tk.Widget] = None, is_tip: bool = False,
                 tip_text: str = 'Скопировано!', **kwargs):
        """
        Инициализация лейбла

        Важно! В window (основной фрейм окна) обязательно должно быть задано:
        self.current_selected_label = None -  Атрибут для отслеживания выделенного лейбла

        label = HighlightableLabel(parent_container, text="Текст 3", font=("Arial", 14), style='Cell.TLabel',
        window=self, is_tip=True, tip_text='Я сделаль!')


        :param master: родительский виджет tkinter.Frame
        :param window: основное окна страницы приложения, tkinter.Frame. Для сброса фокуса по клику вне виджета
        :param is_tip: True - для отображения временной подсказки при двойном клике, False - без подсказки
        :param tip_text: str текст подсказки
        :param kwargs: параметры для Label
        """
        super().__init__(master, **kwargs)          # Конструктор родительского класса Label
        self.selected = False                       # По умолчанию виджет не выделен
        self.is_tip = is_tip
        self.tip_text = tip_text
        self.bg = self.cget('background')           # Изначальный фон (для возврата после отмены выделения)

        # Привязка событий
        self.bind("<Double-1>", self.on_double_click)               # Двойной клик для выделения/отмены
        self.bind("<Button-1>", self.on_single_click)               # Одинарный клик для отмены выделения
        self.bind('<Button-3>', self.on_right_button_click)         # Контекстное меню
        if window:
            window.bind_all("<Button-1>", self.on_window_click)     # Клик по общему окну для отмены выделения
        self.window = window

    def on_double_click(self, event) -> None:
        """
        Обработчик двойного клика.
        Цветовое выделение выбранного виджета + копирование текста в буфер обмена + подсказка (если есть) + сброс
        предыдущих select
        """
        if self.selected:                                   # Если элемент уже был выбран, снимаем выделение
            self.deselect()

        else:                                               # Снимаем выделение с предыдущего выделенного элемента окна
            if hasattr(self.master, 'current_selected_label') and self.master.current_selected_label:
                self.master.current_selected_label.deselect()
            self.selected = True                            # Устанавливаем текущий выбранный элемент
            self.master.current_selected_label = self

            self.config(background='#157bd4')               # Меняем визуал виджета
            self.config(foreground='white')

            text = self.cget('text')                        # Забираем текст из виджета
            self.master.clipboard_clear()
            self.master.clipboard_append(text)              # И копируем его в буфер обмена

            if self.is_tip:                         # Вызываем подсказку с переданным текстом, если флаг подсказки True
                self.tip = TooltipHiding(self, text=self.tip_text, event=event)

    def on_right_button_click(self, event) -> None:
        """ Обработчик клика правой кнопки мыши. Вызов контекстного меню для копирования. """

        if self.selected:                                   # только если объект выделен!
            context_menu = tk.Menu(self, tearoff=0)
            context_menu.add_command(label='Скопировать', command=lambda event=event: self.copy_in_memory(event=event))
            context_menu.post(event.x_root, event.y_root)

    def on_single_click(self, event):
        """Обработчик клика по самому лейблу. Снятие выделения с объекта или ранее выделенных объектов"""

        self.deselect()
        if hasattr(self.master, 'current_selected_label') and self.master.current_selected_label:
            self.master.current_selected_label.deselect()       # Снимаем выделение с предыдущего элемента (если есть)

    def on_window_click(self, event):
        """ Обработчик клика вне лейбла для снятия выделения с объекта. """

        if hasattr(self.master, 'current_selected_label') and self.master.current_selected_label:

            # Если клик был вне любого лейбла, сбрасываем выделение
            if event.widget not in self.master.winfo_children():
                self.master.current_selected_label.deselect()
                self.master.current_selected_label = None

    def copy_in_memory(self, event):
        """ Копирование информации с лейбла в буфер обмена + сброс предыдущей информации там. """

        self.master.clipboard_clear()
        self.master.clipboard_append(self.cget('text'))
        TooltipHiding(self, text='Скопировано!', event=event)

    def deselect(self):
        """ Метод для снятия выделения с лейбла. Возврат изначального фона и цвета шрифта. """

        self.selected = False
        self.config(background=self.bg)
        self.config(foreground='black')

import math
import tkinter as tk
from typing import Union


class Paginator:
    """ Настройка и управление пагинацией """

    def __init__(self, widget: Union[tk.Frame, tk.Widget], array: list, current_page: int, per_page: int = 50):

        self.widget = widget            # Окно, в котором был вызван пагинатор (для доступа к родительским атрибутам)
        self.data = array               # Массив с данными, все записи к отображению
        self.per_page = per_page        # Записей на странице, шт

        self.current_page_number = current_page                         # Текущая страница пагинации
        self.pages_total = self.count_pages_total()

    def count_pages_total(self) -> int:
        """ Расчёт, сколько всего получится страниц в переданном массиве данных """

        len(self.data) / self.per_page
        return math.ceil(len(self.data) / self.per_page)

    def get_data_slice(self) -> list:
        """
        Получение списка записей для отображения на конкретной выбранной странице.

        :return: list срез массива данных для выбранного номера страницы пагинации.
        """
        first_el = (self.current_page_number - 1) * self.per_page
        last_el = first_el + self.per_page
        return self.data[first_el:last_el]

    def has_previous(self) -> bool:
        """ Проверка, существует ли страница с меньшим номером. True если да. """

        if self.current_page_number > 1:
            return True
        return False

    def has_next(self) -> bool:
        """ Проверка, существует ли следующая страница. True если да. """

        if self.current_page_number < self.pages_total:
            return True
        return False

    def _get_max_page2_number(self) -> int:
        """ Определяет максимально возможное значение страницы 2 в ряду пагинации"""
        return self.pages_total - 1

    def get_pages_1_2_3_numbers(self) -> tuple[int, int, int]:
        """
        Определяет номера отображаемых страниц в ряду пагинации

        :return: кортеж с int номерами трех отображаемых страниц
        """
        pg1, pg2, pg3 = 1, 1, 1

        if self.pages_total > 1:
            if self.current_page_number <= self._get_max_page2_number():
                pg2: int = self.current_page_number if self.current_page_number > 1 else 2

            elif self.current_page_number == 2 and self.pages_total == 2:
                pg2: int = self.current_page_number

            else:
                pg2: int = self.current_page_number - 1

            pg1: int = pg2 - 1
            pg3: int = pg2 + 1

        return pg1, pg2, pg3

    def go_to_page_number(self, page_number: int) -> None:
        """
        Перейти к странице с указанным номером.

        :param page_number: int номер страницы для перехода.
        """
        setattr(self.widget.parent, 'data_pagi_page', page_number)
        self.widget.parent.refresh()

    def go_to_first_page(self) -> None:
        """ Перейти к первой странице. """
        self.go_to_page_number(1)

    def go_to_previous_page(self) -> None:
        """ Перейти к предыдущей странице. """
        self.go_to_page_number(self.current_page_number - 1)

    def go_to_next_page(self):
        """ Перейти к следующей странице. """
        self.go_to_page_number(self.current_page_number + 1)

    def go_to_last_page(self):
        """ Перейти к последней странице. """
        self.go_to_page_number(self.pages_total)

"""
Управление синтезом речи для озвучки.
"""
import pyttsx3
import threading
import tkinter as tk


class SpeechSynthesis:
    """ Класс для действий с синтезом речи """

    def __init__(self):
        self.engine = pyttsx3.init()            # Инициализация движка

        self.voices_keys = {                    # Соответствия id голосов озвучки
            'female': 1, 'male': 2
        }

        # Дефолтные настройки
        self.speech_voice = 'male'              # Голос
        self.speech_volume = 100                # Громкость
        self.speech_rate = 120                  # Скорость речи

        self.engine.setProperty('voice', self.engine.getProperty('voices')[self.voices_keys[self.speech_voice]].id)
        self.engine.setProperty('rate', self.speech_rate)

    def set_volume(self, val: str, value_label: tk.Label) -> None:
        """
        Функция изменяет параметр громкости в движке и запускает обновление отображения параметра в лейбле в настройках.

        :param val: str значение, полученное из Scale бегунка
        :param value_label: Лейбл, отображающий актуальное значение параметра громкости речи
        """

        volume = float(val) / 100                       # Преобразуем значение с бегунка в диапазон от 0 до 1
        val = int(round(float(val), 0))                 # Преобразуем значение к int для отображения

        self.engine.setProperty('volume', volume)       # Устанавливаем громкость
        self.speech_volume = val

        self.update_value(val, value_label)             # Обновление текста в лейбле на значение переменной

    def set_speed(self, val: str, value_label: tk.Label) -> None:
        """
        Функция изменяет параметр скорости речи в движке и запускает обновление отображения параметра в лейбле
        в настройках.

        :param val: str значение, полученное из Scale бегунка
        :param value_label: Лейбл, отображающий актуальное значение параметра скорости речи
        """
        rate = 0 + float(val)                           # Преобразуем значение с бегунка в диапазон от 0 до 200
        val = int(round(float(val), 0))                 # Преобразуем значение к int для отображения

        self.engine.setProperty('rate', rate)           # Устанавливаем скорость
        self.speech_rate = val

        self.update_value(val, value_label)             # Обновление текста в лейбле на значение переменной

    def update_value(self, val: int, label: tk.Label) -> None:
        """
        Обновление текста в лейбле на значение из переменной

        :param val: int значение для отображения актуальных данных в лейбле
        :param label: лейбл с этим значением
        """
        label.config(text=val)                          # Обновляем текст метки с текущим значением

    def set_voice(self, var: str) -> None:
        """
        Функция для установки выбранного пользователем голоса в настройках

        :param var: str значение из RadioButton
        """
        voices = self.engine.getProperty('voices')

        self.engine.setProperty('voice', voices[self.voices_keys[var]].id)          # Установка голоса
        self.speech_voice = var

    def _say_out_thread(self, data: str) -> None:
        """
        Запуск произношения текста (для использования в отдельном потоке).

        :param data: str к озвучиванию
        """
        self.engine.say(data)
        self.engine.runAndWait()

    def say_out(self, data: str) -> None:
        """
        Запуск произношения переданного текста в отдельном потоке, чтобы не блокировать основной поток.

        :param data: str к озвучиванию
        """

        # Создаём новый поток с функцией озвучки и запускаем его
        speech_thread = threading.Thread(target=self._say_out_thread, args=(data, ))
        speech_thread.start()

    def say_out_partial(self, data_list: list, current_say: None | str, index_context: int) -> tuple[str, int]:
        """
        Функция для озвучивания примеров по очереди.
        Делит строку на список примеров и озвучивает один из них на основании расчета индекса. По завершению
        озвученных элементов, возвращается к первому, и так далее, по кругу.

        :param data_list: список с данными строки в формате [4, 'word', 'transcription', 'translate', 'context']
        :param current_say: ранее озвучивавшееся слово из атрибута вызывающего класса.
        :param index_context: расчетный индекс примера к озвучиванию
        :return: кортеж с проговариваемым словом и индексом следующего примера; для корректной перезаписи в атрибуты
                вызывающего класса
        """

        context_list = data_list[4].split('\n')           # Разбиваем строку контекста на отдельные примеры
        context_list = [i.strip() for i in context_list if i != '']

        if current_say != data_list[1]:                     # При первом проговаривании записываем слово
            data = context_list[0]
            current_say = data_list[1]
            index_context = 1
        else:                                               # Если не первое проговаривание, озвучиваем следующий пример
            try:
                data = context_list[index_context]
                index_context += 1
            except IndexError:                              # Если примеры закончились, возвращаемся к первому
                data = context_list[0]
                index_context = 1

        self.say_out(data)                                  # Озвучка выбранного примера
        return current_say, index_context                   # Возвращаем для перезаписи в странице вызова

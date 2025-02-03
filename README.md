# <span style="color: darkcyan">Приложение-помощник в изучении английского языка.</span>
___
## Оглавление

[Описание](#Описание)

[Функции](#Функции)

[Установка](#Установка)

[Использование](#Использование)

[Содержимое репозитория](#Содержимое-репозитория)

[Использованные библиотеки](#Использованные-библиотеки)

[Связь](#Связь)

___
## Описание

**English Vocabulary Learning App** — это приложение на Python, помогающее в изучении
английского языка. 

Ведите конспект актуального именно для Вас вокабуляра, прослушивайте 
произношение - изолированно и в различных примерах, используйте различные
методики для закрепления и проверки знаний, просматривайте статистику
результатов.

В общем - Ваш полноценный помощник в интервальном повторении✨🔥.
___

## Функции

- 📖 **Конспект изученных слов/фраз**:

Создавайте тематические разделы и добавляйте в них новые слова/фразы к
изучению, фиксируя актуальный вариант перевода и примеры использования - 
это позволит работать с именно актуальным вокабуляром по нужным темам.
Для удобства в приложении сразу содержатся ссылки на _Reverso Context_ и 
_Google Translator_. 

Доступен поиск, фильтрация по темам, редактирование и удаление записей.

- 🗂️ **Выбор типа хранения данных**:

Используйте удобный для Вас формат сохранения данных - приложение работает с
.db и Excel файлами - на выбор. 

- 🔊 **Аудирование**:

Прослушивайте изученное (включая примеры использования) через синтезатор речи
для запоминания на слух и уточнения транскрипции. 

Доступны настройки речи, 
включая выбор скорости воспроизведения и голоса.

- 🎓 **Тестирование**:

Проверяйте знания изученных слов с использованием различных видов тестирования.

- _Доступно три вида тестов_:
  - Перевод с английского на русский по написанию слова/фразы;
  - Перевод с русского на английский по описанию перевода слова/фразы и 
переводу примеров;
  - Перевод с английского на русский по аудио произношения слова/фразы.


- 📊 **Просмотр статистики прохождения тестирований**:

Все попытки прохождения тестов фиксируются, по завершению нажмите "Создать
запись" - для создания нового отчёта о прохождении для статистики.

Просматривайте отчёты и их детализацию, отслеживайте свой прогресс в прохождении
тестов для корректировки программы изучения.

Доступна фильтрация и сортировка отчётов по различным критериям.
___

## Установка

Для установки приложения выполните следующие шаги:

1. **Клонирование репозитория**:

```bash
git clone https://github.com/MurtazinaAlina/english_vocabulary_learning_app.git
cd english_vocabulary_learning_app
```
2. **Создание виртуального окружения** (опционально):

```bash
python3 -m venv venv
source venv/bin/activate          # Для Linux/Mac
venv\Scripts\activate             # Для Windows
```
3. **Установка зависимостей**:

```bash
pip install -r requirements.txt
```
___
## Использование

Перед запуском рекомендуется просмотреть и, при необходимости, скорректировать
данные в файле `settings.py`. Действие не является обязательным.

**Чтобы запустить приложение через терминал, выполните**:

```bash
python main.py
```

**Для более удобного пользовательского запуска воспользуйтесь скриптами**
(для Windows):

1. Через проводник найдите в проекте скрипт `run_script.vbs`.
2. Создайте для скрипта ярлык.
3. По желанию замените иконку созданного ярлыка на `images/app_icon/folder.ico`.
4. Разместите ярлык в удобном для Вас месте на компьютере и запускайте
приложение двойным кликом по нему.

**Создание базы с данными**:

После запуска создайте свою базу для данных прямо из запущенного приложения:
1. Строка с главным меню > ФАЙЛ.
2. Выберите пункт 'Создать новую книгу Excel со структурой базы' **ИЛИ** 
'Создать новую БД со структурой базы'
3. В открывшемся диалоговом окне выберите папку сохранения и имя файла.
4. При необходимости осуществите импорт данных из Excel в `.db`- файл.

___
## Содержимое репозитория

- `main.py`: Основной файл приложения.
- `requirements.txt`: Зависимости приложения.
- `run_script.bat`: Основной скрипт для запуска приложения через cmd.
- `run_script.vbs`: Скрипт-обёртка для запуска приложения без открытия
cmd-терминала.
- `settings.py`: Файл с основными настройками приложения. Рекомендуется
просмотреть и по необходимости внести коррективы.
- `styles.py`: Файл с настройками стилей.


- `app_windows/`: Папка с конструкторами основных окон приложения
    - `data_window.py`: Окно с отображением всех записей выбранного 
листа/темы, либо всех записей - для БД.
    - `popup.py`: Файл с генерацией всплывающих окон и их обработчиков.
    - `stat_window.py`: Окно для отображения статистики прохождения тестирований.
    - `en_ru_window.py`: Окно тестирования перевода с английского на
русский по написанию слова/фразы.
    - `ru_en_window.py`: Окно тестирования перевода с русского на
английский по описанию слова/фразы и переведённым примерам.
    - `en_ru_audio_window.py`: Окно тестирования перевода с английского на
русский по аудио транскрипции слова/фразы.
  

- `images/`: Папка с файлами иконок и изображений для использования в приложении.
  - `app_icon/`: Файл `.ico` для присвоения в иконку ссылки на приложение.
  - `.png`- файлы для отображения в иконках/кнопках.


- `Utils/`: Папка с различными вспомогательными классами, функциями и утилитами.
    
    - `mixins/`: Папка с миксинами для наследования в основной родительский 
    класс приложения App.
      - `common_widgets_n_containers.py`: Виджеты и контейнеры с виджетами, 
        общие для разных окон приложения.
      - `common_handlers.py`: Общие обработчики `commands=`.
      - `common_functions.py`: Общие функции.
      - `mixin_events.py`: Общие события.
      - `mixin_excel.py`: Класс для взаимодействия с Excel.
      
    - `db/`: Папка для работы с БД SQL.
      - `database.py`: Класс для взаимодействия с БД.
      - `models.py`: Модели таблиц.
      - `filler_data.py`: Филлерные данные для заливки в базу при создании.
      
    - `custom_widgets/`: Кастомизированные виджеты tkinter.
      - `custom_label.py`: Кастомный Label.
      - `hover_btn_text.py`: Кастомные кнопки.
      - `main_menu.py`: Кастомное главное меню.
      - `tooltips.py`: Текстовые подсказки при наведении курсора. 
      
    - `auxiliary_tools.py`: Различные вспомогательные функции.
    - `navigation_word_history.py`: Класс для сохранения истории попыток
       тестирования и навигации вперёд-назад.
    - `paginator.py`: Класс для пагинации данных.
    - `speech_synthesis.py`: Класс для управления синтезом речи.
    - `translate-en_ru-1_9.argosmodel`: Модель переводчика для перевода
       примеров с английского языка на русский.
___
## Использованные библиотеки

Основные использованные библиотеки (полный список зависимостей смотри в файле
`requirements.txt`):

- **SQLAlchemy** (2.0.37): Библиотека для работы с базами данных.
- **openpyxl** (3.1.5): Библиотека для чтения и записи файлов Excel (xlsx).
- **pyttsx3** (2.98): Библиотека для синтеза речи.
- **argostranslate** (1.9.6): Инструмент для перевода на базе нейросетей.
- **pillow** (11.1.0): Библиотека для работы с изображениями.
- **regex** (2024.11.6): Расширенная библиотека для работы с регулярными 
выражениями.

___
## Связь

Если у вас есть вопросы или предложения, обращайтесь по адресу:
[ve4nayavesna@mail.ru](mailto:ve4nayavesna@mail.ru).

"""
Действия с БД.
"""
import datetime
import shutil
from tkinter import filedialog, messagebox as mbox
from sqlalchemy import create_engine, func, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, joinedload

from Utils.db.models import Base, SubjectSheet, WordPhrase, Context, Settings, TestTypes, TestAttempts, Report
from Utils.db.filler_data import subjects, words, examples, settings, test_types, test_attempts, reports


class Database:
    """ Класс для работы с базами данных """

    def __init__(self):
        self.engine = None
        self.Session = None
        self.db_path = None                                                 # Системный путь к файлу с базой

    def create_db(self) -> None:
        """ Создать и сохранить новую базу данных + подключиться к созданной базе """

        self.db_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite Database", "*.db")])

        if not self.db_path:
            return

        self.engine = create_engine(f'sqlite:///{self.db_path}')            # Создаём соединение с БД
        Base.metadata.create_all(self.engine)                               # Создаём таблицы
        self.Session = sessionmaker(bind=self.engine)                       # Создаём сессию

        # Заливка тестовых данных
        self.set_filler_data()

    def set_filler_data(self):
        """ Заливка тестовых данных """

        self.refresh_db_after_new_tables()

        # ЗАЛИВАЕМ ФИЛЛЕРНЫЕ ДАННЫЕ ДЛЯ ТЕСТ_ДРАЙВА
        with self.Session() as session:
            session.add_all(subjects)
            session.add_all(words)
            session.add_all(examples)
            session.add(settings)
            session.add_all(test_types)
            session.add_all(test_attempts)
            session.add_all(reports)
            session.commit()

    def refresh_db_after_new_tables(self) -> None:
        """ Обновление таблиц в базе. Функция добавляет НОВЫЕ созданные таблицы, не затрагивая старые"""
        Base.metadata.create_all(bind=self.engine)

    def connect_db(self) -> None:
        """ Подключиться к БД, выбрав файл с базой"""

        self.db_path = filedialog.askopenfilename(title='Выберите базу данных', filetypes=[("SQLite Database", "*.db")])

        if not self.db_path:
            return

        self.engine = create_engine(f'sqlite:///{self.db_path}')            # Создаём соединение с БД
        self.Session = sessionmaker(bind=self.engine)                       # Создаём сессию

    def disconnect_db(self) -> None:
        """ Отключиться от БД """

        self.engine = None
        self.Session = None
        self.db_path = None

    def save_db_as(self) -> None:
        """ Сохранить файл .db как. Вызывает диалоговое окно с выбором папки сохранения и запросом имени файла. """

        folder_selected = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder_selected:
            filename = filedialog.asksaveasfilename(                # Открываем диалог для ввода имени файла
                initialdir=folder_selected,
                title="Введите имя файла",
                defaultextension=".db",
                filetypes=(("SQL Files", "*.db"), ("All Files", "*.*"))
            )
            if filename:
                filename = filename.replace('/', '\\')              # Для корректной работы Windows

                try:
                    # Копируем файл базы данных в выбранную папку
                    shutil.copy2(self.db_path, filename)
                    mbox.showinfo('Сохранение', f"Файл сохранен как:\n{filename}")

                except Exception as e:
                    mbox.showerror('Ошибка', f"Не удалось сохранить файл: {e}")

    def get_list_all_themes(self) -> list[str]:
        """
        Получить список с str названиями всех разделов (тем)

        :return: список формата ['Тема 1', 'Тема 2', ... 'Тема про N']
        """
        with self.Session() as session:
            all_themes = session.query(SubjectSheet).all()
            all_themes = [theme.name for theme in all_themes]

        return all_themes

    def random_word_from_theme(self, theme: str | None) -> list[int | str]:
        """
        Получение списка с данными случайно выбранного слова из конкретного раздела или всей базы

        :param theme: str название выбранного пользователем раздела (листа с темой) или None
        :return: Список формата [ID_записи_int, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
        """
        with self.Session() as session:

            # Рандомизатор на уровне БД
            if theme:                                                   # Из конкретного раздела
                random_word = session.query(WordPhrase).join(SubjectSheet).filter(SubjectSheet.name == theme).\
                    order_by(func.random()).first()
            else:                                                       # Если тема не выбрана - из всей базы
                random_word = session.query(WordPhrase).options(joinedload(WordPhrase.subject)).order_by(
                    func.random()).first()

            if not random_word:                                         # Обработка пустого раздела
                mbox.showinfo('', 'Выбран пустой раздел')
                return ['' for i in range(6)]                           # Заглушка для отображения

            # Редактируем для вывода данные примеров контекста
            context = '\n\n'.join([i.example for i in random_word.context_examples])

            word_theme = random_word.subject.name

        return [random_word.id, random_word.word, random_word.transcription, random_word.translate, context, word_theme]

    def create_new_subject(self, new_theme_name: str) -> SubjectSheet:
        """
        Создание нового раздела (темы).

        :param new_theme_name: str название нового раздела
        :return: новый созданный ОБЪЕКТ класса SubjectSheet
        """

        new_subject = SubjectSheet(name=new_theme_name)
        with self.Session() as session:
            session.add(new_subject)
            session.commit()

        return new_subject

    def create_new_word(self, choosen_sheet_cmbbx: str, word: str, transcript: str, translate: str,
                        context: str) -> bool:
        """
        Создать новую запись со словом по выбранной теме + заполнить примеры из context по данным из форм ввода

        :param choosen_sheet_cmbbx: str название выбранной темы
        :param word: str слово/фраза
        :param transcript: str транскрипция
        :param translate: str перевод
        :param context: str примеры употребления
        :return: True при успешном создании, False при ошибке
        """
        session = self.Session()

        try:
            # Создаём в рамках транзакции, чтобы при ошибках сделать полный откат
            session.begin()

            theme = session.query(SubjectSheet).filter(SubjectSheet.name == choosen_sheet_cmbbx).first()
            new_word = WordPhrase(word=word, transcription=transcript, translate=translate, subject=theme)
            session.add(new_word)

            context = context.split('\n')
            context = [example.strip() for example in context if example != '']
            for example in context:
                example = Context(example=example, word=new_word)
                session.add(example)

            session.commit()
            is_created = True

        except SQLAlchemyError as error:
            session.rollback()
            is_created = False
            mbox.showerror('Ошибка!', f'Ошибка при создании: {error}')

        finally:
            session.close()

        return is_created

    def get_all_words_from_subject(self, theme: str | None = None) -> list[list[int | str]]:
        """
        Получить данные всех слов, связанных с выбранным разделом.

        :param theme: str название выбранного раздела (листа) или None - для отсутствия фильтра по теме
        :return: список со списками данных строк формата:
                [[5, 'sixfold (adv, adj)', 'fōld', 'шестикратный, в шесть раз.', 'имя_темы'], [...] ...]
        """
        with self.Session() as session:
            result_list = []

            # Забираем данные всех слов + названия их тем
            all_data = session.query(WordPhrase,
                                     SubjectSheet.name.label('subj_name')
                                     ).join(SubjectSheet).order_by(WordPhrase.id.desc())

            # Если тема задана, применяем фильтрацию, если нет - оставляем все данные
            if theme:
                all_data = all_data.filter(SubjectSheet.name == theme).all()
            elif not theme:
                all_data = all_data.all()

            # Редактируем для вывода данные примеров контекста и складываем всё в результирующий лист
            for word, title in all_data:
                context = '\n'.join([i.example for i in word.context_examples])

                data = [word.id, word.word, word.transcription, word.translate, context, title]
                result_list.append(data)
        return result_list

    def get_word_by_id(self, word_id: int) -> list[int | str] | None:
        """
        Получить информацию о записи WordPhrase по id

        :param word_id: int id слова/фразы
        :return: Список формата [ID_записи_int, 'word', 'transcript', 'translate', 'Here is context', 'sheet name']
                None - при отсутствии записи
        """
        with self.Session() as session:
            word_updated = session.query(WordPhrase).options(joinedload(WordPhrase.subject)).get(word_id)

            if word_updated:
                word_theme = word_updated.subject.name

                # Редактируем для вывода данные примеров контекста
                context = '\n\n'.join([i.example for i in word_updated.context_examples])

                return [word_updated.id, word_updated.word, word_updated.transcription, word_updated.translate, context,
                        word_theme]
            return None

    def delete_subject(self, theme: str) -> bool:
        """
        Удаление темы (листа) по названию

        :param theme: str название темы к удалению
        :return: True при успешном удалении, False при ошибке/отмене операции
        """
        session = self.Session()

        try:
            # Удаляем в рамках транзакции для полного отката действия при возникновении ошибок
            session.begin()
            to_delete = session.query(SubjectSheet).filter(SubjectSheet.name == theme).first()
            session.delete(to_delete)
            session.commit()
            is_deleted = True

        except SQLAlchemyError as error:
            session.rollback()
            is_deleted = False
            mbox.showerror('Ошибка!', f'Ошибка при выполнении запроса: {error}')

        finally:
            session.close()

        return is_deleted

    def delete_word(self, word_id: int) -> bool:
        """
        Удалить запись со словом из WordPhrase по id

        :param word_id: int id записи слова в таблице WordPhrase
        :return: True при успешном удалении, False при ошибке/отмене операции
        """
        session = self.Session()

        try:
            session.begin()

            to_delete = session.query(WordPhrase).filter_by(id=word_id).first()
            session.delete(to_delete)
            session.commit()
            is_deleted = True

        except SQLAlchemyError as error:
            session.rollback()
            is_deleted = False
            mbox.showerror('Ошибка!', f'Ошибка при выполнении запроса: {error}')

        finally:
            session.close()

        return is_deleted

    def update_word(self, word_id: int, word: str, transcript: str, translate: str, context: str,
                    choosen_sheet_cmbbx:str) -> bool:
        """
        Редактирование записи слова в WordPhrase по данным из формы ввода
        (11, 'word', 'transcript', 'translate', 'context', 'choosen_sheet_cmbbx')

        :param word_id: int id записи слова в таблице WordPhrase
        :param word: str слово/фразы
        :param transcript: str транскрипция
        :param translate: str перевод
        :param context: str примеры использования в контексте
        :param choosen_sheet_cmbbx: str название выбранной темы/листа
        :return: True при успешном изменении, False при ошибке/отмене операции
        """
        session = self.Session()
        try:
            # Обновляем в рамках транзакции для полной отмены при возникновении ошибок
            word_to_update = session.query(WordPhrase).get(word_id)
            theme = session.query(SubjectSheet).filter_by(name=choosen_sheet_cmbbx).first()
            if word_to_update:
                word_to_update.word = word
                word_to_update.transcription = transcript
                word_to_update.translate = translate
                word_to_update.subject = theme

                # Перезаписываем контекст
                for example in word_to_update.context_examples:
                    session.delete(example)

                context = context.split('\n')
                context = [example.strip() for example in context if example != '']
                for example in context:
                    example = Context(example=example, word=word_to_update)
                    session.add(example)

            session.commit()
            is_updated = True

        except SQLAlchemyError as error:
            session.rollback()
            is_updated = False
            mbox.showerror('Ошибка!', f'Ошибка при выполнении запроса: {error}')

        finally:
            session.close()

        return is_updated

    def get_app_settings(self) -> Settings:
        """
        Забрать всю информацию о пользовательских настройках приложения

        :return: ОБЪЕКТ Settings с доступом ко всем атрибутам
        """
        with self.Session() as session:
            result = session.query(Settings).first()
        return result

    def set_new_color_theme(self, color_theme: str) -> None:
        """
        Записать в пользовательские настройки (таблицу Settings) новую выбранную цветовую тему

        :param color_theme: str обозначение цветовой темы к установке
        """
        with self.Session() as session:
            current_settings = session.query(Settings).first()          # Текущие настройки
            current_settings.color_theme = color_theme                  # Обновляем
            session.commit()

    def set_new_speech_settings(self, speech_volume: int, speech_rate: int, voice: str) -> None:
        """
        Записать в пользовательские настройки (таблицу Settings) новые данные голосовых настроек

        :param speech_volume: int значение бегунка громкости
        :param speech_rate: int значение бегунка скорости
        :param voice: str переменная выбора голоса
        """
        with self.Session() as session:
            current_settings = session.query(Settings).first()          # Текущие настройки
            current_settings.speech_volume = speech_volume              # Обновляем
            current_settings.speech_rate = speech_rate
            current_settings.speech_voice = voice
            session.commit()

    def create_test_attempt(self, word_id: int, result: str, test_type: str) -> None:
        """
        Записать в БД попытку тестирования слова

        :param word_id: int id слова/фразы
        :param result: str результат прохождения
        :param test_type: str тип теста
        """
        session = self.Session()
        try:
            session.begin()

            dt = datetime.datetime.now()
            test_type = session.query(TestTypes).filter_by(name=test_type).first()
            attempt = TestAttempts(timestamp=dt, test_type=test_type, word_id=word_id, result=result, report_id=None)
            session.add(attempt)
            session.commit()

        except SQLAlchemyError as error:
            session.rollback()
            mbox.showerror('Ошибка!', f'Ошибка при выполнении запроса: {error}')

        finally:
            session.close()

    def get_statistic_data_by_test_type(self, test_type: str) -> tuple[int, int,int]:
        """
        Получить из БД данные для отображения в статистике попыток
        (Все записи нужного типа теста, не привязанные к отчёту)

        :param test_type: str название типа тестирования
        :return: кортеж с числовыми значениями (right, wrong, attempts YES + NO)
        """
        with self.Session() as session:

            # Сначала получаем список записей отфильтрованный по условиям
            res = session.query(TestAttempts).join(TestTypes).filter(
                (TestAttempts.report_id == None) & (TestTypes.name == test_type))

            # Выполняем агрегацию по результатам
            counts = res.with_entities(
                func.count().filter(TestAttempts.result == 'YES').label('yes_count'),
                func.count().filter(TestAttempts.result == 'NO').label('no_count')
            ).one()

            return counts.yes_count, counts.no_count, counts.yes_count + counts.no_count

    def create_statistic_report(self, test_type: str) -> bool:
        """
        Создать новый отчёт статистики и присвоить его id попыткам, относящимся к нужному типу тестирования

        :param test_type: str название типа тестирования
        :return: True при успехе создания отчёта и присвоения попыткам его id, False при возникновении ошибок
        """
        session = self.Session()
        dt = datetime.datetime.now()

        try:
            session.begin()                                             # Делаем транзакцией

            # Забираем из базы все попытки + темы попыток
            atts = session.query(TestAttempts, SubjectSheet.name.label('att_theme')
                                 ).join(TestTypes).join(WordPhrase).join(SubjectSheet).filter(
                (TestAttempts.report_id == None) & (TestTypes.name == test_type)).all()

            # Определяем для отчёта название темы (если уникальная) и выборку слов (по теме или всего)
            used_themes = set([att.att_theme for att in atts])  # Множество всех тем в попытках
            if len(used_themes) == 1:
                theme_if_is = atts[0].att_theme
                sample_of_words = session.query(func.count(WordPhrase.id)).filter(
                    SubjectSheet.name == theme_if_is).join(SubjectSheet).scalar()
            else:
                theme_if_is = '-'
                sample_of_words = session.query(func.count(WordPhrase.id)).scalar()

            # Создаём новый отчёт
            new_report = Report(timestamp=dt, theme_if_is=theme_if_is, word_sampling=sample_of_words)
            session.add(new_report)
            session.flush()                         # Применяем flush для синхронизации с базой данных и получения ID

            # Присваиваем id отчёта попыткам нужного типа тестирования
            for attempt in atts:
                attempt[0].report_id = new_report.id

            session.commit()
            is_created = True

        except SQLAlchemyError as error:
            session.rollback()
            mbox.showerror('Ошибка!', f'Ошибка при выполнении запроса: {error}')
            is_created = False

        finally:
            session.close()

        return is_created

    def get_list_all_statistic_reports(self) -> list[list]:
        """
        Получить список с данными всех отчётов БД. Функция забирает данные отчётов из БД и приводит их к виду списка
        определенного формата для вывода.

        :return: Список со списками, в которых лежат данные каждого отчёта, формата:
                [[1, datetime.datetime(2025, 1, 21, 1, 37, 47), 3, 4, 75.0, '-', 2005, 'en -> ru: word'] ...]
        """
        result_list = []
        with self.Session() as session:

            # Забираем все отчёты + высчитываем данные для вывода, упорядочиваем
            all_reports = session.query(
                Report.id,
                Report.timestamp,
                Report.theme_if_is,
                Report.word_sampling,
                func.count(TestAttempts.id).filter(TestAttempts.result == 'YES').label('count_yes'),
                func.count(TestAttempts.id).filter(TestAttempts.result.in_(['YES', 'NO'])).label('count_yes_no'),
                TestTypes.name.label('test_type')
            ).select_from(Report).join(TestAttempts, TestAttempts.report_id == Report.id).join(TestTypes).\
                group_by(Report.id).order_by(Report.id.desc()).all()

            # Дополнительно форматируем данные
            for report in all_reports:
                percent = round((report.count_yes * 100/ report.count_yes_no), 1)
                dt = report.timestamp.replace(microsecond=0)

                # Формируем список с данными отчёта и добавляем его в итоговый список
                one_report_list = [report.id, dt, report.count_yes, report.count_yes_no, percent, report.theme_if_is,
                                   report.word_sampling, report.test_type]
                result_list.append(one_report_list)

            return result_list

    def get_list_filtered_statistic_reports(self, filter_list: list[str | bool],
                                            order_by: str | None = None, desc_order: bool = True) -> list[list]:
        """
        Получить список с данными отчётов (в формате списков для вывода) с учётом пользовательской фильтрации и
        сортировки.

        :param filter_list: Список с параметрами пользовательской фильтрации отчётов формата:
                            ['filter', '2025-01-15', '2025-01-21', True, 'en -> ru: word', True, '-']
        :param order_by: str название типа сортировки (если есть) или None
        :param desc_order: bool порядок сортировки

        :return: Отфильтрованный отсортированный список со списками, в которых лежат данные каждого отчёта, формата:
                [[1, datetime.datetime(2025, 1, 21, 1, 37, 47), 3, 4, 75.0, '-', 2005, 'en -> ru: word'] ...]
        """
        result_list = []
        with self.Session() as session:

            # Забираем все отчёты + высчитываем данные для вывода, упорядочиваем
            query = session.query(
                Report.id,
                Report.timestamp,
                Report.theme_if_is,
                Report.word_sampling,
                func.count(TestAttempts.id).filter(TestAttempts.result == 'YES').label('count_yes'),
                func.count(TestAttempts.id).filter(TestAttempts.result.in_(['YES', 'NO'])).label('count_yes_no'),
                TestTypes.name.label('test_type')
            ).select_from(Report).join(TestAttempts, TestAttempts.report_id == Report.id).join(TestTypes).\
                join(WordPhrase).join(SubjectSheet).group_by(Report.id)

            # Последовательно применяем к выборке пользовательские фильтры - при их указании
            if filter_list[3]:
                types_only = filter_list[4]                                 # Фильтр по типу тестирования
                query = query.filter(TestTypes.name == types_only)

            if filter_list[5]:                                              # Фильтр по темам
                themes_only = filter_list[6]
                query = query.filter(Report.theme_if_is == themes_only)

            if filter_list[0] != 'all':                                     # Фильтр по датам
                date_from = datetime.datetime.strptime(filter_list[1], '%Y-%m-%d')
                date_before = datetime.datetime.strptime(filter_list[2] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
                query = query.filter(Report.timestamp >= date_from, Report.timestamp <= date_before)

            # Настраиваем сортировку, если переданы параметры для неё
            if order_by == 'id':
                order = Report.id
            elif not order_by:
                order = Report.id
            elif order_by == 'theme':
                order = Report.theme_if_is
            elif order_by == 'type':
                order = TestAttempts.test_type_id

            if desc_order:
                query = query.order_by(desc(order))
            if not desc_order:
                query = query.order_by(asc(order))

            # Дополнительно форматируем данные
            for report in query:
                percent = round((report.count_yes * 100 / report.count_yes_no), 1)
                dt = report.timestamp.replace(microsecond=0)

                # Формируем список с данными отчёта и добавляем его в итоговый список
                one_report_list = [report.id, dt, report.count_yes, report.count_yes_no, percent, report.theme_if_is,
                                   report.word_sampling, report.test_type]
                result_list.append(one_report_list)

            return result_list

    def delete_statistic_report_by_id(self, report_id: int) -> bool:
        """
        Удалить из БД отчёт Report по id + все связанные попытки TestAttempts

        :param report_id: int id отчёта к удалению
        :return: True при успехе, False при возникновении любой ошибки и отмене действия
        """
        session = self.Session()
        try:
            # Делаем транзакцией для полного отката при ошибках
            session.begin()

            to_delete = session.query(Report).get(report_id)        # Находим отчёт по id
            if to_delete:
                session.delete(to_delete)                           # Удаляем. Каскадом должны удалиться попытки

            session.commit()
            is_deleted = True

        except SQLAlchemyError as error:
            session.rollback()                                      # При любой ошибке откат
            mbox.showerror('Ошибка!', f'При выполнении запроса произошла ошибка: {error}')
            is_deleted = False

        finally:
            session.close()

        return is_deleted

    def get_attempts_by_report_id(self, report_id: int) -> list[list[int | str]]:
        """
        Получить список с детализацией попыток по номеру отчёта

        :param report_id: id отчёта статистики
        :return: список списков, список всех попыток в отчёте с переданным id, формата:
                [[67, '2025-01-09 17:14:25', 'a supremacy', 'Верно', 39], [...], ... ],
        """
        with self.Session() as session:

            # Забираем все нужные данные о попытках, относящихся к отчёту с переданным id
            query = session.query(TestAttempts.id,
                                  TestAttempts.timestamp,
                                  WordPhrase.word,
                                  TestAttempts.result,
                                  Report.id).\
                select_from(TestAttempts).join(Report).join(WordPhrase).\
                filter(Report.id == report_id).all()

            # Форматируем данные для отображения и складываем в результирующий лист
            result_list = []
            for row in query:
                row = list(row)
                row[1] = datetime.datetime.strftime(row[1], '%Y-%m-%d %H:%M:%S')
                result_list.append(row)

            return result_list

    def is_new_word(self, word: str, transcript: str, translate:str) -> bool:
        """
        Определяет, является ли переданное слово новым или уже есть в базе с такими значениями.

        :param word: str слово/фраза
        :param transcript: str транскрипция
        :param translate: str перевод
        :return: True если переданное слово новое и не встречается в базе с таким текстом, транскрипцией и переводом
        """
        with self.Session() as session:
            result = session.query(WordPhrase).filter(WordPhrase.word == word,
                                                      WordPhrase.transcription == transcript,
                                                      WordPhrase.translate == translate).first()
            if result:
                return False                            # Если запись с такими значениями найдена, возвращаем False
            return True

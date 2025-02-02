from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

import styles

# Создаем базовый класс для моделей
Base = declarative_base()


class BaseModel(Base):
    """ Кастомизация базового класса с автоинкрементом id """
    __abstract__ = True                                             # Этот класс не будет использоваться напрямую в БД

    id = Column(Integer, primary_key=True, autoincrement=True)


class SubjectSheet(BaseModel):
    """ Тема (лист, раздел) """
    __tablename__ = 'subjects'

    name = Column(String, nullable=False, unique=True)

    word_phrases = relationship('WordPhrase', order_by='WordPhrase.id', back_populates='subject',
                                cascade='all, delete-orphan')       # Для удаления связанных слов

    def __repr__(self):
        return f"<SubjectSheet(id={self.id}, name={self.name})>"


class WordPhrase(BaseModel):
    """ Слово/фраза, запись со всеми данными """
    __tablename__ = 'word_phrases'

    word = Column(String, nullable=False)
    transcription = Column(String)
    translate = Column(String)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)

    # Отношения
    subject = relationship('SubjectSheet', back_populates='word_phrases')
    context_examples = relationship('Context', back_populates='word', cascade='all, delete-orphan')
    test_attempts = relationship('TestAttempts', back_populates='word', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<WordPhrase(id={self.id}, word={self.word}, transcription={self.transcription}, " \
               f"translate={self.translate}, subject_id={self.subject_id})>"


class Context(BaseModel):
    """ Примеры с использованием слов/фраз, контекст """
    __tablename__ = 'examples'

    example = Column(String, nullable=False)
    word_id = Column(Integer, ForeignKey(WordPhrase.id), nullable=False)

    word = relationship(WordPhrase, back_populates='context_examples')

    def __repr__(self):
        return f'<Context(id={self.id}, example={self.example}, word_id={self.word_id}, word={self.word.word})>'


class Settings(BaseModel):
    """ Основные пользовательские настройки приложения """
    __tablename__ = 'settings'

    color_theme = Column(String)            # Цветовая тема приложения
    speech_volume = Column(Integer)         # Громкость речи
    speech_rate = Column(Integer)           # Скорость речи
    speech_voice = Column(String)           # Выбор голоса воспроизведения

    # Ограничения значений настроек
    values = tuple(styles.STYLE_COLORS.keys())          # ('lav', 'l_orange_2', 'l_orange', 'emer', 'l_gr')
    __table_args__ = (CheckConstraint(f'color_theme IN {values} OR color_theme IS NULL', name='check_color_theme'),
                      CheckConstraint(f'speech_voice IN ("male", "female") OR speech_voice IS NULL',
                                      name='check_speech_voice'),
                      CheckConstraint(f'(speech_volume IS NULL OR (speech_volume >= 0 AND speech_volume <= 100))',
                                      name='check_speech_volume'),
                      CheckConstraint(f'(speech_rate IS NULL OR (speech_rate >= 0 AND speech_rate <= 200))',
                                      name='check_speech_rate'))


class TestTypes(BaseModel):
    """ Типы попыток тестирования """
    __tablename__ = 'test_types'

    name = Column(String, nullable=False, unique=True)

    test_attempts = relationship('TestAttempts', back_populates='test_type', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<id: {self.id}, name: {self.name}>'


class Report(BaseModel):
    """ Отчёт с попытками прохождения """
    __tablename__ = 'reports'

    timestamp = Column(DateTime, nullable=False)
    theme_if_is = Column(String, nullable=False)
    word_sampling = Column(Integer, nullable=False)

    test_attempts = relationship('TestAttempts', back_populates='report', cascade='all, delete-orphan')

    # Ограничения
    __table_args__ = (CheckConstraint('word_sampling > 0', name='check_word_sampling'), )

    def __repr__(self):
        return f'<id: {self.id}, timestamp: {self.timestamp}>'


class TestAttempts(BaseModel):
    """ Попытки прохождения тестирования """
    __tablename__ = 'test_attempts'

    timestamp = Column(DateTime, nullable=False)
    test_type_id = Column(Integer, ForeignKey(TestTypes.id), nullable=False)
    word_id = Column(Integer, ForeignKey(WordPhrase.id), nullable=False)
    result = Column(String, nullable=False)
    report_id = Column(Integer, ForeignKey(Report.id), nullable=True)

    # Отношения
    test_type = relationship(TestTypes, back_populates='test_attempts')
    word = relationship(WordPhrase, back_populates='test_attempts')
    report = relationship(Report, back_populates='test_attempts')

    # Ограничения
    __table_args__ = (CheckConstraint(f'result IN ("YES", "NO", "PASS")', name='check_result_value'), )

    def __repr__(self):
        return f'<id: {self.id}, timestamp: {self.timestamp}, test_type_id: {self.test_type_id}, ' \
               f'word_id: {self.word_id}, result: {self.result}, report_id: {self.report_id}>'

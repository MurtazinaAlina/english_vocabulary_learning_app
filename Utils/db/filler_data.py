"""
Тестовые данные для заполнения новой созданной БД.
"""
from Utils.db.models import SubjectSheet, WordPhrase, Context, Settings, TestTypes, TestAttempts, Report
from settings import TEST_TYPES
from datetime import datetime as dt


# Темы
subjects = [
    SubjectSheet(name='Theme 1'),
    SubjectSheet(name='Theme 2'),
    SubjectSheet(name='Theme 3'),
]

# Слова/фразы
words = [
    WordPhrase(word='to brim', transcription='-', translate='переполняться, наполняться до краёв', subject_id=1),
    WordPhrase(word='do me a solid', transcription='-', translate='Сделай мне одолжение', subject_id=1),
    WordPhrase(word='to hack down', transcription='hak', translate='истребить, вырубить \ взломать', subject_id=2),
    WordPhrase(word='do something for days', transcription='', translate='делать что-то днями', subject_id=2),
    WordPhrase(word='sixfold (adv, adj)', transcription='fōld', translate='шестикратный, в шесть раз.', subject_id=3)
]

# Примеры использования
examples = [
    Context(example='His emotions began to brim, overflowing with love for her.   ', word_id=1),
    Context(example='During the spell of heavy rain, the reservoir started to brim over dangerously.', word_id=1),
    Context(example='Could you do me a solid and help me move this weekend?  ', word_id=2),
    Context(example='Must I hack down a whole family tree of demons? ', word_id=3),
]

# Настройки - цветовая тема, синтез речи
settings = Settings(color_theme=None, speech_volume=None, speech_rate=None, speech_voice=None)

# Типы тестирования
test_types = [
    TestTypes(name=TEST_TYPES[0]),
    TestTypes(name=TEST_TYPES[1]),
    TestTypes(name=TEST_TYPES[2]),
]

# Тестовые попытки
test_attempts = [
    TestAttempts(timestamp=dt.now(), test_type_id=1, word_id=1, result='YES', report_id=None),
    TestAttempts(timestamp=dt.now(), test_type_id=1, word_id=2, result='YES', report_id=None),
    TestAttempts(timestamp=dt.now(), test_type_id=1, word_id=4, result='PASS', report_id=None),
    TestAttempts(timestamp=dt.now(), test_type_id=3, word_id=3, result='YES', report_id=None),
    TestAttempts(timestamp=dt(2025, 1, 5, 12, 00), test_type_id=1, word_id=1, result='YES', report_id=1),
    TestAttempts(timestamp=dt(2025, 1, 4, 2, 30), test_type_id=1, word_id=2, result='NO', report_id=1),
    TestAttempts(timestamp=dt(2024, 12, 24, 2, 30), test_type_id=3, word_id=1, result='YES', report_id=2),
    TestAttempts(timestamp=dt(2024, 12, 14, 2, 30), test_type_id=3, word_id=1, result='YES', report_id=3),
]

# Тестовые отчёты
reports = [
    Report(timestamp=dt(2025, 1, 5, 12, 30), theme_if_is='-', word_sampling=10),
    Report(timestamp=dt.now(), theme_if_is='Theme 1', word_sampling=2),
    Report(timestamp=dt.now(), theme_if_is='-', word_sampling=10),
]

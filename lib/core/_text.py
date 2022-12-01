import re
from textstat import flesch_reading_ease
NO_SPECIAL_CHARS = '[^A-Za-z0-9\s]+'


def remove_special_chars(text):
    return re.sub(NO_SPECIAL_CHARS, '', text)


def remove_unicode(text):
    return text.encode('ascii', 'ignore').decode('ascii')


def remove_newline(text):
    text = re.sub(' +', ' ', text.replace('\n', ' '))
    # Remove Tabs
    text = re.sub(' +', ' ', text.replace('\t', ' '))
    return text


def clean_text(text):
    text = remove_unicode(text)
    text = remove_newline(text)
    text = remove_special_chars(text)
    text = text.lower()
    return text.strip()


def get_reading_score(text):
    score = flesch_reading_ease(text)
    return score
